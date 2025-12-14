from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Span:
    text: str
    start: int
    end: int


class RuleLLMClient:
    """
    Offline, deterministic rule-based backend.

    - Deterministic & audit-friendly
    - NOT a clinical model
    - Returns JSON-like dict compatible with Extractor schema adapter
    """

    def __init__(self) -> None:
        # IMPORTANT: used by Extractor to tag meta.llm_backend and EvidenceSource
        self.backend_name = "rules"

        # Explicit denial patterns
        self._denial_patterns = [
            r"\bdenies suicidal ideation\b",
            r"\bdenies suicide ideation\b",
            r"\bdenies suicidal thoughts\b",
            r"\bdenies SI\b",
        ]

        # Direct ideation language
        self._ideation_patterns = [
            r"\bi want to die\b",
            r"\bwant to die\b",
            r"\bwish i were dead\b",
            r"\bend it all\b",
            r"\bkill myself\b",
            r"\bsuicide\b",
            r"\bbetter off dead\b",
        ]

        # Attempt / intoxication markers
        self._attempt_patterns = [
            r"\bsuicide attempt\b",
            r"\battempted suicide\b",
            r"\bexogenous intoxication\b",
            r"\boverdose\b",
            r"\bintoxication\b",
        ]

        # Firearm / post-mortem markers
        self._firearm_patterns = [
            r"\bgunshot\b",
            r"\bfirearm\b",
            r"\bfirearm injury\b",
            r"\btraumatic brain injury\b",
            r"\bleft temporal region\b",
        ]

        # Indirect / third-party reconstruction
        self._indirect_intent_patterns = [
            r"\bfarewell messages\b",
            r"\bfarewell message\b",
            r"\bleft a letter\b",
            r"\bleft (?:a )?note\b",
        ]

        # Temporal hints
        self._temporal_current_patterns = [
            r"\bemergency department\b",
            r"\bat triage\b",
            r"\bchief complaint\b",
            r"\btoday\b",
            r"\bnow\b",
            r"\bright now\b",
        ]
        self._temporal_recent_patterns = [
            r"\byesterday\b",
            r"\blast night\b",
            r"\bearlier today\b",
            r"\bthree months ago\b",
            r"\b(\d+)\s+months?\s+ago\b",
            r"\brecent\b",
            r"\boutpatient\b",
            r"\bpsychiatric assessment\b",
        ]
        self._temporal_past_patterns = [
            r"\bdeath was confirmed\b",
            r"\bwithout vital signs\b",
            r"\bmedical examiner\b",
            r"\bpost-mortem\b",
            r"\bambulance\b",
            r"\bsamu\b",
        ]

    def generate_json(self, prompt: str) -> Dict:
        text = self._extract_text_block(prompt) or prompt
        return self._extract_signals_from_text(text)

    def _extract_signals_from_text(self, text: str) -> Dict:
        denial_spans = self._find_any(text, self._denial_patterns)
        ideation_spans = self._find_any(text, self._ideation_patterns)
        attempt_spans = self._find_any(text, self._attempt_patterns)
        firearm_spans = self._find_any(text, self._firearm_patterns)
        indirect_spans = self._find_any(text, self._indirect_intent_patterns)

        uncertainty_cues: List[str] = []
        missing_information: List[str] = []

        # suicidal_ideation
        if ideation_spans and denial_spans:
            suicidal_ideation = self._signal("indeterminate", ideation_spans + denial_spans)
            uncertainty_cues.append("explicit_denial_with_ideation_language")
        elif ideation_spans:
            suicidal_ideation = self._signal("present", ideation_spans)
        elif attempt_spans or firearm_spans or indirect_spans:
            suicidal_ideation = self._signal("present", attempt_spans + firearm_spans + indirect_spans)
            if indirect_spans:
                uncertainty_cues.append("retrospective_or_third_party_evidence")
        else:
            suicidal_ideation = self._signal("indeterminate", [])
            uncertainty_cues.append("insufficient_explicit_ideation_evidence")

        # past_behavior
        if attempt_spans or firearm_spans or indirect_spans:
            past_behavior = self._signal("present", attempt_spans + firearm_spans + indirect_spans)
        else:
            past_behavior = self._signal("indeterminate", [])

        # intent & plan
        if attempt_spans:
            intent = self._signal("present", attempt_spans)
            plan = self._signal("present", attempt_spans)
        elif firearm_spans:
            intent = self._signal("present", firearm_spans + indirect_spans)
            plan = self._signal("present", firearm_spans + indirect_spans)
        elif indirect_spans:
            intent = self._signal("present", indirect_spans)
            plan = self._signal("present", indirect_spans)
        else:
            if denial_spans:
                intent = self._signal("absent", denial_spans)
                plan = self._signal("absent", denial_spans)
            else:
                intent = self._signal("indeterminate", [])
                plan = self._signal("indeterminate", [])

        # self_harm (kept conservative in prototype)
        self_harm = self._signal("indeterminate", [])

        # temporal
        temporal = self._infer_temporal(text, attempt_spans, firearm_spans, indirect_spans)

        # missing info hint
        if suicidal_ideation["presence"] == "present" and plan["presence"] in ("indeterminate", "absent"):
            missing_information.append("method_or_plan_details_not_specified")

        return {
            "suicidal_ideation": suicidal_ideation,
            "self_harm": self_harm,
            "intent": intent,
            "plan": plan,
            "past_behavior": past_behavior,
            "temporal": temporal,
            "uncertainty_cues": uncertainty_cues,
            "missing_information": missing_information,
        }

    def _infer_temporal(
        self,
        text: str,
        attempt_spans: List[Span],
        firearm_spans: List[Span],
        indirect_spans: List[Span],
    ) -> str:
        if attempt_spans and self._has_any_patterns(text, self._temporal_current_patterns):
            return "current"

        if (firearm_spans or indirect_spans) and self._has_any_patterns(text, self._temporal_past_patterns):
            return "past"

        if self._has_any_patterns(text, self._temporal_recent_patterns):
            return "recent"

        if indirect_spans:
            return "past"

        if re.search(r"\btonight\b|\btomorrow\b|\bnext week\b", text, flags=re.IGNORECASE):
            return "future"

        return "unknown"

    def _extract_text_block(self, prompt: str) -> Optional[str]:
        m = re.search(r"<<<TEXT>>>\s*(.*?)\s*<<<END_TEXT>>>", prompt, flags=re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1)
        return None

    def _signal(self, presence: str, evidence: List[Span]) -> Dict:
        return {
            "presence": presence,
            "evidence": [{"text": sp.text, "start": sp.start, "end": sp.end, "source": "rule"} for sp in evidence],
        }

    def _has_any_patterns(self, text: str, patterns: List[str]) -> bool:
        return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)

    def _find_any(self, text: str, patterns: List[str]) -> List[Span]:
        spans: List[Span] = []
        for pat in patterns:
            for m in re.finditer(pat, text, flags=re.IGNORECASE):
                spans.append(Span(text=text[m.start() : m.end()], start=m.start(), end=m.end()))
        return self._dedupe_overlapping_spans(spans)

    def _dedupe_overlapping_spans(self, spans: List[Span]) -> List[Span]:
        if not spans:
            return []

        spans_sorted = sorted(spans, key=lambda s: (s.start, -(s.end - s.start), s.text.lower()))
        kept: List[Span] = []

        for sp in spans_sorted:
            if any(sp.start >= kp.start and sp.end <= kp.end for kp in kept):
                continue
            kept.append(sp)

        kept = sorted(kept, key=lambda s: (s.start, s.end))
        uniq: Dict[Tuple[int, int, str], Span] = {}
        for sp in kept:
            uniq[(sp.start, sp.end, sp.text)] = sp
        return list(uniq.values())
