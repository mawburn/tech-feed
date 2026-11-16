import { loadData } from "./scripts/data.mjs";

// Indexes are generated from dated JSON files, not edited on each new briefing.
const {feed, weeklyFeed} = loadData();
const issues = feed.issues;
const weeks = weeklyFeed.weeks;
const slug = text => String(text || "").toLowerCase().normalize("NFKD")
  .replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const stories = issue => [
  ...(issue.topStories || []),
  ...(issue.alsoWorthKnowing || []),
  ...(issue.newTools || [])
];
const topicPages = [];
const globalCategories = new Set();
for (const issue of issues) {
  for (const category of new Set(stories(issue).map(s => s.category || "Other"))) {
    topicPages.push({ date: issue.date, category, slug: slug(category),
      permalink: "/daily/" + issue.date + "/topics/" + slug(category) + "/index.html" });
    globalCategories.add(category);
  }
}
for (const category of globalCategories) {
  topicPages.push({ date: "all", category, slug: slug(category),
    permalink: "/topics/" + slug(category) + "/index.html" });
}

const dateObj = iso => new Date(String(iso) + "T12:00:00Z");
const shortDate = new Intl.DateTimeFormat("en-US", {month:"short", day:"numeric", timeZone:"UTC"});
const fullDate = new Intl.DateTimeFormat("en-US", {weekday:"long",month:"long",day:"numeric",year:"numeric", timeZone:"UTC"});
const monthYear = new Intl.DateTimeFormat("en-US", {month:"long",day:"numeric",year:"numeric", timeZone:"UTC"});
const http = url => {
  try { return ["http:", "https:"].includes(new URL(String(url)).protocol); }
  catch { return false; }
};
const base = "/tech-feed";
const url = path => base + (String(path).startsWith("/") ? path : "/" + path);
const dayRoute = day => day === "all" ? "/all/" : "/daily/" + day + "/";
const topicRoute = (day, category) => day === "all"
  ? "/topics/" + slug(category) + "/" :
    "/daily/" + day + "/topics/" + slug(category) + "/";

export default function(eleventyConfig) {
  eleventyConfig.setNunjucksEnvironmentOptions({ autoescape: true });
  eleventyConfig.addGlobalData("feed", feed);
  eleventyConfig.addGlobalData("weeklyFeed", weeklyFeed);
  eleventyConfig.addGlobalData("topicPages", topicPages);
  eleventyConfig.addGlobalData("projectSite", {
    base, baseUrl: "https://mawburn.github.io/tech-feed",
    name: "mawburn Feed"
  });
  eleventyConfig.addFilter("siteUrl", url);
  eleventyConfig.addFilter("absoluteUrl", path => "https://mawburn.github.io" + url(path));
  eleventyConfig.addFilter("isHttp", http);
  eleventyConfig.addFilter("slug", slug);
  eleventyConfig.addFilter("pad2", value => String(value ?? "").padStart(2, "0"));
  eleventyConfig.addFilter("json", value => JSON.stringify(value, null, 2));
  eleventyConfig.addFilter("dayRoute", dayRoute);
  eleventyConfig.addFilter("topicRoute", topicRoute);
  eleventyConfig.addFilter("dateShort", iso => shortDate.format(dateObj(iso)));
  eleventyConfig.addFilter("dateFull", iso => fullDate.format(dateObj(iso)));
  eleventyConfig.addFilter("dateMonthYear", iso => monthYear.format(dateObj(iso)));
  eleventyConfig.addFilter("weekLabel", week =>
    shortDate.format(dateObj(week.weekStart)) + " – " + monthYear.format(dateObj(week.weekEnding)));
  eleventyConfig.addFilter("storyList", issuesArg => (issuesArg || []).flatMap(stories));
  eleventyConfig.addFilter("getIssues", (all, day) => day === "all" ? all : all.filter(i => i.date === day));
  eleventyConfig.addFilter("matchesCategory", (all, category) => !category ? (all || []) :
    (all || []).filter(item => (item.category || "Other") === category));
  eleventyConfig.addFilter("countCategory", (all, category) => !category ? (all || []).length :
    (all || []).filter(item => (item.category || "Other") === category).length);
  eleventyConfig.addFilter("topicCounts", issueList => {
    const counts = new Map();
    for (const issue of issueList || []) {
      for (const s of stories(issue)) {
        const category = s.category || "Other";
        counts.set(category, (counts.get(category) || 0) + 1);
      }
    }
    return [...counts].sort((a,b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .map(([name,count]) => ({name,count,slug:slug(name)}));
  });
  eleventyConfig.addFilter("totalStories", issueList => (issueList || []).reduce((n,i) => n + stories(i).length,0));
  eleventyConfig.addFilter("sumTopicCounts", counts => (counts || []).reduce((n,c) => n + c.count,0));

  // Date-specific source files are read during the build. Generated feeds and
  // Markdown indexes are rendered from templates in src/, not copied from main.
  [
    "assets/styles.css", "assets/favicon.svg", "llms.txt", "robots.txt",
  ].forEach(path => eleventyConfig.addPassthroughCopy(path));

  return {
    dir: { input: "src", includes: "_includes", output: "_site" },
    pathPrefix: "/tech-feed/",
    templateFormats: ["njk"]
  };
}
