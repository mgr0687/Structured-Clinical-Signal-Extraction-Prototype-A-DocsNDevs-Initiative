from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Presence(str, Enum):
    present = "present"
    absent = "absent"
    indeterminate = "indeterminate"


class EvidenceSource(str, Enum):
    llm = "llm"
    cue_matcher = "cue_matcher"
    rule = "rule"


class EvidenceSpan(BaseModel):
    text: str
    start: Optional[int] = None
    end: Optional[int] = None
    source: EvidenceSource = EvidenceSource.llm


class Signal(BaseModel):
    presence: Presence = Presence.indeterminate
    evidence: List[EvidenceSpan] = Field(default_factory=list)


class Temporal(str, Enum):
    current = "current"
    recent = "recent"
    past = "past"
    future = "future"
    unknown = "unknown"


class Signals(BaseModel):
    suicidal_ideation: Signal = Field(default_factory=Signal)
    self_harm: Signal = Field(default_factory=Signal)
    intent: Signal = Field(default_factory=Signal)
    plan: Signal = Field(default_factory=Signal)
    past_behavior: Signal = Field(default_factory=Signal)

    temporal: Temporal = Temporal.unknown
    uncertainty_cues: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


class CueHit(BaseModel):
    cue: str
    evidence: List[EvidenceSpan] = Field(default_factory=list)


class CueHits(BaseModel):
    contextual: List[CueHit] = Field(default_factory=list)
    subjective: List[CueHit] = Field(default_factory=list)
    ambiguous: List[CueHit] = Field(default_factory=list)


class ExtractorMeta(BaseModel):
    extractor_name: str = "dundieplz-extractor"
    extractor_version: str = "0.2"
    llm_backend: str = "dummy"
    language: str = "unknown"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExtractionResult(BaseModel):
    text: str
    signals: Signals = Field(default_factory=Signals)
    cue_hits: CueHits = Field(default_factory=CueHits)
    meta: ExtractorMeta = Field(default_factory=ExtractorMeta)
