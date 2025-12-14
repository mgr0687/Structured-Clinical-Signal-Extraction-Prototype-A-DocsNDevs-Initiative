# Structured Clinical Signal Extraction Prototype: A DocsNDevs Initiative

[![Build Status](https://img.shields.io/github/workflow/status/username/repository/CI)](https://github.com/username/repository/actions)
[![Coverage Status](https://coveralls.io/repos/github/username/repository/badge.svg?branch=main)](https://coveralls.io/github/username/repository?branch=main)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

**DundiePlz** is an early-stage, research-oriented prototype for **structured extraction of suicide-related clinical signals** from free-text psychiatric notes.

The project explores how subjective, contextual psychiatric language can be mapped into **auditable, deterministic structures**, while explicitly acknowledging epistemic limits, uncertainty, and failure modes.

This is **not** a production system, **not** a diagnostic tool, and **not** a clinical decision-support system.  
At this stage, DundiePlz is focused on **governance, interpretability, and error discovery**, not performance or scale.

---

## Quickstart

### Prerequisites

Ensure you have Python 3.8+ installed. If not, download it from [python.org](https://www.python.org/downloads/).

1. **Clone the repository**:

    ```bash
    git clone https://github.com/username/dundieplz.git
    cd dundieplz
    ```

2. **Install dependencies**:

    Create and activate a virtual environment (optional but recommended):

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use .venv\Scripts\activate
    ```

    Then install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Streamlit GUI**:

    After installing dependencies, run the Streamlit application to interact with the model:

    ```bash
    streamlit run dundieplz/gui_app.py
    ```

4. **Interact with the prototype**:

    - Load synthetic cases from the buttons
    - Paste or type clinical notes into the input field
    - Choose the backend (rules or dummy)
    - See the output with evidence highlighting and structured JSON

    The model uses a **deterministic dummy backend** or a **rule-based backend** for simulating NLP behavior and validating extraction.

---

## Project goals

The primary goals of DundiePlz are to:

- Explore the **limits of structured frameworks** (e.g., C-SSRS, PHQ-9) when applied to free-text clinical narratives
- Design a **framework-agnostic core layer** that normalizes ambiguous or indeterminate signals
- Produce **auditable outputs** with explicit evidence spans
- Avoid unsupported clinical inference
- Prioritize **determinism, transparency, and safety** during early prototyping

---

## Non-goals (important)

DundiePlz does **not** aim to:

- Predict suicide risk
- Replace clinical judgment
- Perform automated diagnosis
- Provide real-time patient-facing interventions
- Optimize accuracy, recall, or performance metrics at this stage

Any apparent “intelligence” in the system is intentionally constrained.

---

## Architecture overview

The system is intentionally layered:

### 1. Core signal layer (framework-agnostic)

At the lowest level, the system extracts **atomic clinical signals**, such as:

- Suicidal ideation (presence / absence / indeterminate)
- Intent
- Plan
- Past behavior
- Temporal orientation (past / recent / current / future / unknown)

This layer is **non-clinical** and **non-inferential**.  
Its purpose is to normalize ambiguity and prevent uncertainty from propagating upward.

### 2. Framework-specific layers (planned / partial)

Higher-level frameworks such as:

- C-SSRS
- PHQ-9

are treated as **interpretive overlays** on top of the core signals.  
They are not hard-coded assumptions.

---

## Deterministic backends

To preserve reproducibility and auditability, the project currently supports **offline backends**:

- **Dummy backend** — minimal, conservative extraction used for smoke testing
- **Rule-based backend** — deterministic pattern matching used to simulate NLP behavior on synthetic cases

These backends do **not** perform clinical inference.  
They exist to validate the pipeline, schemas, and failure modes.

LLM-based backends are intentionally deferred.

---

## Evidence-first outputs

All extracted signals include:

- Explicit presence state (`present`, `absent`, `indeterminate`)
- Evidence spans with character offsets
- Source attribution (rule-based, cue-based, or LLM-based)

This allows downstream users to **inspect why** a signal exists, not just that it exists.

---

## Synthetic cases

The project uses **clinically realistic synthetic cases**, written by a psychiatrist with experience in emergency and urgent care settings.

Each synthetic case:

- Is explicitly labeled as fictional
- Includes sensitive content warnings
- Is used for validation, not training

No real patient data is used.

---

## Minimal GUI

A lightweight Streamlit-based GUI is included to:

- Paste or load full synthetic cases
- Switch between deterministic backends
- Inspect structured outputs
- Visualize extracted evidence

The GUI is a **testing interface**, not a user-facing application.

---

## Safety considerations

DundiePlz intentionally avoids:

- Generating new ideation
- Suggesting methods or means
- Providing advice or recommendations
- Escalating ambiguous signals into conclusions

Ambiguity is preserved when ambiguity exists.

---

## Current status

As of this version:

- Fully local execution
- One-case-at-a-time processing
- Deterministic, auditable outputs
- Explicit handling of temporal references
- Conservative behavior by design

The project is in **early prototype (v0.1)**.

---

## Planned next steps

- Expand synthetic case evaluation set
- Introduce batch processing
- Improve temporal reasoning edge cases
- Formalize framework-specific overlays
- Explore governance and evaluation metrics
- Investigate safe integration of non-local models

---

## Disclaimer

This project is for **research and prototyping purposes only**.

It is **not** intended for clinical use, diagnosis, triage, or patient care.

---

## Author

Developed by a psychiatrist with clinical experience in emergency and urgent care settings, exploring the intersection of psychiatry, NLP, and AI governance.
