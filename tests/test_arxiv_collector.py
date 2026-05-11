import arxiv

from extensions.arxiv import collector
from extensions.arxiv.collector import (
    _arxiv_category_to_oai_set,
    _normalise_caption_math,
    _parse_first_figure,
    _parse_oaipmh_records,
    fetch_papers,
    keyword_match,
)


def test_keyword_match_positive():
    text = "A foundation model for medical image segmentation using MRI and CT scans"
    must_include = ["medical image", "MRI", "CT scan", "segmentation"]
    assert keyword_match(text, must_include) is True


def test_keyword_match_negative():
    text = "A graph neural network for protein folding prediction"
    must_include = ["medical image", "MRI", "CT scan", "segmentation"]
    assert keyword_match(text, must_include) is False


def test_keyword_match_case_insensitive():
    text = "MEDICAL IMAGING with Diffusion Models"
    must_include = ["medical imaging"]
    assert keyword_match(text, must_include) is True


def test_fetch_papers_returns_list():
    """fetch_papers with zero max_results returns empty list without hitting network."""
    results = fetch_papers(categories=["cs.CV"], must_include=["medical"], max_results=0)
    assert isinstance(results, list)


def test_arxiv_category_to_oai_set_maps_common_categories():
    assert _arxiv_category_to_oai_set("cs.AI") == "cs:cs:AI"
    assert _arxiv_category_to_oai_set("stat.ML") == "stat:stat:ML"
    assert _arxiv_category_to_oai_set("astro-ph.GA") == "physics:astro-ph:GA"
    assert _arxiv_category_to_oai_set("cs") == "cs"


def test_parse_oaipmh_records_extracts_matching_papers():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
             xmlns:arxiv="http://arxiv.org/OAI/arXiv/">
      <ListRecords>
        <record>
          <header>
            <identifier>oai:arXiv.org:2605.12345</identifier>
            <datestamp>2026-05-11</datestamp>
            <setSpec>cs:cs:AI</setSpec>
          </header>
          <metadata>
            <arxiv:arXiv>
              <arxiv:id>2605.12345</arxiv:id>
              <arxiv:created>2026-05-11</arxiv:created>
              <arxiv:authors>
                <arxiv:author>
                  <arxiv:keyname>Doe</arxiv:keyname>
                  <arxiv:forenames>Jane</arxiv:forenames>
                </arxiv:author>
                <arxiv:author>
                  <arxiv:keyname>Smith</arxiv:keyname>
                  <arxiv:forenames>Alex</arxiv:forenames>
                </arxiv:author>
              </arxiv:authors>
              <arxiv:title>Agentic foundation models for science</arxiv:title>
              <arxiv:categories>cs.AI cs.LG</arxiv:categories>
              <arxiv:abstract>
                We study a large language model agent for scientific discovery.
              </arxiv:abstract>
            </arxiv:arXiv>
          </metadata>
        </record>
        <record>
          <metadata>
            <arxiv:arXiv>
              <arxiv:id>2505.11111</arxiv:id>
              <arxiv:created>2025-05-11</arxiv:created>
              <arxiv:authors />
              <arxiv:title>Old large language model metadata update</arxiv:title>
              <arxiv:categories>cs.AI</arxiv:categories>
              <arxiv:abstract>
                This older paper matches the keyword but should be ignored by created date.
              </arxiv:abstract>
            </arxiv:arXiv>
          </metadata>
        </record>
        <record>
          <metadata>
            <arxiv:arXiv>
              <arxiv:id>2605.54321</arxiv:id>
              <arxiv:created>2026-05-11</arxiv:created>
              <arxiv:authors />
              <arxiv:title>A theorem about lattices</arxiv:title>
              <arxiv:categories>math.CO</arxiv:categories>
              <arxiv:abstract>No configured keyword appears here.</arxiv:abstract>
            </arxiv:arXiv>
          </metadata>
        </record>
        <resumptionToken>next-page-token</resumptionToken>
      </ListRecords>
    </OAI-PMH>
    """

    papers, token = _parse_oaipmh_records(
        xml,
        must_include=["large language model"],
        max_authors=1,
        created_since="2026-05-10",
    )

    assert token == "next-page-token"
    assert papers == [
        {
            "id": "2605.12345",
            "title": "Agentic foundation models for science",
            "authors": ["Jane Doe"],
            "categories": ["cs.AI", "cs.LG"],
            "abstract": "We study a large language model agent for scientific discovery.",
            "url": "https://arxiv.org/abs/2605.12345",
            "pdf_url": "https://arxiv.org/pdf/2605.12345",
        }
    ]


def test_fetch_papers_falls_back_to_oaipmh(monkeypatch):
    expected = [{"id": "2605.12345", "title": "Fallback paper"}]

    def fail_search_api(**kwargs):
        raise arxiv.HTTPError("https://export.arxiv.org/api/query", 5, 429)

    def use_oaipmh(**kwargs):
        return expected

    monkeypatch.setattr(collector, "_fetch_papers_from_search_api", fail_search_api)
    monkeypatch.setattr(collector, "_fetch_papers_from_oaipmh", use_oaipmh)

    results = fetch_papers(categories=["cs.AI"], must_include=["agent"], max_results=10)

    assert results == expected


def test_parse_first_figure_extracts_url_and_caption():
    html = """
        <section>
            <figure id="S3.F1" class="ltx_figure">
                <img src="2604.12345v1/Figures/figure1.png" alt="Refer to caption">
                <figcaption class="ltx_caption ltx_centering"><span class="ltx_tag ltx_tag_figure">Figure 1: </span>A test architecture overview.</figcaption>
            </figure>
        </section>
        """

    figure = _parse_first_figure(html, "https://arxiv.org/html/2604.12345")

    assert figure == {
        "figure_url": "https://arxiv.org/html/2604.12345v1/Figures/figure1.png",
        "figure_caption": "A test architecture overview.",
    }


def test_normalise_caption_math_wraps_latex_for_katex():
    caption = (
        "Illustration of PR-MaGIC updating the embedding vector distribution "
        "ρ t \\rho_{t} toward μ \\mu."
    )

    normalised = _normalise_caption_math(caption)

    assert "ρ t \\rho_{t}" not in normalised
    assert "\\( \\rho_{t} \\)" in normalised
    assert "\\( \\mu \\)" in normalised
