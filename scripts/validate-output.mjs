import assert from "node:assert/strict";
import {existsSync,readFileSync} from "node:fs";
import {join} from "node:path";
import {loadData} from "./data.mjs";

const {feed,weeklyFeed}=loadData();
const out="_site", verify=path=>assert(existsSync(join(out,path)),"Missing generated file: "+path);
const read=path=>readFileSync(join(out,path),"utf8");
const safe=val=>String(val??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const expected=[
 "index.html","all/index.html","weekly.html","sitemap.xml",
 "assets/styles.css","assets/favicon.svg","data/briefings.json","data/weekly.json",
 "llms.txt","archive.md","weekly-archive.md","robots.txt"
];
for(const name of expected)verify(name);
const builtDaily=JSON.parse(read("data/briefings.json"));
const builtWeekly=JSON.parse(read("data/weekly.json"));
assert.deepEqual(builtDaily.issues.map(x=>x.date),feed.issues.map(x=>x.date),"Generated daily index mismatch");
assert.deepEqual(builtWeekly.weeks.map(x=>x.weekEnding),weeklyFeed.weeks.map(x=>x.weekEnding),"Generated weekly index mismatch");
for(const issue of feed.issues){
 const filename="daily/"+issue.date+"/index.html";
 verify(filename);
 const html=read(filename);
 for(const key of ["topStories","alsoWorthKnowing","newTools"]){
  for(const item of issue[key]||[]){
   assert(html.includes(safe(item.title)), "Missing story "+item.title+" on "+issue.date);
   for(const discussion of item.discussions||[]){
    const url=safe(discussion.url);
    assert(html.includes(url),"Missing community link for "+item.title);
    assert(html.includes('class="thread-pill"'),"Missing visible discussion badge on "+issue.date);
   }
  }
 }
}
// The homepage must include the latest edition's actual discussion links,
 // not only the dated deep-link pages.
const latest=feed.issues[0];
if(latest){
  const homepage=read("index.html");
  const latestStories=[...(latest.topStories||[]),...(latest.alsoWorthKnowing||[]),...(latest.newTools||[])];
  const expected=latestStories.flatMap(story=>story.discussions||[]);
  for(const thread of expected){
    assert(homepage.includes(safe(thread.url)),"Homepage lost prefetched thread "+thread.url);
  }
  if(expected.length){
    assert(homepage.includes('class="thread-pill"'),"Homepage lacks visible discussion badges");
    assert(homepage.includes("HN/Reddit"),"Homepage lacks discussion count");
  }
  console.log("Latest homepage includes "+expected.length+" prefetched discussion links");
}

for(const week of weeklyFeed.weeks){
 const path="weekly/"+week.weekEnding+"/index.html";
 verify(path);
 assert(read(path).includes(safe(week.title)),"Missing weekly headline "+week.weekEnding);
}
for(const path of ["index.html","weekly.html"]){
 assert(!/<script\b[^>]*\bsrc\s*=/.test(read(path)),"Unexpected client-side JS "+path);
}
console.log("Verified "+feed.issues.length+" recent daily HTML pages, "+weeklyFeed.weeks.length+" weekly pages and two generated JSON feeds");
