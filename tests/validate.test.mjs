// Schema validation and quarantine behaviour.  node --test tests/validate.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, existsSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { createValidators, validateFile, allPublicationFiles, main } from "../scripts/validate-content.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const fixtures = join(root, "tests", "fixtures");
const validators = createValidators();
const schedulerDaily = JSON.parse(readFileSync(join(fixtures, "scheduler-daily.json"), "utf8"));
const schedulerWeekly = JSON.parse(readFileSync(join(fixtures, "scheduler-weekly.json"), "utf8"));
const clone = v => structuredClone(v);

function sandbox() {
  const dir = mkdtempSync(join(tmpdir(), "tech-feed-validate-"));
  mkdirSync(join(dir, "data", "daily"), { recursive: true });
  mkdirSync(join(dir, "data", "weekly"), { recursive: true });
  mkdirSync(join(dir, "assets", "img"), { recursive: true });
  return dir;
}
function put(dir, kind, name, value) {
  const path = join(dir, "data", kind, name);
  writeFileSync(path, typeof value === "string" ? value : JSON.stringify(value, null, 2));
  return path;
}
const check = (dir, path) => validateFile(path, validators, { root: dir });

test("every committed publication is valid", () => {
  for (const file of allPublicationFiles()) assert.deepEqual(validateFile(file, validators), [], file);
});

test("scheduler output (pre-enrichment) is accepted unchanged", () => {
  const dir = sandbox();
  assert.deepEqual(check(dir, put(dir, "daily", `${schedulerDaily.date}.json`, schedulerDaily)), []);
  assert.deepEqual(check(dir, put(dir, "weekly", `${schedulerWeekly.weekEnding}.json`, schedulerWeekly)), []);
  rmSync(dir, { recursive: true });
});

test("unknown extra fields from the scheduler are allowed", () => {
  const dir = sandbox();
  const doc = clone(schedulerDaily);
  doc.newField = { anything: true };
  doc.topStories[0].extra = "ok";
  assert.deepEqual(check(dir, put(dir, "daily", `${doc.date}.json`, doc)), []);
  rmSync(dir, { recursive: true });
});

test("malformed publications are rejected", () => {
  const dir = sandbox();
  const date = schedulerDaily.date;
  const cases = {
    "missing summary": d => { delete d.topStories[0].summary; },
    "blank title": d => { d.alsoWorthKnowing[0].title = "  "; },
    "bad source url": d => { d.topStories[0].sources[0].url = "javascript:alert(1)"; },
    "no sources": d => { d.newTools[0].sources = []; },
    "missing section": d => { delete d.newTools; },
    "bad discussion": d => { d.topStories[0].discussions = [{ platform: "Reddit", url: "/r/x" }]; },
    "date mismatch": d => { d.date = "2026-01-01"; },
    "local image without dimensions": d => { d.topStories[0].image = { url: "https://e.com/a.png", local: "img/0123456789abcdef0123.webp" }; },
  };
  for (const [name, mutate] of Object.entries(cases)) {
    const doc = clone(schedulerDaily);
    mutate(doc);
    assert.notDeepEqual(check(dir, put(dir, "daily", `${date}.json`, doc)), [], name);
  }
  assert.notDeepEqual(check(dir, put(dir, "daily", `${date}.json`, "{ not json")), [], "unparseable");
  assert.notDeepEqual(check(dir, put(dir, "daily", "2026-02-30.json", { ...clone(schedulerDaily), date: "2026-02-30" })), [], "impossible date");
  const week = clone(schedulerWeekly);
  delete week.themes;
  assert.notDeepEqual(check(dir, put(dir, "weekly", `${week.weekEnding}.json`, week)), [], "weekly without themes");
  rmSync(dir, { recursive: true });
});

test("image.local must point to an existing optimized file", () => {
  const dir = sandbox();
  const doc = clone(schedulerDaily);
  doc.topStories[0].image = { url: "https://e.com/a.png", local: "img/0123456789abcdef0123.webp", width: 10, height: 10, sha256: "a".repeat(64) };
  const path = put(dir, "daily", `${doc.date}.json`, doc);
  assert.match(check(dir, path).join(), /does not exist/);
  writeFileSync(join(dir, "assets", "img", "0123456789abcdef0123.webp"), "x");
  assert.deepEqual(check(dir, path), []);
  rmSync(dir, { recursive: true });
});

test("quarantine removes only invalid files and succeeds", () => {
  const dir = sandbox();
  const good = put(dir, "daily", `${schedulerDaily.date}.json`, schedulerDaily);
  const bad = put(dir, "daily", "2026-11-17.json", "{ broken");
  const week = put(dir, "weekly", `${schedulerWeekly.weekEnding}.json`, schedulerWeekly);
  const report = join(dir, "quarantine.txt");
  const saved = { ...process.env };
  process.env.QUARANTINE_REPORT = report;
  delete process.env.GITHUB_STEP_SUMMARY;
  delete process.env.GITHUB_ACTIONS;
  const errors = console.error;
  console.error = () => {};
  try {
    assert.equal(main(["--root", dir]), 1, "strict mode fails");
    assert.equal(main(["--root", dir, "--quarantine"]), 0);
  } finally {
    console.error = errors;
    process.env = saved;
  }
  assert.ok(existsSync(good) && existsSync(week));
  assert.ok(!existsSync(bad));
  assert.equal(readFileSync(report, "utf8").trim(), "data/daily/2026-11-17.json");
  rmSync(dir, { recursive: true });
});
