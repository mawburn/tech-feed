# mawburn Feed

A zero-client-JavaScript daily/weekly technology news site generated with **Eleventy 3 + Nunjucks** and deployed on **GitHub Pages**.

Public URL: https://mawburn.github.io/tech-feed/

## How it works

1. The existing 7 AM Pacific Morning AI & Developer Brief task writes the full day's news to data/briefings.json on main, preserving the previous six Pacific dates. It also updates archive.md.
2. The Sunday Technology Weekly Review task writes a deduplicated Monday–Sunday recap to data/weekly.json, preserving up to 52 weeks, and updates weekly-archive.md.
3. The Sync publisher Open Graph images GitHub Action scans source URLs and attaches verified publisher OG image metadata to stories in data/briefings.json.
4. The Build and deploy static news site GitHub Action installs Eleventy, validates JSON, renders static HTML under _site/, and uploads it to GitHub Pages. It runs on feed/template changes and after image sync.

Every story, source link, topic count, and daily/weekly navigation link is rendered into HTML during the build. **The deployed site does not require JavaScript to display news.** Nunjucks templates run only at build time.

## Required GitHub Pages setting

**Repository → Settings → Pages → Build and deployment → Source: GitHub Actions.**

This replaces the old Deploy from a branch / main / (root) setting. The connected GitHub tools cannot switch this setting.

Once switched, open the [Build and deploy static news site workflow](https://github.com/mawburn/tech-feed/actions/workflows/deploy-pages.yml) and select Run workflow, or allow the next commit to trigger it. The first successful deployment serves https://mawburn.github.io/tech-feed/.

The former root index.html, weekly.html, assets/app.js, and assets/weekly.js remain as a rollback option. Eleventy reads only src/ and deploys only the generated _site/ folder, so those legacy scripts **are not included** in the static Pages build. They can be removed after deployment is verified.

## Generated pages

- / — newest complete daily briefing
- /daily/YYYY-MM-DD/ — individual daily edition
- /daily/YYYY-MM-DD/topics/TOPIC/ — static topic filter for that day
- /all/ and /topics/TOPIC/ — seven-day archive and global topic pages
- /weekly.html — most recent Sunday recap
- /weekly/YYYY-MM-DD/ — historical weekly summaries (up to 52 weeks)
- /sitemap.xml, /llms.txt, /archive.md, /weekly-archive.md
- /data/briefings.json and /data/weekly.json

Article images use the publishers' OG image URLs, with credits. Stories without a valid source image appear as text.

## Develop locally

Requires Node.js 20 or newer.

    npm install
    npm run check
    npm run build
    npm run dev

Generated pages appear in _site/. The site uses the GitHub Pages project path /tech-feed/ in its links. For a local server mounted at /, adjust the base/siteUrl filter in eleventy.config.js or serve the build at that prefix.

## Templates

- src/_includes/layouts/base.njk — HTML shell, SEO, navigation
- src/_includes/partials/edition.njk — daily story sections
- src/_includes/partials/daily-sidebar.njk — server-rendered topic/date links
- src/_includes/partials/weekly-layout.njk — weekly recap
- src/daily.njk, src/topics.njk, src/weekly-date.njk — per-edition pagination
- assets/styles.css — readable-width dark layout
- eleventy.config.js — data loading and template filters

No generated files are committed; GitHub Actions uploads the _site/ build artifact.

## Why a separate image-build trigger?

GitHub Actions updates made with the default GITHUB_TOKEN do not trigger subsequent push workflows. The static deployment workflow also listens for the completion of the OG image sync, so both the original news update and the enrichment update can be reflected in Pages.
