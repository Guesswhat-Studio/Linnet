import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import UTC, datetime, timedelta
from html import unescape
from typing import Any
from urllib.parse import urljoin

import arxiv
import httpx

_REPO = os.environ.get("GITHUB_REPOSITORY", "YuyangXueEd/Linnet")
_ARXIV_USER_AGENT = f"Linnet/1.0 (https://github.com/{_REPO})"
_OAIPMH_ENDPOINT = "https://oaipmh.arxiv.org/oai"
_OAIPMH_LOOKBACK_DAYS = 7
_XML_NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "arxiv": "http://arxiv.org/OAI/arXiv/",
}
_SELF_GROUP_ARCHIVES = {"cs", "econ", "eess", "math", "q-bio", "q-fin", "stat"}
_PHYSICS_ARCHIVES = {
    "astro-ph",
    "cond-mat",
    "gr-qc",
    "hep-ex",
    "hep-lat",
    "hep-ph",
    "hep-th",
    "math-ph",
    "nlin",
    "nucl-ex",
    "nucl-th",
    "physics",
    "quant-ph",
}


def keyword_match(text: str, keywords: list[str]) -> bool:
    """Return True if text contains at least one keyword (case-insensitive)."""
    lower = text.lower()
    return any(kw.lower() in lower for kw in keywords)


