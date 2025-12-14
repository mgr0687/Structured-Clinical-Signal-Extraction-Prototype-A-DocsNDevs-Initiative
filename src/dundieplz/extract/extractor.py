# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from dundieplz.schemas.extractor_schema import (
    CueHit,
    CueHits,
    EvidenceSource,
    EvidenceSpan,
    ExtractionResult,
    ExtractorMeta,
    Presence,
    Signal,
    Signals,
    Temporal,
)

from dundieplz.extract.llm_client import LLMClient


# -----------------------------
# Extras
# -----------------------------

def _detect_language(text: str) -> str:
    """
    Very lightweight language guess (non-NLP).
    """
    lower = text.lower()

    # Portuguese (pt-BR) hints
    if any(ch in lower for ch in ["ã", "õ", "ç", "á", "é", "í", "ó", "ú"]) or any(
        w in lower for w in ["não", "queria", "amanhã", "filhos", "esposa", "marido"]
    ):
        return "pt-BR"

    # English hints
    if any(w in lower for w in [" i ", " my ", " wish", " die", " kill", " suicide"]):
        return "en"

    return "unknown"


def _find_all(haystack_lower: str, needle_lower: str) -> List[Tuple[int, int]]:
    """
    Returns (start, end) spans for literal substring matches.
    Deterministic and audit-friendly.
    """
    if not needle_lower:
        return []

    out: List[Tuple[int, int]] = []
    start = 0
    while True:
        idx = haystack_lower.find(needle_lower, start)
        if idx == -1:
            break
        out.append((idx, idx + len(needle_lower)))
        start = idx + 1  # allow overlaps
    return out


def _dict_to_signal(obj: Dict, default_source: EvidenceSource) -> Signal:
    """
    Converts a backend dict into a Signal schema object.
    """
    presence_raw = obj.get("presence", "indeterminate")
    try:
        presence = Presence(presence_raw)
    except Exception:
        presence = Presence.indeterminate

    evidence_list = []
    for ev in obj.get("evidence", []) or []:
        evidence_list.append(
            EvidenceSpan(
                text=str(ev.get("text", "")),
                start=ev.get("start"),
                end=ev.get("end"),
                source=default_source,
            )
        )

    return Signal(presence=presence, evidence=evidence_list)


def _dict_to_temporal(value: str) -> Temporal:
    try:
        return Temporal(value)
    except Exception:
        return Temporal.unknown


# -----------------------------
# Extractor
# -----------------------------

@dataclass
class Extractor:
    """
    Extractor
    - receives raw text
    - calls backend (dummy / rules / llm)
    - runs cue matcher
    - returns ExtractionResult
    """

    llm_client: LLMClient

    def extract(self, text: str) -> ExtractionResult:
        raw_text = text or ""
        lower = raw_text.lower()

        # Call backend
        llm_out = self.llm_client.generate_json(raw_text)

        # Detect backend identity
        backend_name = getattr(self.llm_client, "backend_name", "llm")

        # Decide evidence source based on backend
        if backend_name == "rules":
            default_source = EvidenceSource.rule
        else:
            default_source = EvidenceSource.llm

        # Build signals
        signals = Signals(
            suicidal_ideation=_dict_to_signal(
                llm_out.get("suicidal_ideation", {}),
                default_source,
            ),
            self_harm=_dict_to_signal(
                llm_out.get("self_harm", {}),
                default_source,
            ),
            intent=_dict_to_signal(
                llm_out.get("intent", {}),
                default_source,
            ),
            plan=_dict_to_signal(
                llm_out.get("plan", {}),
                default_source,
            ),
            past_behavior=_dict_to_signal(
                llm_out.get("past_behavior", {}),
                default_source,
            ),
            temporal=_dict_to_temporal(llm_out.get("temporal", "unknown")),
            uncertainty_cues=list(llm_out.get("uncertainty_cues", []) or []),
            missing_information=list(llm_out.get("missing_information", []) or []),
        )

        # Cue matcher (literal, deterministic)
        cue_hits = self._match_cues(raw_text, lower)

        # Meta
        meta = ExtractorMeta(
            llm_backend=backend_name,
            language=_detect_language(raw_text),
        )

        return ExtractionResult(
            text=raw_text,
            signals=signals,
            cue_hits=cue_hits,
            meta=meta,
        )

    # -----------------------------
    # Cue matcher
    # -----------------------------

    def _match_cues(self, raw_text: str, lower: str) -> CueHits:
        """
        Literal cue matching with offsets.
        """
        from dundieplz.extract.llm_client import (
            CONTEXTUAL_CUES,
            SUBJECTIVE_CUES,
            AMBIGUOUS_CUES,
        )

        def build_hits(cues: List[str]) -> List[CueHit]:
            hits: List[CueHit] = []
            for cue in cues:
                cue_l = cue.lower()
                spans = _find_all(lower, cue_l)
                if not spans:
                    continue

                evidence = [
                    EvidenceSpan(
                        text=raw_text[s:e],
                        start=s,
                        end=e,
                        source=EvidenceSource.cue_matcher,
                    )
                    for (s, e) in spans
                ]
                hits.append(CueHit(cue=cue, evidence=evidence))
            return hits

        return CueHits(
            contextual=build_hits(CONTEXTUAL_CUES),
            subjective=build_hits(SUBJECTIVE_CUES),
            ambiguous=build_hits(AMBIGUOUS_CUES),
        )


# -----------------------------
# Optional factory
# -----------------------------

def build_default_extractor() -> Extractor:
    """
    Creates an Extractor using DummyLLMClient.
    Intended for smoke-tests and demos.
    """
    from dundieplz.extract.llm_client import DummyLLMClient

    return Extractor(llm_client=DummyLLMClient())
