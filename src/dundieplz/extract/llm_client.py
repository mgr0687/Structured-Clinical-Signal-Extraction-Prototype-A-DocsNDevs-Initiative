from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


class LLMClient(Protocol):
    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """Return a JSON-like dict. Must be valid JSON structure (no markdown)."""
        ...


@dataclass
class DummyLLMClient:
    """
    A local, deterministic fallback that mimics an extractor without calling any LLM.

    This is NOT a clinical tool. It's a smoke-test client so the pipeline works end-to-end.
    """

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        # We only need the raw narrative; prompt contains it at the end.
        # We'll try to extract the text block between <<<TEXT>>> markers.
        m = re.search(r"<<<TEXT>>>\s*(.*?)\s*<<<END_TEXT>>>", prompt, flags=re.DOTALL)
        text = m.group(1) if m else prompt

        lower = text.lower()

        def ev(span: str, start: Optional[int] = None, end: Optional[int] = None):
            d = {"text": span}
            if start is not None:
                d["start"] = start
            if end is not None:
                d["end"] = end
            return d

        # Heuristic examples (toy, for pipeline testing)
        suicidal_phrases = [
            "end it all",
            "kill myself",
            "suicide",
            "wish i were dead",
            "want to die",
            "better off dead",
        ]
        selfharm_phrases = [
            "cut myself",
            "cut herself",
            "cut himself",
            "self-harm",
            "self harm",
            "self-cutting",
            "burned myself",
            "scratch until bleeding",
        ]
        intent_phrases = [
            "i will kill myself",
            "i'm going to kill myself",
            "i plan to kill myself",
            "i'm going to do it",
            "i will do it tonight",
        ]
        plan_markers = [
            "plan",
            "method",
            "rope",
            "pills",
            "overdose",
            "jump",
            "gun",
            "knife",
            "bridge",
            "tonight",
            "tomorrow",
        ]
        past_markers = [
            "last year",
            "years ago",
            "previous attempt",
            "attempted",
            "overdosed",
            "tried to kill myself",
        ]

        def find_any(phrases):
            for p in phrases:
                idx = lower.find(p)
                if idx != -1:
                    return p, idx, idx + len(p)
            return None

        si = find_any(suicidal_phrases)
        sh = find_any(selfharm_phrases)
        it = find_any(intent_phrases)
        pl = find_any(plan_markers)
        pb = find_any(past_markers)

        def signal_obj(found):
            if not found:
                return {"presence": "indeterminate", "evidence": []}
            phrase, s, e = found
            return {"presence": "present", "evidence": [ev(text[s:e], s, e)]}

        out: Dict[str, Any] = {
            "suicidal_ideation": signal_obj(si),
            "self_harm": signal_obj(sh),
            "intent": signal_obj(it),
            "plan": signal_obj(pl),
            "past_behavior": signal_obj(pb),
            "temporal": "unknown",
            "uncertainty_cues": [],
            "missing_information": [],
            "extracted_by": "dummy",
            "extractor_version": "0.1",
        }

        # simple uncertainty cues
        if any(w in lower for w in ["maybe", "not sure", "i guess", "sort of", "kind of"]):
            out["uncertainty_cues"].append("hedging_language")

        # temporal guess
        if any(w in lower for w in ["today", "right now", "currently"]):
            out["temporal"] = "current"
        elif any(w in lower for w in ["yesterday", "last week", "recently"]):
            out["temporal"] = "recent"
        elif any(w in lower for w in ["last year", "years ago", "in 2019", "in 2020"]):
            out["temporal"] = "past"

        return out


class JsonParsingLLMClient:
    """
    Wraps any text-generation backend that returns a string.
    You provide a callable `generate_text(prompt)->str`, we parse JSON.
    """

    def __init__(self, generate_text):
        self._generate_text = generate_text

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        raw = self._generate_text(prompt)

        # Try direct JSON first
        try:
            return json.loads(raw)
        except Exception:
            pass

        # Fallback: extract first JSON object found in the text
        m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not m:
            raise ValueError("LLM did not return JSON.")
        return json.loads(m.group(0))


# =========================
# CONTEXTUAL CUES
# =========================
# Preparatory / contextual signals.
# Statements that suggest psychological preparation, resolution,
# or concern for consequences, without explicit ideation.

CONTEXTUAL_CUES = [
    "i have already sorted my affairs",
    "i have everything in order",
    "my children will be okay",
    "my wife will be fine without me",
    "my husband will be fine without me",
    "they will be better off this way",
    "everyone will be taken care of",
    "i made sure everything is settled",
    "i arranged my finances",
    "i put my things in order",
    "i have already said my goodbyes",
    "there is nothing left to fix",
]


# =========================
# SUBJECTIVE CUES
# =========================
# Emotional / affective burden.
# Expressions of guilt, pity, emotional conflict, or perceived burden.

SUBJECTIVE_CUES = [
    "i feel sorry for my wife",
    "i feel sorry for my children",
    "i feel sorry for my husband",
    "i hate being a burden",
    "they deserve better than me",
    "i only cause pain",
    "i feel guilty for staying alive",
    "they suffer because of me",
    "i ruin everything",
    "i feel ashamed to keep going",
    "i disappoint everyone",
    "i am tired of hurting people",
]


# =========================
# AMBIGUOUS CUES
# =========================
# Vague, non-specific statements.
# Time pressure, inevitability, or action orientation without explicit meaning.

AMBIGUOUS_CUES = [
    "it might be better this way",
    "maybe this is the only option",
    "i cannot keep waiting",
    "i do not see another way",
    "something has to be done",
    "this cannot go on",
    "i just need to do it",
    "i am running out of time",
    "i cannot hold on anymore",
    "there is no point in delaying",
    "it feels inevitable",
    "i am done trying",
]


# =========================
# OPTIONAL: unified export
# =========================
# Useful if you want to loop through categories programmatically.

ALL_CUE_GROUPS = {
    "contextual": CONTEXTUAL_CUES,
    "subjective": SUBJECTIVE_CUES,
    "ambiguous": AMBIGUOUS_CUES,
}
