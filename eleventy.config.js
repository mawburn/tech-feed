import { readFileSync } from "node:fs";

const fromJSON = (path) => JSON.parse(readFileSync(new URL(path, import.meta.url), "utf8"));
const briefing = fromJSON("./data/briefings.json");
const weekly = fromJSON("./data/weekly.json");
const issues = [...(briefing.issues ?? [])].sort((a, b) => b.date.localeCompare(a.date));
const weeks = [...(weekly.weeks ?? [])].sort((a, b) => b.weekEnding.localeCompare(a.weekEnding));

const slug = (s) => String(s ?? "").toLowerCase().normalize("NFKD")
  .replace(/[\u0300-\u036f]/g, "")
  .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

const storyList = (issue) => [
  ...(issue.topStories ?? []),
  ...(issue.alsoWorthKnowing ?? []),
  ...(issue.newTools ?? []),
];

const topicPages = [];
const allCategories = new Set();

for (const issue of issues) {
  const categories = new Set(storyList(issue).map(s => s.category || "Other"));
  for (const category of categories) {
    topicPages.push({ date: issue.date, category, slug: slug(category) });
    allCategories.add(category);
  }
}
for (const category of allCategories) {
  topicPages.push({ date: "all", category, slug: slug(category) });
}

export default function (eleventyConfig) {
  eleventyConfig.addGlobalData("feed", { ...briefing, issues });
  eleventyConfig.addGlobalData("weeklyFeed", { ...weekly, weeks });
  eleventyConfig.addGlobalData("topicPages", topicPages);

  // Daily JSON remains the authoritative source for the scheduled briefing;
  // weekly.json is updated by the Sunday automation.
  for (const path of [
    "assets/styles.css", "assets/favicon.svg",
    "data/briefings.json", "data/weekly.json",
    "archive.md", "weekly-archive.md", "llms.txt", "robots.txt",
  ]) {
    eleventyConfig.addPassthroughCopy(path);
  }

  // No frontend JS ships. All filtering, archive pages, and story links
  // are rendered to HTML by Eleventy during the GitHub Actions build.
  return {
    dir: { input: "src", output: "_site" },
    pathPrefix: "/tech-feed/",
    templateFormats: ["11ty.js"],
  };
}
