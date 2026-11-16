import { readFileSync } from 'node:fs';
const feed = JSON.parse(readFileSync(new URL('../data/briefings.json', import.meta.url), 'utf-8'));
const errors = [];
const validURL = value => { try {return ['https:', 'http:'].includes(new URL(value).protocol);} catch {return false;} };
if (feed.schemaVersion !== 1 || !Array.isArray(feed.issues)) errors.push('Invalid feed schema');
const seen=new Set();
for(const issue of feed.issues||[]){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(issue.date)) errors.push('Invalid date');
 if(seen.has(issue.date)) errors.push('Duplicate edition');seen.add(issue.date);
 for(const key of ['topStories','alsoWorthKnowing','newTools']){
  if(!Array.isArray(issue[key])) {errors.push('Missing '+key);continue;}
  for(const story of issue[key]){
   if(!story.title||!story.summary||!story.category||!story.sources?.length) errors.push('Incomplete story: '+story.title);
   for(const src of story.sources||[]) if(!src.label||!validURL(src.url)) errors.push('Bad URL: '+story.title);
  }
 }
}
if((feed.issues||[]).length>7) errors.push('Too many editions');
if(errors.length){console.error(errors.join('\n'));process.exit(1);}
console.log('Valid feed with '+feed.issues.length+' editions');