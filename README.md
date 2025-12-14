# Structured Clinical Signal Extraction Prototype: A DocsNDevs Initiative [![Build Status](https://img.shields.io/github/workflow/status/username/repository/CI)](https://github.com/username/repository/actions) [![Coverage Status](https://coveralls.io/repos/github/username/repository/badge.svg?branch=main)](https://coveralls.io/github/username/repository?branch=main) [![License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/licenses/MIT) [![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
This is an early-stage, research-oriented prototype for structured extraction of suicide-related clinical signals from free-text psychiatric notes.

This project explores how subjective and contextual psychiatric language can be transformed into auditable, deterministic structures while acknowledging the epistemic limits, uncertainty, and failure modes inherent in clinical text analysis.

Please note: DundiePlz is not a production-ready system, not a diagnostic tool, and not a clinical decision support system. At this stage, DundiePlz is primarily focused on governance, interpretability, and error discovery, not performance, scalability, or clinical validity.

Quickstart
Prerequisites

Ensure Python 3.8+ is installed. If not, download it from python.org
.

Clone the repository:

git clone https://github.com/username/dundieplz.git
cd dundieplz


Install dependencies:

It is recommended to create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate  # On Windows, use .venv\Scripts\activate


Then install the required packages:

pip install -r requirements.txt


Run the Streamlit GUI:

After installing dependencies, run the Streamlit application to interact with the model:

streamlit run dundieplz/gui_app.py


Interact with the prototype:

Load synthetic cases using the buttons.

Paste or type clinical notes into the input field.

Choose the backend (rules or dummy).

View the structured output with evidence highlighting and structured JSON.

The model uses a deterministic dummy backend or a rule-based backend for simulating NLP behavior and validating extraction.

Project Goals

The primary goals of DundiePlz are to:

Explore the limitations of structured frameworks (e.g., C-SSRS, PHQ-9) when applied to free-text clinical narratives.

Design a framework-agnostic core layer that normalizes ambiguous or indeterminate signals.

Produce auditable outputs with explicit evidence spans, enabling transparency in clinical decision-making processes.

Avoid unsupported clinical inference and overreach.

Prioritize determinism, transparency, and safety during early prototyping and development.

Non-goals

DundiePlz does not aim to:

Predict suicide risk.

Replace clinical judgment or human expertise.

Perform automated diagnosis.

Provide real-time patient-facing interventions.

Optimize performance or recall metrics at this stage.

Any apparent “intelligence” in the system is intentionally constrained for research purposes.

Architecture Overview

The system is structured with a layered design:

1. Core Signal Layer (Framework-agnostic)

The core signal layer extracts atomic clinical signals, such as:

Suicidal ideation (presence / absence / indeterminate)

Intent

Plan

Past behavior

Temporal orientation (past / recent / current / future / unknown)

This layer is non-clinical and non-inferential, ensuring that ambiguity is handled early and does not propagate to higher levels of analysis.

2. Framework-Specific Layers (Planned / Partial)

Higher-level frameworks such as:

C-SSRS

PHQ-9

are treated as interpretive overlays on top of the core signals. These frameworks do not assume or encode any clinical decision-making logic by default but can be integrated in a way that respects the limitations of each framework.

Deterministic Backends

To preserve reproducibility and auditability, the project currently supports offline backends:

Dummy Backend — A minimal, conservative extraction used for smoke testing and ensuring baseline functionality.

Rule-Based Backend — A deterministic pattern matching system used to simulate NLP behavior for validating the extraction pipeline with synthetic cases.

These backends do not perform clinical inference but serve to validate the extraction pipeline and evaluate the functioning of the core system.

LLM-based backends are intentionally deferred until the system is more mature.

Evidence-First Outputs

All extracted signals include:

Explicit presence states (present, absent, indeterminate).

Evidence spans with character offsets, making the extraction process transparent.

Source attribution (rule-based, cue-based, or LLM-based) for full traceability of the signals.

This allows downstream users to inspect why a signal was generated, not just its presence or absence.

Synthetic Cases

The project uses clinically realistic synthetic cases, created by a psychiatrist with experience in emergency and urgent care settings. These cases are designed for validation, not for training, and are explicitly labeled as fictional.

Each synthetic case includes:

A fictional case disclaimer.

Sensitive content warnings.

No real patient data is used in the project.

Minimal GUI

A lightweight Streamlit-based GUI is included for:

Loading full synthetic cases.

Switching between deterministic backends.

Inspecting structured outputs and evidence.

Visualizing extracted evidence.

The GUI serves as a testing interface and is not intended for clinical use or deployment.

Safety Considerations

DundiePlz intentionally avoids:

Generating new ideation or suggestions for suicide methods.

Making unsupported clinical assertions.

Providing advice or clinical recommendations.

Escalating ambiguous signals to actionable conclusions.

Ambiguity is preserved when ambiguity exists, and no unqualified assumptions are made by the system.

Current Status

As of this version:

Fully local execution.

One-case-at-a-time processing.

Deterministic, auditable outputs.

Explicit handling of temporal references.

Conservative behavior by design, with explicit limits to the model's "intelligence".

The project is in early prototype (v0.1), and scalability is not yet a primary concern.

Planned Next Steps

Planned next steps include:

Expanding the synthetic case evaluation set.

Introducing batch processing capabilities for more efficient analysis.

Improving temporal reasoning edge cases.

Formalizing the integration of framework-specific overlays.

Exploring governance and evaluation metrics.

Investigating safe integration of non-local models for scalability.

Disclaimer

This project is for research and prototyping purposes only. It is not intended for clinical use, diagnosis, triage, or patient care. All outputs should be interpreted with caution, and professional medical expertise should always be consulted in clinical settings.

Author

Developed by a psychiatrist with clinical experience in emergency and urgent care settings, exploring the intersection of psychiatry, NLP, and AI governance.