"""Turns the synthetic drug-label and literature data into a flat list of
retrievable evidence chunks with metadata, following the chunk schema in the
project plan (chunk_id, drug, section, text, source, url, date).

Each DailyMed-style label section becomes one chunk (semantic sections, not
fixed-window splitting, per the plan's chunking guidance). Each literature
entry becomes one chunk. Every chunk carries an `evidence_rank` so the
retrieval/reranking layer can apply the evidence-priority hierarchy
(official label > literature) without re-deriving it at query time.
"""
from __future__ import annotations

from urllib.parse import quote

from app.data.drugs import DRUGS
from app.data.literature import LITERATURE

EVIDENCE_RANK_LABEL = 1
EVIDENCE_RANK_LITERATURE = 3

# Human-readable section labels, in a fixed presentation order.
LABEL_SECTIONS = [
    ("indications", "Indications and Usage"),
    ("contraindications", "Contraindications"),
    ("warnings_and_precautions", "Warnings and Precautions"),
    ("adverse_reactions", "Adverse Reactions"),
    ("drug_interactions", "Drug Interactions"),
    ("dosage_considerations", "Dosage Considerations"),
]

POPULATION_SECTIONS = [
    ("renal_impairment", "Use in Specific Populations - Renal Impairment"),
    ("hepatic_impairment", "Use in Specific Populations - Hepatic Impairment"),
    ("geriatric_use", "Use in Specific Populations - Geriatric Use"),
    ("pregnancy", "Use in Specific Populations - Pregnancy"),
]


TAG_SEARCH_PHRASES = {
    "renal_impairment": "renal impairment",
    "hepatic_impairment": "hepatic impairment",
    "elderly": "elderly",
    "allergy": "hypersensitivity",
    "interactions": "drug interactions",
    "chronic_use": "long-term use",
    "cardiovascular": "cardiovascular safety",
}


def _dailymed_url(drug: dict) -> str:
    # Prefer a direct link to the specific SPL document (resolved ahead of
    # time against the real DailyMed API, see drugs.py `dailymed_setid`) so
    # "Open source" lands on the exact label, not a search results page.
    setid = drug.get("dailymed_setid")
    if setid:
        return f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}"
    return (
        "https://dailymed.nlm.nih.gov/dailymed/search.cfm?query="
        f"{quote(drug['generic_name'])}"
    )


def _pubmed_search_url(generic_name: str, relevance_tags: list[str]) -> str:
    # Rather than searching for the fabricated demo title verbatim (which
    # would reliably return zero results on the real PubMed), search PubMed
    # for the drug plus its clinical topic, so the link lands on genuine,
    # relevant literature on the real site.
    topics = [TAG_SEARCH_PHRASES[t] for t in relevance_tags if t in TAG_SEARCH_PHRASES]
    term = " ".join([generic_name, *topics]) if topics else generic_name
    return f"https://pubmed.ncbi.nlm.nih.gov/?term={quote(term)}"


def build_chunks() -> list[dict]:
    chunks: list[dict] = []

    for drug in DRUGS:
        drug_id = drug["drug_id"]
        generic_name = drug["generic_name"]
        sections = drug["sections"]
        url = _dailymed_url(drug)

        for key, label in LABEL_SECTIONS:
            text = sections.get(key)
            if not text:
                continue
            chunk_id = f"DM_{drug_id}_{key}"
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "drug_id": drug_id,
                    "drug_name": generic_name,
                    "drug_class": drug["drug_class"],
                    "source_name": "DailyMed",
                    "source_type": "label",
                    "section": label,
                    "text": text,
                    "url": url,
                    "publication_date": "current label",
                    "evidence_rank": EVIDENCE_RANK_LABEL,
                }
            )

        pop = sections.get("use_in_specific_populations", {})
        for key, label in POPULATION_SECTIONS:
            text = pop.get(key)
            if not text:
                continue
            chunk_id = f"DM_{drug_id}_pop_{key}"
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "drug_id": drug_id,
                    "drug_name": generic_name,
                    "drug_class": drug["drug_class"],
                    "source_name": "DailyMed",
                    "source_type": "label",
                    "section": label,
                    "text": text,
                    "url": url,
                    "publication_date": "current label",
                    "evidence_rank": EVIDENCE_RANK_LABEL,
                    "population_tag": key,
                }
            )

    drug_lookup = {d["drug_id"]: d for d in DRUGS}
    for entry in LITERATURE:
        drug = drug_lookup[entry["drug_id"]]
        chunk_id = f"LIT_{entry['pmid']}"
        chunks.append(
            {
                "chunk_id": chunk_id,
                "drug_id": entry["drug_id"],
                "drug_name": drug["generic_name"],
                "drug_class": drug["drug_class"],
                "source_name": "PubMed",
                "source_type": "literature",
                "section": entry["title"],
                "text": entry["finding"],
                "url": _pubmed_search_url(drug["generic_name"], entry.get("relevance_tags", [])),
                "publication_date": str(entry["year"]),
                "evidence_rank": EVIDENCE_RANK_LITERATURE,
                "relevance_tags": entry.get("relevance_tags", []),
            }
        )

    return chunks


if __name__ == "__main__":
    import json

    chunks = build_chunks()
    print(f"Built {len(chunks)} chunks across {len(DRUGS)} drugs.")
    print(json.dumps(chunks[0], indent=2))
