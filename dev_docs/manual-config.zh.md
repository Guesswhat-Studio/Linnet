# 手动配置指南

> 🌐 **Language / 语言**: **中文** · [English](manual-config.md)

想要完全手动配置每一项？这篇文档会带你走完全部步骤。
如果你更想用交互式向导，直接使用上游的 [Setup Wizard（中文设置向导）](https://yuyangxueed.github.io/Linnet/setup/zh/) 即可。

---

## Step 1 — 用模板创建你自己的仓库

优先在 [GitHub 项目页面](https://github.com/YuyangXueEd/Linnet) 上使用 **Use this template → Create a new repository**。
这样你会得到一份带完整自动化流程的独立仓库，也更少遇到 fork 带来的 Actions 限制。

如果你确实需要保留和上游的 fork 关系，当然也可以继续使用 **Fork**；但这份手动指南默认你是在创建自己的独立 digest 仓库。

### 可选：通过设置向导一键部署

推荐的一键部署路径已经不再使用 PAT。现在的方式是：

1. 把 **Linnet Bridge** GitHub App 安装到目标仓库
2. 打开上游设置向导：<https://yuyangxueed.github.io/Linnet/setup/zh/>
3. 点击 **安装 GitHub App** / **授权 GitHub**
4. 在 Step 5 里直接部署

这份手动指南保留给两种情况：你想完全自己掌控每一步配置，或者组织 / 仓库策略阻止了 GitHub App 流程。

---

## Step 2 — 添加你的 API Key

在你的仓库里，进入：**Settings → Secrets and variables → Actions → New repository secret**

| 名称（Name） | 值（Value） |
|---|---|
| `OPENROUTER_API_KEY` | 从 [openrouter.ai/keys](https://openrouter.ai/keys) 获取的 key —— 免费额度即可使用，格式以 `sk-or-...` 开头 |

这是默认的快速上手凭据。[OpenRouter](https://openrouter.ai) 允许你用同一个 key 调用多种 AI 模型（Gemini、GPT、Claude 等），并可随时在它们之间切换。

> 💰 **成本预估**：使用默认模型（`google/gemini-2.5-flash-lite`），**跑一次完整日报大约花费 $0.1 USD**。按每天自动跑一次算，一个月总成本 **不到 $3 USD**（约 ¥20）。实际花费会随你启用的数据源、论文数量、摘要语言而浮动，可以在 [OpenRouter 控制台](https://openrouter.ai/activity) 里实时查看每次调用的开销。如果预算更紧，可以在 `config/sources.yaml` 里把 `scoring_model` / `summarization_model` 换成更便宜的模型，或在 `config/extensions/arxiv.yaml` 里降低每天抓取的论文上限。

如果你想用其他兼容 OpenAI 协议的 provider（服务商），请修改 [`config/sources.yaml`](../config/sources.yaml) 里的这几项：

```yaml
llm:
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  api_key_env: "OPENAI_API_KEY"
  scoring_model: "gpt-5-mini"
  summarization_model: "gpt-5-mini"
```

然后在 GitHub Secrets 中用对应的环境变量名保存密钥，例如：

```bash
export OPENAI_API_KEY=sk-...
```

---

## Step 3 — 启用 GitHub Pages

进入：**Settings → Pages → Source: GitHub Actions**

点击 **Save** 保存。你的站点 URL 会显示在那里，格式类似 `https://YOUR-USERNAME.github.io/Linnet`。

---

## Step 4 — 选择你的研究主题

打开 [`config/extensions/arxiv.yaml`](../config/extensions/arxiv.yaml)。里面内置了四个现成的 profile（主题模板）——
取消掉最贴近你工作领域的那一段的注释，然后自由修改关键词：

```yaml
# PROFILE A: AI / ML / LLM (general)   —— 人工智能 / 机器学习 / 大模型（通用）
# categories: [cs.AI, cs.LG, cs.CL, cs.CV, stat.ML]
# must_include:
#   - large language model
#   - foundation model

# PROFILE B: Astrophysics / Space Science        —— 天体物理 / 空间科学
# PROFILE C: Chemistry / Materials Science        —— 化学 / 材料科学
# PROFILE D: Computational Biology / Bioinformatics —— 计算生物 / 生物信息
```

想要其他语言的摘要？打开 [`config/sources.yaml`](../config/sources.yaml)，
把 `language: "en"` 改成 `"zh"`（中文）、`"fr"`、`"de"`、`"ja"`、`"ko"`、`"es"` 或任何其他语言代码即可。

---

## Step 5 — 首次运行

如果仓库里的 GitHub Actions / workflows 当前仍处于禁用状态，而你又没有成功使用设置向导 Step 5 的自动启用功能，请先在仓库里手动启用它们。这种情况最常见于 fork。

旧 fork 的干净起步方式：删除继承来的 `docs/data/daily/*.json`、`docs/data/weekly/*.json` 和 `docs/data/monthly/*.json`，但保留 `.gitkeep` 文件。下一次 `Daily Digest` 会为你的仓库生成全新的数据。

需要**依次**手动触发两个 workflow：

1. **生成简报内容**：进入 **Actions → Daily Digest → Run workflow → Run workflow**，等它跑完（大约 3–5 分钟）。这一步会调用 LLM 生成当天的日报并提交到 `docs/` 目录。
2. **部署站点到 GitHub Pages**：进入 **Actions → Deploy Astro Site to GitHub Pages → Run workflow → Run workflow**，等它跑完（大约 1–2 分钟）。这一步会把 Astro 站点构建好并发布出去。

> 💡 之后每天 `Daily Digest` 会自动跑，并在成功后自动触发部署，所以**只有第一次**需要你手动点这两下。

全部完成后，打开 `https://<你的用户名>.github.io/<仓库名>/` 就能看到你的站点。

可选但很推荐：把这个地址填到仓库主页的 **About -> Website** 里，这样 GitHub 仓库首页也会直接显示站点入口。

---

## 开关各个数据源（sources）

打开 [`config/sources.yaml`](../config/sources.yaml)，为每个 source 设置 `enabled: true` 或 `enabled: false`：

```yaml
arxiv:
  enabled: true          # arXiv 论文 —— 主角

hacker_news:
  enabled: true          # Hacker News 热门帖

github_trending:
  enabled: true          # 今日 GitHub trending 仓库
  max_repos: 15

weather:
  enabled: true
  city: "Edinburgh"      # 改成你所在的城市

postdoc_jobs:
  enabled: false         # 学术岗位招聘信息 —— 按需开启

supervisor_updates:
  enabled: false         # 教授/实验室主页监控 —— 按需开启

quote_of_day:
  enabled: false         # 每日一句英文名言，用作简报标语（需要 API_NINJAS_KEY）

hitokoto:
  enabled: false         # 一言 · 每日中文金句作为简报标语（无需 key）
```

你同样可以在这里切换 AI 模型：调整 `llm.provider`、把 `llm.base_url` 指向其他兼容 OpenAI 的服务商、修改 `llm.api_key_env`，或设置每天抓取论文的数量上限。

---

## 自定义 LLM 提示词（Prompts）

所有总结（summarisation）和打分（scoring）的 prompt 都可以在 `config/sources.yaml` 的 `llm.prompts:` 块中覆盖。
默认的 prompt 已经以注释形式放在文件里了 —— 取消注释并按需修改即可：

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

每个 prompt 可用的占位符（placeholders）：

| Prompt key | 可用占位符 |
|---|---|
| `arxiv_score` | `{title}`, `{abstract}` |
| `arxiv_summary` | `{title}`, `{abstract}`, `{lang}` |
| `hacker_news_summary` | `{title}`, `{url}`, `{lang}` |
| `github_summary` | `{full_name}`, `{description}`, `{lang}` |

---

## 把简报推送到微信（Server 酱 / ServerChan）

[Server 酱](https://sct.ftqq.com/) 是一个**把文本消息推送到微信**的免费服务 —— 启用之后，每天的简报会通过它的官方公众号 **"Server 酱 · Turbo"** 直接推送到你的微信里，点开消息里的链接就能跳转到完整日报。**在国内使用、无需翻墙、不用装额外 App**，比 Slack 更适合中文用户。

配置步骤：

1. 打开 [sct.ftqq.com/sendkey](https://sct.ftqq.com/sendkey)，用微信扫码登录
2. **按页面提示关注 "Server 酱 · Turbo" 微信公众号**（这一步必须做，否则收不到推送），然后复制你的 SendKey
3. 把它添加为仓库 secret：**Settings → Secrets and variables → Actions → New repository secret**，命名为 `SERVERCHAN_SENDKEY`
4. 在 [`config/sources.yaml`](../config/sources.yaml) 中启用它：

```yaml
sinks:
  serverchan:
    enabled: true
    max_papers: 5
    max_hn: 3
    max_github: 3
    max_jobs: 3
```

这样 key 不会进入 YAML 文件，也不会被提交到版本库。

---

## 把简报推送到 Slack

除了网站，你还可以每天收到一条 Slack 消息：

1. 进入 [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. 左侧栏 → **Features → Incoming Webhooks** → 开关切到 **On**
3. 往下滚 → **Add New Webhook to Workspace** → 选择你要接收消息的频道 → **Allow**
4. 复制 webhook URL（格式类似 `https://hooks.slack.com/services/T.../B.../...`）
5. 把它添加为仓库 secret：**Settings → Secrets and variables → Actions → New repository secret**，命名为 `SLACK_WEBHOOK_URL`
6. 在 [`config/sources.yaml`](../config/sources.yaml) 中启用它：

```yaml
sinks:
  slack:
    enabled: true
    max_papers: 5    # 包含多少篇论文
    max_hn: 3        # 包含多少条 HN 帖子
    max_github: 3    # 包含多少个 trending 仓库
```

如果你跳过这一步，也不会有任何报错 —— 网站仍会正常更新。

---

## 自动运行的定时任务

| 触发时间 | 执行内容 |
|---|---|
| 默认工作日 UTC 09:30（北京时间 17:30） | 完整日报 —— 论文、HN、GitHub trending、天气、美股盘前信号，以及你启用的其他扩展 |
| 每周一 UTC 00:00（北京时间早 8 点） | 过去一周的周报汇总 |
| 每月 1 号 UTC 00:00（北京时间早 8 点） | 月度综览 |

设置向导可以根据你的本地时间和 UTC offset，在 `.github/workflows/daily.yml` 里生成自定义日报时间。你也可以手动改 workflow 里的 cron，或者手动触发这些任务：**Actions -> [对应 workflow 名称] -> Run workflow**。
