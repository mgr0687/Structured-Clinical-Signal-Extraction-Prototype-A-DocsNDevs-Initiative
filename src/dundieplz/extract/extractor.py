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
    PTBR provavel (não-NLP).
    
    """
    lower = text.lower()
    # pt br huehue
    if any(ch in lower for ch in ["ã", "õ", "ç", "á", "é", "í", "ó", "ú"]) or any(
        w in lower for w in ["não", "queria", "amanhã", "filhos", "esposa", "marido"]
    ):
        return "pt-BR"
    # english
    if any(w in lower for w in ["i ", "my ", "wish", "die", "kill", "suicide"]):
        return "en"
    return "unknown"


def _find_all(haystack_lower: str, needle_lower: str) -> List[Tuple[int, int]]:
    """
    Retorna (start, end) de needle em haystack, via busca literal.
    Deterministico e auditavel.
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
        start = idx + 1  # overlapson isso vc tem que ver mais pra frente 
    return out


def _dict_to_signal(obj: Dict, default_source: EvidenceSource) -> Signal:
    """
    Converte o bloco do llm_client (dict) para nosso Signal (schema).
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



@dataclass
class Extractor:
    """
    Extractor
    - recebe texto bruto
    - chama llm_client (dummy agora)
    - roda cue matcher (hits)
    - devolve ExtractionResult (form)
    """
    llm_client: LLMClient

   

    def extract(self, text: str) -> ExtractionResult:

        raw_text = text or ""
        lower = raw_text.lower()

        # call dummy-llm
        llm_out = self.llm_client.generate_json(raw_text)

        # signals

        signals = Signals(
            suicidal_ideation=_dict_to_signal(llm_out.get("suicidal_ideation", {}), EvidenceSource.llm),
            self_harm=_dict_to_signal(llm_out.get("self_harm", {}), EvidenceSource.llm),
            intent=_dict_to_signal(llm_out.get("intent", {}), EvidenceSource.llm),
            plan=_dict_to_signal(llm_out.get("plan", {}), EvidenceSource.llm),
            past_behavior=_dict_to_signal(llm_out.get("past_behavior", {}), EvidenceSource.llm),
            temporal=_dict_to_temporal(llm_out.get("temporal", "unknown")),
            uncertainty_cues=list(llm_out.get("uncertainty_cues", []) or []),
            missing_information=list(llm_out.get("missing_information", []) or []),
        )

       
        cue_hits = self._match_cues(raw_text, lower)

        # Auditory
        meta = ExtractorMeta(
            llm_backend=str(llm_out.get("extracted_by", "unknown")),
            # extractor_version já tem default no schema; mas você pode sobrescrever aqui se quiser
            language=_detect_language(raw_text),
        )

        # form
        return ExtractionResult(
            text=raw_text,
            signals=signals,
            cue_hits=cue_hits,
            meta=meta,
        )

    def _match_cues(self, raw_text: str, lower: str) -> CueHits:
        """
        hits para:
        - contextual
        - subjective
        - ambiguous
        usando match literal + offsets.
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


# Factory opcional (duvidoso)


def build_default_extractor() -> Extractor:
    """
    Cria um Extractor usando o DummyLLMClient.
     smoke-tests e demo
    """
    from dundieplz.extract.llm_client import DummyLLMClient
    return Extractor(llm_client=DummyLLMClient())
