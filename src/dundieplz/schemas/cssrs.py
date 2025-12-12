from __future__ import annotations

from pydantic import BaseModel, Field
from .core_signals import EvidenceSpan, Presence, TemporalContext


class CSSRSInspiredOutput(BaseModel):
    """
    C-SSRS-inspired representation (NO scoring).
    Reference schema to demonstrate mapping demands.
    """

    passive_ideation: Presence = Field(Presence.indeterminate)
    active_ideation: Presence = Field(Presence.indeterminate)

    intent: Presence = Field(Presence.indeterminate)
    plan: Presence = Field(Presence.indeterminate)
    method_specified: Presence = Field(Presence.indeterminate)
    access_to_means: Presence = Field(Presence.indeterminate)
    timeframe_specified: Presence = Field(Presence.indeterminate)

    past_suicidal_behavior: Presence = Field(Presence.indeterminate)
    preparatory_behaviors: Presence = Field(Presence.indeterminate)

    temporal: TemporalContext = TemporalContext.unknown
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    notes: str | None = Field(None, description="Explain ambiguity; never score or recommend.")
