# Contributing to Linnet

Contributions are welcome: bug fixes, new extensions, new sinks, setup polish,
docs, examples, and workflow recipes all help.

Linnet is built around one simple idea: if a useful source has a URL, RSS feed,
API, or scrapeable page, the community should be able to teach Linnet how to
turn it into a morning briefing section.

---

## Good First Contributions

Good starter contributions usually fit one of these shapes:

- Add a fixture-backed parser test for an existing extension.
- Add a small no-key extension backed by RSS, Atom, or a public JSON API.
- Improve an extension's `meta.json` so it is clearer in the setup wizard.
- Add a source preset to an existing extension.
- Improve docs for a setup path you actually tried.

If you have an idea but are not ready to code it, open a Discussion or an
extension request issue. See [`docs/extension-ideas.md`](docs/extension-ideas.md)
for source ideas and the information that makes an idea easy to pick up.

---

## Adding a New Extension

An extension is a self-contained data source. It owns its full pipeline:

```text
fetch() -> process() -> render() -> FeedSection
```

### 1. Copy the package template

```bash
cp -r extensions/_template extensions/my_source
```

Use a lowercase `snake_case` directory name. The directory name, Python class
`key`, `meta.json.key`, and `config/sources.yaml` key should all match.

### 2. Implement the extension

Open `extensions/my_source/__init__.py` and fill in:

- `fetch()` - pull raw data. Do not call an LLM here.
- `process()` - score, filter, or summarize. LLM calls are allowed here.
- `render()` - package items into a `FeedSection`. Do not do network work here.

Rules to preserve:

- Keep the extension self-contained.
- Read credentials from environment variables only.
- Respect `self.config.get("dry_run")` before any LLM call.
- Keep live-network behavior out of tests.

### 3. Fill in metadata for the setup wizard

Edit `extensions/my_source/meta.json`.

This metadata powers the Astro setup wizard and public extension registry:

- source picker title and description
- setup fields
- tags and category
- default layout hints

After editing metadata, refresh the generated registry:

```bash
cd astro
npm run sync:extension-meta
```

### 4. Register and configure it

Register the extension in `extensions/__init__.py`:

```python
from extensions.my_source import MySourceExtension

REGISTRY: list[type[BaseExtension]] = [
    ...,
    MySourceExtension,
]
```

Add a source block in `config/sources.yaml`:

```yaml
display_order:
  - my_source

my_source:
  enabled: false
  max_items: 10
```

If your extension needs filters, presets, or source-specific settings, add:

```yaml
# config/extensions/my_source.yaml
keywords:
  - AI
  - machine learning
```

`main.py` already merges `config/sources.yaml` with
`config/extensions/{name}.yaml` for every registered extension, so new
extensions do not need custom orchestrator wiring.

### 5. Add tests and docs

At minimum:

- Add `tests/test_my_source.py` with fixture-based parser/filter tests.
- Update `extensions/my_source/README.md`.
- Mention any required environment variables.
- Run the relevant checks before opening a PR.

Useful references:

- [`extensions/README.md`](extensions/README.md)
- [`extensions/_template/README.md`](extensions/_template/README.md)
- [`extensions/arxiv/README.md`](extensions/arxiv/README.md)

---

## Adding a New Sink

A sink receives the fully built payload and delivers it to another place, such
as Slack, ServerChan, email, Discord, or Telegram.

Create a package under `sinks/my_sink/`, subclass `BaseSink`, register it in
`sinks/__init__.py`, and add non-secret config under `sinks:` in
`config/sources.yaml`.

Credentials must stay in environment variables or GitHub Actions secrets:

```python
import os

from sinks.base import BaseSink


class MySink(BaseSink):
    key = "my_sink"

    def deliver(self, payload: dict) -> None:
        api_key = os.environ.get("MY_SINK_API_KEY", "")
        if not api_key:
            raise EnvironmentError("MY_SINK_API_KEY is not set")
        # send payload
```

Add the required secret to `.github/workflows/daily.yml` only as an environment
variable reference. Do not commit secret values.

---

## Development Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -q
```

Run the pipeline locally:

```bash
export OPENROUTER_API_KEY=sk-or-...
python main.py --mode daily
python main.py --dry-run
```

`--dry-run` fetches enabled sources but skips LLM calls, which is useful for
checking collectors without spending API credits.

---

## Pull Request Checklist

- [ ] One extension or sink per PR when possible.
- [ ] No credentials in YAML, docs, tests, or fixtures.
- [ ] `fetch()` has no LLM calls.
- [ ] `process()` respects `dry_run` before LLM calls.
- [ ] `render()` has no network calls.
- [ ] Tests use fixtures or monkeypatching instead of live APIs.
- [ ] Extension metadata is synced if `meta.json` changed.
- [ ] Relevant docs are updated.
- [ ] `PYTHONPATH=. pytest tests/ -q` passes, or the PR explains the narrower check used.
