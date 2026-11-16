#!/usr/bin/env node
// Validate dated publication files against the versioned JSON Schemas in schemas/.
//
//   node scripts/validate-content.mjs                 validate every data/daily + data/weekly file
//   node scripts/validate-content.mjs FILE...         validate only these files
//   node scripts/validate-content.mjs --quarantine    CI build mode: remove invalid files from the
//                                                     working copy (never from git) so Hugo builds the
//                                                     valid ones, then exit 0 and record what was removed
//
// In quarantine mode the list of removed files is written to $QUARANTINE_REPORT (if set) and the
// GitHub step summary, so the workflow can deploy the valid content and fail afterwards.
import { readFileSync, readdirSync, existsSync, rmSync, appendFileSync, writeFileSync } from "node:fs";
import { join, relative, resolve, basename, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const schemaDir = join(repoRoot, "schemas");
const KINDS = {
  daily: { dir: "data/daily", schema: "daily.v1.schema.json", dateKey: "date" },
  weekly: { dir: "data/weekly", schema: "weekly.v1.schema.json", dateKey: "weekEnding" },
};
const SECTIONS = ["topStories", "alsoWorthKnowing", "newTools"];

export function createValidators() {
  const ajv = new Ajv2020({ allErrors: true, strict: false });
  addFormats(ajv);
  for (const file of readdirSync(schemaDir).filter(f => f.endsWith(".schema.json"))) {
    ajv.addSchema(JSON.parse(readFileSync(join(schemaDir, file), "utf8")), file);
  }
  return Object.fromEntries(Object.entries(KINDS).map(([kind, k]) => [kind, ajv.getSchema(k.schema)]));
}

const realDate = s => {
  const d = new Date(`${s}T00:00:00Z`);
  return !Number.isNaN(d.getTime()) && d.toISOString().slice(0, 10) === s;
};

function imagesOf(kind, doc) {
  if (kind === "daily") return SECTIONS.flatMap(k => (Array.isArray(doc[k]) ? doc[k] : [])).map(s => s?.image);
  return (Array.isArray(doc.themes) ? doc.themes : []).map(t => t?.image);
}

/** Validate one publication file. Returns a list of human-readable problems (empty when valid). */
export function validateFile(path, validators, { root = repoRoot, assetsDir = join(root, "assets") } = {}) {
  const rel = relative(root, path);
  const kind = rel.startsWith("data/weekly/") ? "weekly" : rel.startsWith("data/daily/") ? "daily" : null;
  if (!kind) return [`${rel}: not under data/daily or data/weekly`];
  const name = basename(path);
  if (!/^\d{4}-\d{2}-\d{2}\.json$/.test(name)) return [`${rel}: file name must be YYYY-MM-DD.json`];
  let doc;
  try {
    doc = JSON.parse(readFileSync(path, "utf8"));
  } catch (error) {
    return [`${rel}: invalid JSON (${error.message})`];
  }
  const problems = [];
  const validate = validators[kind];
  if (!validate(doc)) {
    for (const e of validate.errors) problems.push(`${rel}: ${e.instancePath || "/"} ${e.message}`);
  }
  const date = name.slice(0, 10);
  const key = KINDS[kind].dateKey;
  if (doc && doc[key] !== date) problems.push(`${rel}: ${key} "${doc?.[key]}" does not match file name`);
  if (!realDate(date)) problems.push(`${rel}: ${date} is not a real calendar date`);
  if (doc && typeof doc === "object") {
    for (const image of imagesOf(kind, doc)) {
      if (image?.local && !existsSync(join(assetsDir, image.local))) {
        problems.push(`${rel}: image.local ${image.local} does not exist under assets/`);
      }
    }
  }
  return problems;
}

export function allPublicationFiles(base = repoRoot) {
  return Object.values(KINDS).flatMap(({ dir }) => {
    const folder = join(base, dir);
    if (!existsSync(folder)) return [];
    return readdirSync(folder).filter(f => f.endsWith(".json")).sort().map(f => join(folder, f));
  });
}

export function main(argv) {
  const quarantine = argv.includes("--quarantine");
  const rootIndex = argv.indexOf("--root");
  const root = rootIndex >= 0 ? resolve(argv[rootIndex + 1]) : repoRoot;
  const files = argv.filter((a, i) => !a.startsWith("--") && argv[i - 1] !== "--root").map(f => resolve(f));
  const targets = files.length ? files : allPublicationFiles(root);
  const validators = createValidators();
  const failed = [];
  for (const file of targets) {
    if (!existsSync(file)) continue; // deleted in this change
    const problems = validateFile(file, validators, { root });
    if (problems.length) failed.push({ file: relative(root, file), problems });
  }
  for (const { file, problems } of failed) {
    for (const p of problems) {
      console.error(process.env.GITHUB_ACTIONS ? `::error file=${file}::${p}` : `✗ ${p}`);
    }
  }
  if (quarantine && failed.length) {
    for (const { file } of failed) rmSync(join(root, file));
    const lines = ["### Quarantined publications", "", "These files failed validation and were left out of this build:", "",
      ...failed.map(f => `- \`${f.file}\`: ${f.problems.slice(0, 3).join("; ")}`), ""];
    if (process.env.GITHUB_STEP_SUMMARY) appendFileSync(process.env.GITHUB_STEP_SUMMARY, lines.join("\n") + "\n");
    if (process.env.QUARANTINE_REPORT) writeFileSync(process.env.QUARANTINE_REPORT, failed.map(f => f.file).join("\n") + "\n");
    console.error(`Quarantined ${failed.length} invalid file(s); building the remaining ${targets.length - failed.length}.`);
    return 0;
  }
  if (failed.length) {
    console.error(`${failed.length} of ${targets.length} publication file(s) are invalid.`);
    return 1;
  }
  const daily = targets.filter(f => f.includes("/data/daily/")).length;
  console.log(`Valid publications: ${daily} daily, ${targets.length - daily} weekly`);
  return 0;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exitCode = main(process.argv.slice(2));
}
