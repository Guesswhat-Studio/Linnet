# Manual Configuration Guide

> 🌐 **Language / 语言**: **English** · [中文](manual-config.zh.md)

Prefer to configure everything by hand? This page walks through every step.
If you'd rather use the interactive wizard, use the [upstream setup wizard](https://yuyangxueed.github.io/Linnet/setup/) instead.

---

## Step 1 — Create your own repo from this template

Prefer **Use this template → Create a new repository** on the [GitHub page](https://github.com/YuyangXueEd/Linnet).
That gives you your own copy with all the automation included, without the extra Actions friction that forks often add.

If you intentionally need an upstream-linked development copy, you can still use **Fork**, but this manual guide assumes you are creating your own standalone digest repo.

### Optional: one-click deploy via the Setup Wizard

The recommended one-click path no longer uses a PAT. Instead:

1. install the **Linnet Bridge** GitHub App on your target repo
2. open the upstream setup wizard at <https://yuyangxueed.github.io/Linnet/setup/>
3. click **Install GitHub App** / **Authorize GitHub**
4. deploy from Step 5

This manual guide remains the fallback path when you want to keep every config change explicit, or when org / repo policy blocks the GitHub App flow.

---

## Step 2 — Add your API key

In your repo go to: **Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|---|---|
| `OPENROUTER_API_KEY` | Your key from [openrouter.ai/keys](https://openrouter.ai/keys) — free tier works, starts with `sk-or-...` |

This is the default fast-path credential. [OpenRouter](https://openrouter.ai) lets you call many AI models
(Gemini, GPT, Claude) with one key and switch between them any time.

> 💰 **Cost estimate**: With the default model (`google/gemini-2.5-flash-lite`), **one full daily digest run costs roughly $0.1 USD**. At one run per day, that's **under $3 USD / month**. Actual spend varies with the sources you enable, how many papers get fetched, and the summary language — you can watch per-call costs live on the [OpenRouter dashboard](https://openrouter.ai/activity). If you want to spend less, swap `scoring_model` / `summarization_model` in `config/sources.yaml` for a cheaper model, or lower the daily paper cap in `config/extensions/arxiv.yaml`.

If you prefer a different OpenAI-compatible provider, set these fields in [`config/sources.yaml`](../config/sources.yaml):

```yaml
llm:
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  api_key_env: "OPENAI_API_KEY"
  scoring_model: "gpt-5-mini"
  summarization_model: "gpt-5-mini"
```

Then export or store the matching secret name instead:

```bash
export OPENAI_API_KEY=sk-...
```

---

## Step 3 — Enable GitHub Pages

Go to: **Settings → Pages → Source: GitHub Actions**

Click **Save**. Your site URL will appear there — it looks like `https://YOUR-USERNAME.github.io/Linnet`.

---

## Step 4 — Pick your research topics

Open [`config/extensions/arxiv.yaml`](../config/extensions/arxiv.yaml). It has four ready-made profiles —
uncomment the one closest to your work and edit the keywords freely:

```yaml
# PROFILE A: AI / ML / LLM (general)
# categories: [cs.AI, cs.LG, cs.CL, cs.CV, stat.ML]
# must_include:
#   - large language model
#   - foundation model

# PROFILE B: Astrophysics / Space Science
# PROFILE C: Chemistry / Materials Science
# PROFILE D: Computational Biology / Bioinformatics
```

Want summaries in a different language? Open [`config/sources.yaml`](../config/sources.yaml) and
change `language: "en"` to `"zh"`, `"fr"`, `"de"`, `"ja"`, `"ko"`, `"es"`, or any other language code.

---

## Step 5 — Run it for the first time

If GitHub Actions / workflows are currently disabled in the repo, enable them manually first unless you already used the Setup Wizard’s Step 5 auto-enable option successfully. This is most common on forks.

Clean start for older forks: delete any inherited generated snapshots under `docs/data/daily/*.json`, `docs/data/weekly/*.json`, and `docs/data/monthly/*.json`, but keep the `.gitkeep` files. The next `Daily Digest` run will create fresh data for your repo.

You need to manually trigger **two** workflows in order:

1. **Generate the digest content**: Go to **Actions → Daily Digest → Run workflow → Run workflow** and wait for it to finish (about 3–5 minutes). This calls the LLM, builds today's digest, and commits it into `docs/`.
2. **Deploy the site to GitHub Pages**: Go to **Actions → Deploy Astro Site to GitHub Pages → Run workflow → Run workflow** and wait for it to finish (about 1–2 minutes). This builds the Astro site and publishes it.

> 💡 From then on, `Daily Digest` runs automatically every day and auto-triggers the deploy on success — so you only need to click these two buttons **the first time**.

Once both are green, your site is live at `https://<your-username>.github.io/<repo-name>/`.

Optional but recommended: paste that URL into the repository's **About -> Website** field so the site link also appears on the GitHub repo home page.

---

## Turn sources on and off

Open [`config/sources.yaml`](../config/sources.yaml) and set `enabled: true` or `enabled: false`
for each source:

```yaml
arxiv:
  enabled: true          # arXiv papers — the main event

hacker_news:
  enabled: true          # top Hacker News stories

github_trending:
  enabled: true          # today's trending GitHub repos
  max_repos: 15

weather:
  enabled: true
  city: "Edinburgh"      # change to your city

postdoc_jobs:
  enabled: false         # academic job listings — turn on if you want these

supervisor_updates:
  enabled: false         # professor/lab page monitor — turn on if you want these

quote_of_day:
  enabled: false         # daily quote as briefing tagline (English, requires API_NINJAS_KEY)

hitokoto:
  enabled: false         # 一言 daily quote as briefing tagline (Chinese, no key needed)
```

You can also switch AI models here, set `llm.provider`, point `llm.base_url` at another OpenAI-compatible provider, change `llm.api_key_env`, or cap how many papers get fetched per day.

---

## Customise LLM prompts

Every summarisation and scoring prompt can be overridden in `config/sources.yaml` under the `llm.prompts:` block.
The commented-out defaults are already in that file — uncomment and edit any you want to change:

```yaml
llm:
  summarization_model: "google/gemini-2.5-flash-lite"
  # prompts:
  #   arxiv_summary: |
  #     Summarize the core method and contribution of the following paper
  #     {lang}, in 2-3 sentences (≤100 words):
  #     Title: {title}
  #     Abstract: {abstract}
  #   hacker_news_summary: |
  #     Summarize the core content of the following tech news story
  #     {lang}, in one sentence (≤50 words):
  #     Title: {title}
  #     URL: {url}
```

Available placeholders per prompt:

| Prompt key | Placeholders |
|---|---|
| `arxiv_score` | `{title}`, `{abstract}` |
| `arxiv_summary` | `{title}`, `{abstract}`, `{lang}` |
| `hacker_news_summary` | `{title}`, `{url}`, `{lang}` |
| `github_summary` | `{full_name}`, `{description}`, `{lang}` |

---

## Get your digest in ServerChan

If you want a lighter notification path, especially for Chinese-language workflows, ServerChan is a good fit:

1. Open [sct.ftqq.com/sendkey](https://sct.ftqq.com/sendkey)
2. Copy your SendKey
3. Add it as a secret: **Settings → Secrets and variables → Actions → New repository secret**, name it `SERVERCHAN_SENDKEY`
4. Enable it in [`config/sources.yaml`](../config/sources.yaml):

```yaml
sinks:
  serverchan:
    enabled: true
    max_papers: 5
    max_hn: 3
    max_github: 3
    max_jobs: 3
```

This keeps the key out of YAML and out of version control.

---

## Get your digest in Slack

In addition to the website, you can receive a daily Slack message:

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Left sidebar → **Features → Incoming Webhooks** → toggle **On**
3. Scroll down → **Add New Webhook to Workspace** → choose your channel → **Allow**
4. Copy the webhook URL (looks like `https://hooks.slack.com/services/T.../B.../...`)
5. Add it as a secret: **Settings → Secrets and variables → Actions → New repository secret**, name it `SLACK_WEBHOOK_URL`
6. Enable it in [`config/sources.yaml`](../config/sources.yaml):

```yaml
sinks:
  slack:
    enabled: true
    max_papers: 5    # how many papers to include
    max_hn: 3        # how many HN stories to include
    max_github: 3    # how many trending repos to include
```

If you skip this step, nothing breaks — the website still updates as normal.

---

## What runs automatically

| When | What happens |
|---|---|
| Weekdays at 09:30 UTC | Full digest — papers, HN, GitHub trending, weather, US pre-market stocks, any extras you enabled |
| Every Monday at 1 AM UTC | Weekly summary of the past week |
| 1st of every month at 2 AM UTC | Monthly overview |

You can also trigger any of these by hand: **Actions → [workflow name] → Run workflow**.
