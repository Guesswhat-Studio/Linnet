import hashlib
import json
from pathlib import Path
from typing import Any

import trafilatura

_DEFAULT_HASHES_PATH = str(
    Path(__file__).parent.parent.parent / "docs" / "data" / "supervisor_hashes.json"
)


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_hashes(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write_hashes(path: str, hashes: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2)


def detect_changes(url: str, current_text: str, hashes_path: str = _DEFAULT_HASHES_PATH) -> bool:
    """Return True if the page content has changed since last check."""
    hashes = _load_hashes(hashes_path)
    current_hash = compute_hash(current_text)
    return hashes.get(url) != current_hash


def update_hashes(url: str, current_text: str, hashes_path: str = _DEFAULT_HASHES_PATH) -> None:
    hashes = _load_hashes(hashes_path)
    hashes[url] = compute_hash(current_text)
    _write_hashes(hashes_path, hashes)


def fetch_supervisor_updates(
    supervisors: list[dict],
    hashes_path: str = _DEFAULT_HASHES_PATH,
) -> list[dict[str, Any]]:
    """
    For each supervisor URL, fetch page text via trafilatura,
    compare hash, return list of changed entries.
    """
    updates = []
    hashes = _load_hashes(hashes_path)
    for sup in supervisors:
        url = sup["url"]
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            continue
        text = trafilatura.extract(downloaded) or ""
        if not text:
            continue
        current_hash = compute_hash(text)
        previous_hash = hashes.get(url)
        if previous_hash is None:
            hashes[url] = current_hash
            _write_hashes(hashes_path, hashes)
            continue
        if previous_hash != current_hash:
            hashes[url] = current_hash
            _write_hashes(hashes_path, hashes)
            updates.append(
                {
                    "name": sup.get("name", ""),
                    "institution": sup.get("institution", ""),
                    "url": url,
                    "page_text": text[:3000],  # cap for LLM context
                    "change_summary": "",  # filled by summarizer
                }
            )
    return updates
