import json

from extensions.supervisor_updates.collector import (
    compute_hash,
    detect_changes,
    fetch_supervisor_updates,
    update_hashes,
)


def test_compute_hash_is_deterministic():
    text = "Prof. Smith is hiring postdocs in medical imaging."
    assert compute_hash(text) == compute_hash(text)


def test_compute_hash_differs_for_different_text():
    h1 = compute_hash("We have an open postdoc position in CV.")
    h2 = compute_hash("No positions available at this time.")
    assert h1 != h2


def test_detect_changes_new_url(tmp_path):
    hashes_file = tmp_path / "supervisor_hashes.json"
    hashes_file.write_text("{}")
    changed = detect_changes(
        url="https://example.com/lab",
        current_text="We are hiring a postdoc in AI.",
        hashes_path=str(hashes_file),
    )
    assert changed is True


def test_detect_changes_same_content(tmp_path):
    text = "No current openings."
    h = compute_hash(text)
    hashes_file = tmp_path / "supervisor_hashes.json"
    hashes_file.write_text(json.dumps({"https://example.com/lab": h}))
    changed = detect_changes(
        url="https://example.com/lab",
        current_text=text,
        hashes_path=str(hashes_file),
    )
    assert changed is False


def test_update_hashes_persists(tmp_path):
    hashes_file = tmp_path / "supervisor_hashes.json"
    hashes_file.write_text("{}")
    test_url = "https://example.com/lab"
    update_hashes(test_url, "new content", str(hashes_file))
    hashes = json.loads(hashes_file.read_text())
    # Use .get() to avoid triggering substring-check alerts on the URL string
    assert hashes.get(test_url) is not None


def test_update_hashes_creates_parent_dir(tmp_path):
    hashes_file = tmp_path / "nested" / "supervisor_hashes.json"
    test_url = "https://example.com/lab"

    update_hashes(test_url, "new content", str(hashes_file))

    hashes = json.loads(hashes_file.read_text())
    assert hashes.get(test_url) == compute_hash("new content")


def test_fetch_supervisor_updates_initializes_baseline_without_emitting(monkeypatch, tmp_path):
    hashes_file = tmp_path / "supervisor_hashes.json"

    monkeypatch.setattr(
        "extensions.supervisor_updates.collector.trafilatura.fetch_url",
        lambda url: "<html>initial page</html>",
    )
    monkeypatch.setattr(
        "extensions.supervisor_updates.collector.trafilatura.extract",
        lambda downloaded: "Initial page content",
    )

    updates = fetch_supervisor_updates(
        [{"name": "Ada", "institution": "Example University", "url": "https://example.com/lab"}],
        hashes_path=str(hashes_file),
    )

    assert updates == []
    hashes = json.loads(hashes_file.read_text())
    assert hashes.get("https://example.com/lab") == compute_hash("Initial page content")


def test_fetch_supervisor_updates_returns_later_changes(monkeypatch, tmp_path):
    hashes_file = tmp_path / "supervisor_hashes.json"
    page = {"text": "Initial page content"}

    monkeypatch.setattr(
        "extensions.supervisor_updates.collector.trafilatura.fetch_url",
        lambda url: "<html>page</html>",
    )
    monkeypatch.setattr(
        "extensions.supervisor_updates.collector.trafilatura.extract",
        lambda downloaded: page["text"],
    )

    supervisors = [
        {"name": "Ada", "institution": "Example University", "url": "https://example.com/lab"}
    ]
    assert fetch_supervisor_updates(supervisors, hashes_path=str(hashes_file)) == []

    page["text"] = "Updated page content with a new PhD opening."
    updates = fetch_supervisor_updates(supervisors, hashes_path=str(hashes_file))

    assert updates == [
        {
            "name": "Ada",
            "institution": "Example University",
            "url": "https://example.com/lab",
            "page_text": "Updated page content with a new PhD opening.",
            "change_summary": "",
        }
    ]
