import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const daily = JSON.parse(readFileSync("data/briefings.json","utf8"));
const weekly = JSON.parse(readFileSync("data/weekly.json","utf8"));
assert.equal(daily.schemaVersion, 1, "Unexpected daily data schema");
assert.equal(weekly.schemaVersion, 1, "Unexpected weekly data schema");
assert(Array.isArray(daily.issues), "Missing daily issues");
assert(Array.isArray(weekly.weeks), "Missing weekly recaps");

const dayIds = new Set();
for(const day of daily.issues){
  assert.match(day.date, /^\d{4}-\d{2}-\d{2}$/, "Invalid daily date");
  assert(!dayIds.has(day.date), "Duplicate daily edition: " + day.date);
  dayIds.add(day.date);
  for(const key of ["topStories","alsoWorthKnowing","newTools"]){
    assert(Array.isArray(day[key]), "Missing " + key + " on " + day.date);
  }
  assert(typeof day.overview === "string", "Missing overview");
}
const weekIds = new Set();
for(const week of weekly.weeks){
  assert.match(week.weekEnding, /^\d{4}-\d{2}-\d{2}$/, "Invalid Sunday date");
  assert(!weekIds.has(week.weekEnding), "Duplicate week");
  weekIds.add(week.weekEnding);
  assert(Array.isArray(week.themes) && week.themes.length > 0, "Missing weekly themes");
  assert(Array.isArray(week.toolsToWatch), "Missing toolsToWatch");
  assert(Array.isArray(week.sourceDays), "Missing weekly sourceDays");
}
console.log("Valid static generation inputs: " + daily.issues.length + " days, " + weekly.weeks.length + " weeks");
