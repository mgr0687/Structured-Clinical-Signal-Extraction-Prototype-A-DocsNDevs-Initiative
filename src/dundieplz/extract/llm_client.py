# -*- coding: ascii -*-

from __future__ import annotations

from typing import Dict, List, Protocol


# -----------------------------
# Cues (used by cue_matcher in extractor.py)
# -----------------------------

CONTEXTUAL_CUES: List[str] = [
    "I gave my dog away",
    "I gave my pet away",
    "I gave my pets away",
    "My pets will be fine",
    "I separated the inheritance",
    "I already separated the inheritance",
    "My kids will be fine",
    "My children will be fine",
    "My wife will be fine",
    "My husband will be fine",
    "I feel sorry for my wife",
    "I feel sorry for my husband",
    "I feel sorry for my kids",
    "I feel sorry for my children",
    "I cannot keep waiting",
    "Better I do it",
]

SUBJECTIVE_CUES: List[str] = [
    "there is only one way to solve this",
    "only one way to solve this",
    "I cannot take it anymore",
    "I am done",
    "I am exhausted",
    "I am a burden",
    "I cause too much trouble",
]

AMBIGUOUS_CUES: List[str] = [
    "saio da vida para entrar na historia",
    "chega eu nao aguento mais",
    "eu queria nao acordar amanha",
]

DIRECT_SUICIDAL_CUES: List[str] = [
    "kill myself",
    "suicide",
    "want to die",
    "wish i were dead",
    "end it all",
    "better off dead",
    "eu queria nao acordar amanha",
    "vou por uma bala na minha cabeca",
]


# -----------------------------
# LLMClient protocol
# -----------------------------

class LLMClient(Protocol):
    def generate_json(self, prompt: str) -> Dict:
        ...


# -----------------------------
# Dummy backend (heuristic baseline)
# -----------------------------

class DummyLLMClient:
    """
    Lightweight heuristic backend.
    Purpose: smoke tests and baseline behavior.

    This is NOT clinical inference.
    """

    def __init__(self) -> None:
        self.backend_name = "dummy"

    def generate_json(self, prompt: str) -> Dict:
        text = prompt or ""
        lower = text.lower()

        ideation_hits = self._find_any(lower, DIRECT_SUICIDAL_CUES)

        temporal = "unknown"
        if any(w in lower for w in ["now", "right now", "today", "emergency department"]):
            temporal = "current"
        elif any(w in lower for w in ["yesterday", "last night", "earlier today"]):
            temporal = "recent"
        elif any(w in lower for w in ["tonight", "tomorrow", "next week"]):
            temporal = "future"
        elif any(w in lower for w in ["years ago", "months ago", "last year"]):
            temporal = "past"

        if ideation_hits:
            suicidal_ideation = {
                "presence": "present",
                "evidence": ideation_hits,
            }
            uncertainty_cues: List[str] = []
            missing_information: List[str] = [
                "method_or_plan_details_not_specified"
            ]
        else:
            suicidal_ideation = {
                "presence": "indeterminate",
                "evidence": [],
            }
            uncertainty_cues = [
                "insufficient_explicit_ideation_evidence"
            ]
            missing_information = []

        return {
            "suicidal_ideation": suicidal_ideation,
            "self_harm": {"presence": "indeterminate", "evidence": []},
            "intent": {"presence": "indeterminate", "evidence": []},
            "plan": {"presence": "indeterminate", "evidence": []},
            "past_behavior": {"presence": "indeterminate", "evidence": []},
            "temporal": temporal,
            "uncertainty_cues": uncertainty_cues,
            "missing_information": missing_information,
        }

    def _find_any(self, lower_text: str, cues: List[str]) -> List[Dict]:
        evidence: List[Dict] = []
        for cue in cues:
            cue_l = cue.lower()
            start = 0
            while True:
                idx = lower_text.find(cue_l, start)
                if idx == -1:
                    break
                evidence.append(
                    {
                        "text": cue,
                        "start": idx,
                        "end": idx + len(cue_l),
                        "source": "llm",
                    }
                )
                start = idx + 1
        return evidence