def _clean_metadata_text(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _clean_html_text(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


_GREEK_DUPLICATE_LATEX_RE = re.compile(
    r"(["
    r"\u0370-\u03FF"
    r"\u1F00-\u1FFF"
    r"](?:\s+[A-Za-z0-9]+)?)\s+(\\[A-Za-z]+(?:\s*(?:\{[^{}]*\}|_[{][^{}]*[}]|\^[{][^{}]*[}]|_[A-Za-z0-9]+|\^[A-Za-z0-9]+))*)"
)

_LATEX_EXPR_RE = re.compile(
    r"(?<!\\\()(?<!\\\[)"
    r"(\\[A-Za-z]+(?:\s*(?:\{[^{}]*\}|_[{][^{}]*[}]|\^[{][^{}]*[}]|_[A-Za-z0-9]+|\^[A-Za-z0-9]+))*)"
)


def _normalise_caption_math(text: str) -> str:
    """
    Convert arXiv's flattened math text into KaTeX-friendly inline math.

    After tags are stripped, captions often contain duplicated text such as
    ``ρ t \\rho_{t}`` or ``μ \\mu``. We drop the duplicated unicode prefix and
    wrap the remaining LaTeX command in ``\\( ... \\)`` so KaTeX can render it.
    """
    if "\\" not in text:
        return text

    text = _GREEK_DUPLICATE_LATEX_RE.sub(r"\2", text)
    text = _LATEX_EXPR_RE.sub(r"\\( \1 \\)", text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_first_figure(html: str, base_url: str) -> dict[str, str] | None:
    figures = re.findall(r"<figure\b[^>]*>(.*?)</figure>", html, re.DOTALL | re.IGNORECASE)
    for figure_html in figures:
        caption_match = re.search(
            r"<figcaption\b[^>]*>(.*?)</figcaption>", figure_html, re.DOTALL | re.IGNORECASE
        )
        if not caption_match:
            continue

        raw_caption = _clean_html_text(caption_match.group(1))
        if not re.search(r"\bFigure\s*1\b", raw_caption, re.IGNORECASE):
            continue

        image_match = re.search(r'<img\b[^>]*src="([^"]+)"', figure_html, re.IGNORECASE)
        if not image_match:
            continue

        caption = re.sub(r"^Figure\s*1\s*:\s*", "", raw_caption, flags=re.IGNORECASE).strip()
        caption = _normalise_caption_math(caption)
        return {
            "figure_url": urljoin(base_url, image_match.group(1)),
            "figure_caption": caption or raw_caption,
        }
    return None


def _parse_author_affiliations(html: str) -> list[str]:
    matches = re.findall(
        r"<meta[^>]+name=[\"']citation_author_institution[\"'][^>]+content=[\"']([^\"']+)[\"']",
        html,
        re.IGNORECASE,
    )
    cleaned = [_clean_html_text(m) for m in matches if m.strip()]
    seen: set[str] = set()
    deduped: list[str] = []
    for item in cleaned:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def enrich_paper_with_figure(
    paper: dict[str, Any],
    request_timeout: float = 20.0,
) -> dict[str, Any]:
    """Best-effort fetch of Figure 1 and author affiliations from arXiv pages."""
    paper_id = paper.get("id", "")
    if not paper_id:
        return paper

    headers = {"User-Agent": _ARXIV_USER_AGENT}

    html_url = f"https://arxiv.org/html/{paper_id}"
    try:
        response = httpx.get(html_url, timeout=request_timeout, headers=headers)
        response.raise_for_status()
        figure = _parse_first_figure(response.text, html_url)
        if figure:
            paper.update(figure)
    except Exception:
        pass

    abs_url = f"https://arxiv.org/abs/{paper_id}"
    try:
        abs_response = httpx.get(abs_url, timeout=request_timeout, headers=headers)
        abs_response.raise_for_status()
        affiliations = _parse_author_affiliations(abs_response.text)
        if affiliations:
            paper["affiliations"] = affiliations
    except Exception:
        pass

    return paper


def enrich_papers_with_figures(
    papers: list[dict[str, Any]],
    request_timeout: float = 20.0,
) -> list[dict[str, Any]]:
    return [enrich_paper_with_figure(paper, request_timeout=request_timeout) for paper in papers]


def _arxiv_category_to_oai_set(category: str) -> str:
    """Map an arXiv category like cs.AI to its OAI-PMH setSpec."""
    category = category.strip()
    archive, separator, subject = category.partition(".")
    if not separator:
        if archive in _PHYSICS_ARCHIVES and archive != "physics":
            return f"physics:{archive}"
        return archive

    if archive in _SELF_GROUP_ARCHIVES:
        group = archive
    elif archive in _PHYSICS_ARCHIVES:
        group = "physics"
    else:
        group = archive

    return f"{group}:{archive}:{subject}"


def _oaipmh_from_date() -> str:
    return (datetime.now(UTC) - timedelta(days=_OAIPMH_LOOKBACK_DAYS)).date().isoformat()


def _xml_text(parent: ET.Element, path: str) -> str:
    node = parent.find(path, _XML_NS)
    return _clean_metadata_text(node.text if node is not None else None)


def _parse_oaipmh_author(author: ET.Element) -> str:
    keyname = _xml_text(author, "arxiv:keyname")
    forenames = _xml_text(author, "arxiv:forenames")
    suffix = _xml_text(author, "arxiv:suffix")
    name = " ".join(part for part in [forenames, keyname, suffix] if part)
    return name or _clean_metadata_text(" ".join(author.itertext()))


def _parse_oaipmh_records(
    xml_text: str,
    must_include: list[str],
    max_authors: int,
    created_since: str | None = None,
) -> tuple[list[dict[str, Any]], str | None]:
    root = ET.fromstring(xml_text)
    error = root.find("oai:error", _XML_NS)
    if error is not None:
        code = error.attrib.get("code", "")
        if code == "noRecordsMatch":
            return [], None
        message = _clean_metadata_text(error.text)
        raise ValueError(f"OAI-PMH error {code}: {message}")

    papers: list[dict[str, Any]] = []
    for record in root.findall(".//oai:record", _XML_NS):
        metadata = record.find("oai:metadata", _XML_NS)
        if metadata is None:
            continue

        arxiv_meta = metadata.find("arxiv:arXiv", _XML_NS)
        if arxiv_meta is None:
            children = list(metadata)
            arxiv_meta = children[0] if children else None
        if arxiv_meta is None:
            continue

        paper_id = _xml_text(arxiv_meta, "arxiv:id")
        created = _xml_text(arxiv_meta, "arxiv:created")
        title = _xml_text(arxiv_meta, "arxiv:title")
        abstract = _xml_text(arxiv_meta, "arxiv:abstract")
        categories = _xml_text(arxiv_meta, "arxiv:categories").split()
        if not paper_id or not title:
            continue
        if created_since and created and created < created_since:
            continue

        combined = f"{title} {abstract}"
        if not keyword_match(combined, must_include):
            continue

        authors = [
            name
            for name in (
                _parse_oaipmh_author(author)
                for author in arxiv_meta.findall("arxiv:authors/arxiv:author", _XML_NS)
            )
            if name
        ]
        papers.append(
            {
                "id": paper_id,
                "title": title,
                "authors": authors[:max_authors],
                "categories": categories,
                "abstract": abstract,
                "url": f"https://arxiv.org/abs/{paper_id}",
                "pdf_url": f"https://arxiv.org/pdf/{paper_id}",
            }
        )

    token_node = root.find(".//oai:resumptionToken", _XML_NS)
    token = _clean_metadata_text(token_node.text if token_node is not None else None) or None
    return papers, token


def _fetch_papers_from_search_api(
    categories: list[str],
    must_include: list[str],
    max_results: int = 100,
    max_authors: int = 5,
    api_retries: int = 5,
    api_delay: float = 10.0,
) -> list[dict[str, Any]]:
    query = " OR ".join(f"cat:{cat}" for cat in categories)
    client = arxiv.Client(num_retries=api_retries, delay_seconds=api_delay)
    client._session.headers.update({"User-Agent": _ARXIV_USER_AGENT})
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    papers = []
    for result in client.results(search):
        combined = f"{result.title} {result.summary}"
        if not keyword_match(combined, must_include):
            continue
        papers.append(
            {
                "id": result.entry_id.split("/abs/")[-1],
                "title": result.title,
                "authors": [a.name for a in result.authors[:max_authors]],
                "categories": list(result.categories),
                "abstract": result.summary,
                "url": result.entry_id,
                "pdf_url": result.pdf_url,
            }
        )

    return papers


def _fetch_papers_from_oaipmh(
    categories: list[str],
    must_include: list[str],
    max_results: int = 100,
    max_authors: int = 5,
    api_delay: float = 10.0,
    request_timeout: float = 30.0,
) -> list[dict[str, Any]]:
    if not categories or max_results == 0:
        return []

    papers: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    from_date = _oaipmh_from_date()
    last_request_at = 0.0

    def wait_for_slot() -> None:
        nonlocal last_request_at
        if last_request_at:
            elapsed = time.monotonic() - last_request_at
            if elapsed < api_delay:
                time.sleep(api_delay - elapsed)
        last_request_at = time.monotonic()

    for category in categories:
        token: str | None = None
        while len(papers) < max_results:
            wait_for_slot()
            params = (
                {"verb": "ListRecords", "resumptionToken": token}
                if token
                else {
                    "verb": "ListRecords",
                    "metadataPrefix": "arXiv",
                    "set": _arxiv_category_to_oai_set(category),
                    "from": from_date,
                }
            )
            response = httpx.get(
                _OAIPMH_ENDPOINT,
                params=params,
                timeout=request_timeout,
                headers={"User-Agent": _ARXIV_USER_AGENT},
            )
            response.raise_for_status()

            batch, token = _parse_oaipmh_records(
                response.text,
                must_include=must_include,
                max_authors=max_authors,
                created_since=from_date,
            )
            for paper in batch:
                if paper["id"] in seen_ids:
                    continue
                seen_ids.add(paper["id"])
                papers.append(paper)
                if len(papers) >= max_results:
                    break

            if not token:
                break

    return papers[:max_results]


def fetch_papers(
    categories: list[str],
    must_include: list[str],
    max_results: int = 100,
    max_authors: int = 5,
    api_retries: int = 5,
    api_delay: float = 10.0,
) -> list[dict[str, Any]]:
    """
    Fetch recent papers from arxiv for given categories,
    pre-filter by must_include keywords on title+abstract.
    Returns list of paper dicts ready for LLM scoring.
    """
    if max_results == 0:
        return []

    try:
        return _fetch_papers_from_search_api(
            categories=categories,
            must_include=must_include,
            max_results=max_results,
            max_authors=max_authors,
            api_retries=api_retries,
            api_delay=api_delay,
        )
    except arxiv.ArxivError as exc:
        print(f"  arXiv search API failed ({exc}); trying OAI-PMH metadata fallback...")

    try:
        return _fetch_papers_from_oaipmh(
            categories=categories,
            must_include=must_include,
            max_results=max_results,
            max_authors=max_authors,
            api_delay=api_delay,
        )
    except (httpx.HTTPError, ET.ParseError, ValueError) as exc:
        print(f"  OAI-PMH fallback failed: {exc}")
        return []
