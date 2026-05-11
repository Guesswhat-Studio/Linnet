# Extension Ideas and Community Board

Linnet grows best when people teach it new sources. A good extension is small,
useful, and easy to explain: "fetch this source, filter the noise, summarize the
items, and render a briefing section."

Use this page as a starting board for issues, Discussions, and first PRs.

---

## Good Extension Candidates

| Idea | Why it fits Linnet | Starter PR shape |
|---|---|---|
| Generic RSS / Atom | Lets users add newsletters, blogs, journals, and small sites without custom code | Feedparser-backed extension with `feeds: [{name, url}]` |
| RSSHub source | Opens many niche websites through one adapter | Configurable RSSHub base URL plus named routes |
| bioRxiv / medRxiv | Strong companion to arXiv for life-science users | Fetch recent preprints, keyword filter, summarize |
| Papers with Code | Turns model/dataset momentum into a briefing section | Fetch latest papers or trending methods |
| Product Hunt | Useful for builders tracking launches | Fetch daily products, summarize positioning |
| Grants and funding calls | High-value academic workflow | RSS/API/scraped source with deadlines and eligibility |
| Conference deadlines | Concrete recurring need for researchers | Static config plus remote deadline sources |
| Local events / meetups | Good personal briefing content | Public calendar/RSS parser |
| University or lab news | Useful for academic users | RSS or page monitor preset |
| Reddit / Hacker communities | Good for niche signal discovery | Configurable subreddit feed with score/comment thresholds |
| YouTube channels | Useful for talks, demos, and lectures | RSS feed parser with summaries |
| Email digest import | Turns existing newsletters into Linnet sections | Needs careful credential and privacy design |

---

## What to Include in an Extension Idea

When opening a Discussion or issue, include:

- Source URL or API docs.
- Whether it has RSS, Atom, JSON, or HTML only.
- Example items that should appear in the briefing.
- Desired output fields, such as `title`, `url`, `summary`, `deadline`.
- Whether it needs an API key.
- Any rate limits or usage rules you know about.
- Whether you can help test it with your own setup.

This makes the idea easy for another contributor to pick up.

---

## Suggested GitHub Labels

For maintainers, these labels make the extension board easier to navigate:

- `extension` - new or existing source plugin work.
- `sink` - delivery channel work.
- `good first issue` - small, fixture-backed, low-risk contributions.
- `help wanted` - useful but not currently owned by the maintainer.
- `needs API research` - requires checking source terms, endpoints, or limits.
- `docs` - documentation, examples, recipes.
- `setup wizard` - changes that affect onboarding or generated config.

---

## Suggested Discussion Categories

Discussions are better than issues for open-ended ideas and community examples.
Useful categories:

- `Show your briefing` - screenshots, sites, and configuration recipes.
- `Extension ideas` - source suggestions before they become scoped issues.
- `Recipes` - "how I configured Linnet for X" writeups.
- `Help / setup` - user questions that are not bugs.
- `Announcements` - release notes, roadmap updates, launch posts.

When an idea becomes concrete, convert it into an issue with a clear checklist.
