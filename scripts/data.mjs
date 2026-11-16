// Per-edition JSON documents are the authoritative content store.
// The two combined /data/*.json endpoints are build artifacts, not source data.
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
const root = fileURLToPath(new URL("../", import.meta.url));

function loadDated(dir, field) {
  const folder = join(root, "data", dir);
  return readdirSync(folder)
    .filter(file => /^\d{4}-\d{2}-\d{2}\.json$/.test(file))
    .map(file => {
      const data = JSON.parse(readFileSync(join(folder, file), "utf8"));
      const date = file.slice(0, 10);
      if(data[field] !== date) throw new Error("Date mismatch in "+dir+"/"+file);
      return data;
    })
    .sort((a,b) => b[field].localeCompare(a[field]));
}
function pacificDate(now) {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/Los_Angeles", year:"numeric",month:"2-digit",day:"2-digit"
  }).formatToParts(now);
  const p = Object.fromEntries(parts.map(({type,value})=>[type,value]));
  return p.year+"-"+p.month+"-"+p.day;
}
function startOfWindow(today) {
  const [year,month,day] = today.split("-").map(Number);
  return new Date(Date.UTC(year,month-1,day-6)).toISOString().slice(0,10);
}
export function loadData(now = new Date()) {
  const allDays = loadDated("daily","date");
  const today = pacificDate(now);
  const start = startOfWindow(today);
  const issues = allDays.filter(issue => issue.date >= start && issue.date <= today);
  const allWeeks = loadDated("weekly","weekEnding");
  const weeks = allWeeks.slice(0,52);
  const generatedAt = now.toISOString();
  return {
    feed: {schemaVersion:1,updatedAt:generatedAt,issues},
    weeklyFeed: {schemaVersion:1,updatedAt:generatedAt,weeks},
    allDays,allWeeks
  };
}
