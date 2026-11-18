#!/usr/bin/env node
// Validate dated publication files against the versioned JSON Schemas in schemas/.
//
//   node scripts/validate-content.mjs                 validate every data/incidents, data/daily and data/weekly file
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
  // incidents first: daily/weekly incidentId references are checked against the valid ones
  incidents: { dir: "data/incidents", schema: "incident.v1.schema.json", dateKey: null },
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

/** incidentId references in a daily or weekly document: [{path, id}] */
function incidentRefs(kind, doc) {
  const refs = [];
  const add = (path, value) => { if (typeof value?.incidentId === "string") refs.push({ path, id: value.incidentId }); };
  if (kind === "daily") {
    for (const key of SECTIONS) (Array.isArray(doc[key]) ? doc[key] : []).forEach((s, i) => add(`/${key}/${i}`, s));
  } else {
    (Array.isArray(doc.themes) ? doc.themes : []).forEach((t, i) => add(`/themes/${i}`, t));
  }
  (Array.isArray(doc.discoveryAudit?.majorIncidentsConsidered) ? doc.discoveryAudit.majorIncidentsConsidered : [])
    .forEach((m, i) => add(`/discoveryAudit/majorIncidentsConsidered/${i}`, m));
  return refs;
}

/** Cross-field rules JSON Schema cannot express. Returns problems for a schema-valid incident. */
function incidentProblems(doc) {
  const problems = [];
  const dates = ["occurredDate", "discoveredDate", "resolvedDate", "fixDate"];
  for (const key of dates) if (doc[key] && !realDate(doc[key])) problems.push(`${key} ${doc[key]} is not a real calendar date`);
  for (const [i, h] of (doc.history || []).entries()) {
    if (h?.date && !realDate(h.date)) problems.push(`history[${i}].date ${h.date} is not a real calendar date`);
    if (i > 0 && h?.date && doc.history[i - 1]?.date && h.date < doc.history[i - 1].date) {
      problems.push(`history must be chronological: entry ${i} (${h.date}) is before entry ${i - 1} (${doc.history[i - 1].date})`);
    }
  }
  const before = (a, b, label) => { if (doc[a] && doc[b] && doc[a] > doc[b]) problems.push(label); };
  before("occurredDate", "discoveredDate", "occurredDate is after discoveredDate");
  before("discoveredDate", "resolvedDate", "resolvedDate is before discoveredDate");
  before("discoveredDate", "fixDate", "fixDate is before discoveredDate");
  if (doc.resolvedDate && doc.status && doc.status !== "resolved") {
    problems.push(`resolvedDate is set but status is "${doc.status}" (reopened incidents must clear resolvedDate)`);
  }
  const lastStatus = [...(doc.history || [])].reverse().find(h => h?.status)?.status;
  if (lastStatus && doc.status && lastStatus !== doc.status) {
    problems.push(`status "${doc.status}" does not match the latest history status "${lastStatus}"`);
  }
  return problems;
}

/** Ids of incident files that validate; used to check incidentId references. */
export function knownIncidentIds(validators, root = repoRoot) {
  const folder = join(root, KINDS.incidents.dir);
  if (!existsSync(folder)) return new Set();
  const ids = new Set();
  for (const f of readdirSync(folder).filter(f => f.endsWith(".json"))) {
    if (!validateFile(join(folder, f), validators, { root, incidentIds: new Set() }).length) ids.add(f.slice(0, -5));
  }
  return ids;
}

function imagesOf(kind, doc) {
  if (kind === "daily") return SECTIONS.flatMap(k => (Array.isArray(doc[k]) ? doc[k] : [])).map(s => s?.image);
  return (Array.isArray(doc.themes) ? doc.themes : []).map(t => t?.image);
}

/** Validate one publication file. Returns a list of human-readable problems (empty when valid). */
export function validateFile(path, validators, { root = repoRoot, assetsDir = join(root, "assets"), incidentIds } = {}) {
  const rel = relative(root, path);
  const kind = rel.startsWith("data/weekly/") ? "weekly" : rel.startsWith("data/daily/") ? "daily"
    : rel.startsWith("data/incidents/") ? "incidents" : null;
  if (!kind) return [`${rel}: not under data/daily, data/weekly or data/incidents`];
  const name = basename(path);
  if (kind === "incidents") {
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*\.json$/.test(name)) return [`${rel}: file name must be <incident-id>.json (lowercase kebab-case)`];
  } else if (!/^\d{4}-\d{2}-\d{2}\.json$/.test(name)) return [`${rel}: file name must be YYYY-MM-DD.json`];
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
  if (kind === "incidents") {
    const schemaOk = !problems.length;
    if (doc && doc.id !== name.slice(0, -5)) problems.push(`${rel}: id "${doc?.id}" does not match file name`);
    if (schemaOk) for (const p of incidentProblems(doc)) problems.push(`${rel}: ${p}`);
    return problems;
  }
  const date = name.slice(0, 10);
  const key = KINDS[kind].dateKey;
  if (doc && doc[key] !== date) problems.push(`${rel}: ${key} "${doc?.[key]}" does not match file name`);
  if (!realDate(date)) problems.push(`${rel}: ${date} is not a real calendar date`);
  if (doc && typeof doc === "object") {
    const refs = incidentRefs(kind, doc);
    if (refs.length) {
      const known = incidentIds ?? knownIncidentIds(validators, root);
      for (const { path: at, id } of refs) {
        if (!known.has(id)) problems.push(`${rel}: ${at}/incidentId "${id}" has no valid record in data/incidents/${id}.json`);
      }
    }
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
  // Computed once from the incident records that are valid *now*, so a quarantined
  // incident also orphans (and quarantines) the reports that point at it.
  const incidentIds = knownIncidentIds(validators, root);
  for (const file of targets) {
    if (!existsSync(file)) continue; // deleted in this change
    const problems = validateFile(file, validators, { root, incidentIds });
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
  const count = dir => targets.filter(f => f.includes(`/data/${dir}/`)).length;
  console.log(`Valid publications: ${count("daily")} daily, ${count("weekly")} weekly, ${count("incidents")} incidents`);
  return 0;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exitCode = main(process.argv.slice(2));
}
