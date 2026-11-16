import assert from "node:assert/strict";
import {loadData} from "./data.mjs";

const {allDays,allWeeks,feed,weeklyFeed} = loadData();
const valid = url => {try {return ["https:","http:"].includes(new URL(url).protocol);}catch{return false;}};
const verifyLinks = (list,description) => {
  if(list===undefined) return;
  assert(Array.isArray(list), description+" must be an array");
  for(const link of list){
    assert(link && typeof link.platform==="string" && link.platform.trim(), description+" platform missing");
    assert(valid(link.url), description+" URL invalid");
    assert(link.label===undefined || typeof link.label==="string", description+" label must be text");
  }
};
for(const issue of allDays) {
  assert.match(issue.date,/^\d{4}-\d{2}-\d{2}$/);
  assert(typeof issue.overview==="string" && issue.overview.trim(),"Missing "+issue.date+" overview");
  assert(typeof issue.marketPulse==="string","Missing "+issue.date+" market pulse");
  for(const key of ["topStories","alsoWorthKnowing","newTools"]){
    assert(Array.isArray(issue[key]),issue.date+" missing "+key);
    for(const story of issue[key]){
      assert(typeof story.title==="string" && story.title.trim(),issue.date+" story missing title");
      assert(typeof story.summary==="string" && story.summary.trim(),story.title+" missing summary");
      assert(typeof story.category==="string" && story.category.trim(),story.title+" missing category");
      assert(Array.isArray(story.sources) && story.sources.length>0,story.title+" missing sources");
      for(const link of story.sources){
        assert(valid(link.url) && typeof link.label==="string",story.title+" invalid primary source");
      }
      verifyLinks(story.discoveredVia,story.title+" discoveredVia");
      verifyLinks(story.discussions,story.title+" discussions");
      if(story.image) assert(valid(story.image.url),story.title+" invalid image");
    }
  }
}
for(const week of allWeeks){
  assert.match(week.weekEnding,/^\d{4}-\d{2}-\d{2}$/);
  assert(Array.isArray(week.themes),week.weekEnding+" missing themes");
  assert(Array.isArray(week.toolsToWatch),week.weekEnding+" missing tools");
  assert(Array.isArray(week.sourceDays),week.weekEnding+" missing sourceDays");
  for(const theme of week.themes)verifyLinks(theme.discussions,theme.title+" discussions");
}
assert(feed.issues.length<=7,"More than seven recent daily editions");
assert(weeklyFeed.weeks.length<=52,"More than 52 weekly recaps");
console.log("Valid dated source files: "+allDays.length+" days, "+allWeeks.length+" weeks");
