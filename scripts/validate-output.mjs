import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const daily = JSON.parse(readFileSync("data/briefings.json","utf8"));
const weekly = JSON.parse(readFileSync("data/weekly.json","utf8"));
const out = "_site";
const verify = path => assert(existsSync(join(out,path)), "Missing generated file: " + path);
const read = path => readFileSync(join(out,path),"utf8");

for(const name of ["index.html","all/index.html","weekly.html","sitemap.xml",
  "assets/styles.css","assets/favicon.svg","data/briefings.json","data/weekly.json",
  "llms.txt","archive.md","weekly-archive.md","robots.txt"]) verify(name);

for(const day of daily.issues){
  const name = "daily/" + day.date + "/index.html";
  verify(name);
  const html = read(name);
  for(const key of ["topStories","alsoWorthKnowing","newTools"]){
    const stories = day[key] || [];
    for(const story of stories) {
      assert(html.includes(escapeHTML(story.title)), "Missing story " + story.title + " on " + day.date);
    }
  }
}
for(const week of weekly.weeks){
  const name = "weekly/" + week.weekEnding + "/index.html";
  verify(name);
  assert(read(name).includes(escapeHTML(week.title)), "Missing week " + week.weekEnding);
}
for(const [name,html] of [["index.html",read("index.html")],["weekly.html",read("weekly.html")]]){
  assert(!/<script\b[^>]*\bsrc\s*=/.test(html), "Unexpected client JS script in "+name);
  assert(!html.includes("Loading latest edition"), "Found client-rendered placeholder in "+name);
}
assert(read("sitemap.xml").includes("/tech-feed/weekly.html"));
console.log("Static pages generated and verified: "+daily.issues.length+" dated daily editions, "+weekly.weeks.length+" weekly summaries");
function escapeHTML(value) {
  return String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
