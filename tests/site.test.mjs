// Checks the built site in public/ against the real publication data.
// Run after `hugo build`:  node --test tests/site.test.mjs
// Set HUGO_PARAMS_TODAY=YYYY-MM-DD for both the build and this test to pin the Pacific date.
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const out = join(root, process.env.SITE_DIR || "public");
const BASE_PATH = "/tech-feed/";
const BASE_URL = "https://mawburn.github.io/tech-feed/";
const SECTIONS = ["topStories", "alsoWorthKnowing", "newTools"];

const pacificToday = () => process.env.HUGO_PARAMS_TODAY ||
  new Intl.DateTimeFormat("en-CA", { timeZone: "America/Los_Angeles", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
const addDays = (iso, n) => new Date(Date.UTC(...iso.split("-").map((v, i) => Number(v) - (i === 1 ? 1 : 0))) + n * 864e5).toISOString().slice(0, 10);
const slug = text => String(text || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const loadDir = (dir, key) => readdirSync(join(root, "data", dir)).filter(f => /^\d{4}-\d{2}-\d{2}\.json$/.test(f))
  .map(f => JSON.parse(readFileSync(join(root, "data", dir, f), "utf8"))).sort((a, b) => b[key].localeCompare(a[key]));
const stories = issue => SECTIONS.flatMap(k => issue[k] || []);
const read = path => readFileSync(join(out, path), "utf8");
const exists = path => existsSync(join(out, path));
const decode = s => s.replace(/&amp;/g, "&").replace(/&#39;|&#x27;/g, "'").replace(/&quot;|&#34;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const htmlFiles = dir => readdirSync(dir).flatMap(name => {
  const p = join(dir, name);
  return statSync(p).isDirectory() ? htmlFiles(p) : p.endsWith(".html") ? [p] : [];
});
const attrs = (html, name) => [...html.matchAll(new RegExp(`\\s${name}=(?:"([^"]*)"|'([^']*)'|([^\\s>]+))`, "g"))].map(m => decode(m[1] ?? m[2] ?? m[3]));

const today = pacificToday();
const windowStart = addDays(today, -6);
const published = loadDir("daily", "date").filter(i => i.date <= today);
const windowIssues = published.filter(i => i.date >= windowStart);
const weeks = loadDir("weekly", "weekEnding");

test("built site exists", () => {
  assert.ok(exists("index.html"), "run `hugo build` first");
});

test("fixed routes are generated", () => {
  for (const path of ["index.html", "all/index.html", "weekly.html", "daily/index.html", "weekly/index.html",
    "topics/index.html", "data/briefings.json", "data/weekly.json", "archive.md", "weekly-archive.md",
    "sitemap.xml", "robots.txt", "llms.txt", "favicon.svg", ".nojekyll"]) {
    assert.ok(exists(path), `missing ${path}`);
  }
});

test("every daily edition, per-edition topic and global topic page exists", () => {
  const categories = new Set();
  for (const issue of published) {
    assert.ok(exists(`daily/${issue.date}/index.html`), `missing daily/${issue.date}/`);
    for (const story of stories(issue)) {
      categories.add(story.category);
      assert.ok(exists(`daily/${issue.date}/topics/${slug(story.category)}/index.html`), `missing topic ${story.category} on ${issue.date}`);
    }
  }
  for (const category of categories) assert.ok(exists(`topics/${slug(category)}/index.html`), `missing /topics/${slug(category)}/`);
  for (const week of weeks) assert.ok(exists(`weekly/${week.weekEnding}/index.html`), `missing weekly/${week.weekEnding}/`);
});

test("homepage shows the latest published edition", () => {
  const html = decode(read("index.html"));
  const latest = published[0];
  if (!latest) return assert.match(html, /No daily briefing/);
  for (const story of stories(latest)) assert.ok(html.includes(story.title), `homepage missing "${story.title}"`);
  const future = loadDir("daily", "date").filter(i => i.date > today);
  for (const issue of future) for (const s of stories(issue)) assert.ok(!html.includes(s.title), "future edition leaked onto homepage");
});

test("/weekly.html shows the latest weekly review", () => {
  const html = decode(read("weekly.html"));
  if (weeks[0]) assert.ok(html.includes(weeks[0].title), "latest weekly title missing");
});

test("daily pages contain every story and discussion link", () => {
  for (const issue of published) {
    const html = decode(read(`daily/${issue.date}/index.html`));
    for (const story of stories(issue)) {
      assert.ok(html.includes(story.title), `${issue.date}: missing "${story.title}"`);
      for (const d of story.discussions || []) assert.ok(html.includes(d.url), `${issue.date}: missing discussion ${d.url}`);
      for (const s of story.sources) assert.ok(html.includes(s.url), `${issue.date}: missing source ${s.url}`);
    }
  }
});

test("per-edition topic pages contain only that topic", () => {
  for (const issue of published) {
    for (const category of new Set(stories(issue).map(s => s.category))) {
      const html = decode(read(`daily/${issue.date}/topics/${slug(category)}/index.html`));
      for (const story of stories(issue)) {
        const shown = html.includes(`story__title>${story.title}<`) || html.includes(`story__title">${story.title}<`);
        assert.equal(shown, story.category === category, `${issue.date}/${category}: "${story.title}"`);
      }
    }
  }
});

test("JSON feeds keep their windows and schema shape", () => {
  const daily = JSON.parse(read("data/briefings.json"));
  assert.equal(daily.schemaVersion, 1);
  assert.ok(!Number.isNaN(Date.parse(daily.updatedAt)));
  assert.deepEqual(daily.issues.map(i => i.date), windowIssues.map(i => i.date));
  for (const [i, issue] of daily.issues.entries()) {
    const source = windowIssues[i];
    assert.deepEqual(Object.keys(issue).sort(), Object.keys(source).sort());
    assert.deepEqual(stories(issue).map(s => s.title), stories(source).map(s => s.title));
    for (const s of stories(issue)) if (s.image?.local) {
      assert.ok(s.image.localUrl?.startsWith(BASE_URL), "image.localUrl must be absolute");
      assert.ok(exists(s.image.localUrl.slice(BASE_URL.length)), `localUrl not published: ${s.image.localUrl}`);
    }
  }
  const weekly = JSON.parse(read("data/weekly.json"));
  assert.equal(weekly.schemaVersion, 1);
  assert.ok(weekly.weeks.length <= 52);
  assert.deepEqual(weekly.weeks.map(w => w.weekEnding), weeks.slice(0, 52).map(w => w.weekEnding));
});

test("links, assets and images respect the /tech-feed/ prefix and resolve locally", () => {
  for (const file of htmlFiles(out)) {
    const html = readFileSync(file, "utf8");
    const rel = file.slice(out.length + 1);
    assert.ok(!/<script\b[^>]*\bsrc=/i.test(html), `${rel}: unexpected external script`);
    for (const url of [...attrs(html, "href"), ...attrs(html, "src")]) {
      if (/^(https?:|mailto:|#|data:)/.test(url)) continue;
      assert.ok(url.startsWith(BASE_PATH), `${rel}: link without base path: ${url}`);
      const path = url.slice(BASE_PATH.length).split(/[?#]/)[0];
      const target = path === "" || path.endsWith("/") ? path + "index.html" : path;
      assert.ok(exists(target), `${rel}: broken internal link ${url}`);
    }
    for (const src of [...attrs(html, "src")].filter(u => !u.startsWith("data:"))) {
      assert.ok(src.startsWith(BASE_PATH), `${rel}: external image ${src}`);
    }
    for (const set of attrs(html, "srcset")) {
      for (const candidate of set.split(",").map(s => s.trim().split(/\s+/)[0])) {
        assert.ok(candidate.startsWith(BASE_PATH) && exists(candidate.slice(BASE_PATH.length)), `${rel}: bad srcset ${candidate}`);
      }
    }
    const canonical = html.match(/<link rel="?canonical"? href="?([^"\s>]+)/);
    assert.ok(canonical && canonical[1].startsWith(BASE_URL), `${rel}: canonical must be absolute under ${BASE_URL}`);
    assert.equal((html.match(/<h1[\s>]/g) || []).length, 1, `${rel}: exactly one <h1>`);
  }
});

test("sitemap lists every edition with absolute URLs", () => {
  const xml = read("sitemap.xml");
  const locs = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1]);
  assert.ok(locs.every(l => l.startsWith(BASE_URL)));
  for (const issue of published) assert.ok(locs.includes(`${BASE_URL}daily/${issue.date}/`));
  for (const week of weeks) assert.ok(locs.includes(`${BASE_URL}weekly/${week.weekEnding}/`));
  assert.ok(locs.includes(`${BASE_URL}weekly.html`));
  assert.ok(locs.includes(`${BASE_URL}data/briefings.json`));
  assert.match(read("robots.txt"), new RegExp(`Sitemap: ${BASE_URL}sitemap.xml`));
});

test("markdown archives and llms.txt use absolute site URLs", () => {
  const archive = read("archive.md");
  for (const issue of windowIssues) assert.ok(archive.includes(`## ${issue.date}`));
  const llms = read("llms.txt");
  assert.ok(llms.includes(`${BASE_URL}data/briefings.json`));
  assert.ok(!/\]\(\//.test(archive), "archive.md contains root-relative links");
});
