"""Citation construction and faithfulness verification (plan STEP 10, 15C).

For every generated claim we store which evidence chunk(s) it is linked to,
and separately verify that every referenced chunk id actually exists among
the retrieved evidence (so the frontend can never show a citation pointing
at nothing, and the evaluation layer can measure citation precision/coverage).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

CHUNK_ID_PATTERN = re.compile(r"\[([A-Za-z0-9_]+)\]")


@dataclass
class Claim:
    claim_id: str
    claim_text: str
    source_chunk_ids: list[str] = field(default_factory=list)
    supported: bool = False


def extract_claims(statements: list[str], valid_chunk_ids: set[str], prefix: str) -> list[Claim]:
    claims: list[Claim] = []
    for i, statement in enumerate(statements):
        referenced = CHUNK_ID_PATTERN.findall(statement)
        valid_refs = [cid for cid in referenced if cid in valid_chunk_ids]
        claims.append(
            Claim(
                claim_id=f"{prefix}_{i}",
                claim_text=statement,
                source_chunk_ids=valid_refs,
                supported=len(valid_refs) > 0,
            )
        )
    return claims


def citation_metrics(claims: list[Claim]) -> dict:
    if not claims:
        return {"precision": 1.0, "coverage": 1.0, "unsupported_claim_rate": 0.0}
    supported = sum(1 for c in claims if c.supported)
    return {
        "precision": round(supported / len(claims), 3),
        "coverage": round(supported / len(claims), 3),
        "unsupported_claim_rate": round(1 - supported / len(claims), 3),
    }
