from __future__ import annotations

from pydantic import BaseModel, Field
from .core_signals import EvidenceSpan, Presence


class PHQ9Item9Output(BaseModel):
    """
    PHQ-9 Item 9 representation (NO scoring).
    Only structures whether the narrative contains thoughts of death/self-harm.
    """

    item9_presence: Presence = Field(
        ...,
        description="Presence/absence/indeterminacy of thoughts of death or self-harm.",
    )
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    notes: str | None = Field(None, description="Explain ambiguity; do not recommend actions.")
