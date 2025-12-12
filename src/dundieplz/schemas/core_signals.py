from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class Presence(str, Enum):
    present = "present"
    absent = "absent"
    indeterminate = "indeterminate"


class EvidenceSpan(BaseModel):
    text: str = Field(..., description="Quoted text span supporting the claim.")
    start: Optional[int] = Field(None, description="Optional character start index.")
    end: Optional[int] = Field(None, description="Optional character end index.")


class Signal(BaseModel):
    presence: Presence
    evidence: List[EvidenceSpan] = Field(default_factory=list)
    notes: Optional[str] = Field(
        None,
        description="Emphasize ambiguity/uncertainty; never recommend actions.",
    )


class TemporalContext(str, Enum):
    current = "current"
    recent = "recent"
    past = "past"
    unknown = "unknown"


class ExtractedCoreSignals(BaseModel):
    """
    Framework-agnostic extraction layer.
    Not a clinical assessment. Only structures narrative signals.
    """

    suicidal_ideation: Signal = Field(
        default_factory=lambda: Signal(presence=Presence.indeterminate),
        description="Any ideation content (passive or active).",
    )
    self_harm: Signal = Field(
        default_factory=lambda: Signal(presence=Presence.indeterminate),
        description="Self-harm / NSSI references (if any).",
    )
    intent: Signal = Field(
        default_factory=lambda: Signal(presence=Presence.indeterminate),
        description="Intent to act (if stated).",
    )
    plan: Signal = Field(
        default_factory=lambda: Signal(presence=Presence.indeterminate),
        description="Plan/method/access/timeframe details (if stated).",
    )
    past_behavior: Signal = Field(
        default_factory=lambda: Signal(presence=Presence.indeterminate),
        description="Past attempts/behaviors/preparatory acts (if stated).",
    )

    temporal: TemporalContext = TemporalContext.unknown
    uncertainty_cues: List[str] = Field(
        default_factory=list,
        description="Cues like 'maybe', contradictions, vague phrasing, denial with qualifiers.",
    )
    missing_information: List[str] = Field(
        default_factory=list,
        description="Explicitly list missing details needed for fuller framework mapping.",
    )

    extracted_by: str = Field("llm", description="Extractor identifier.")
    extractor_version: str = Field("0.1", description="Version tag for reproducibility.")
