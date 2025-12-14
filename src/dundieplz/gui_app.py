from __future__ import annotations

import json
from typing import Literal, List
from html import escape

import streamlit as st

from dundieplz.extract.extractor import Extractor
from dundieplz.extract.llm_client import DummyLLMClient
from dundieplz.extract.rule_llm_client import RuleLLMClient
from dundieplz.schemas.extractor_schema import EvidenceSpan


# --------------------------------------------------
# Types / constants
# --------------------------------------------------

BackendName = Literal["dummy", "rules"]

DISCLAIMER_TEXT = (
    "THIS IS A FICTIONAL CASE PRODUCED BY A PHYSICIAN WITH FORMAL PSYCHIATRY "
    "TRAINING AND EXPERIENCE IN MULTIPLE EMERGENCY AND URGENT CARE SETTINGS IN BRAZIL. "
    "THIS TOOL IS FOR TECHNICAL DEMONSTRATION AND RESEARCH PURPOSES ONLY."
)

SYNTHETIC_CASES = {
    "0101": {
        "title": "Case 0101 (High) - Grief, distress, explicit denial",
        "text": """Outpatient psychiatric assessment attached to a psychiatric hospital with emergency medical services. Patient evaluated by a Psychiatry Resident Physician.

M.F.A., 58 years old, female, homemaker.

Chief complaint and duration: "I have had depression for years, but it got worse after my husband died."

Patient presents to outpatient psychiatric care accompanied by her son, tearful, sobbing.

Reports prior treatment for a mood disorder for approximately 20 years, currently on desvenlafaxine 50 mg. She reports that the initial depressive episode began after the loss of the family dog, Nelson.

Reports significant worsening of symptoms three months ago following the death of her husband due to stroke (per patient report).

"I cry day and night," she states.

Associated symptoms include early insomnia and non-restorative sleep. Denies somatic complaints.

During the mental status examination, patient displays marked emotional distress with intense crying, interspersed with brief moments of emotional reorganization.

Neutral, dark clothing. Appropriate behavior. Good rapport with accompanying family member.

She also reports intrusive thoughts related to grief and longing, stating: "I want to die without him," verbatim.

Her son expressed concern and requested hospitalization. The patient agrees to inpatient care; however, she explicitly denies suicidal ideation.

Speech is coherent, with tragic content, normal flow, mood-congruent, and without perceptual disturbances.

Denies suicidal ideation.

Family history: Mother deceased 15 years ago. Father alive with Alzheimer's disease. Married, mother of two biological children. Lives with husband, two children, and father. Grandfather with history of alcohol use disorder.

Personal medical history: Type 1 diabetes mellitus on metformin (dose unknown). Desvenlafaxine 50 mg once daily. Two cesarean sections. Breast implants. Denies medication allergies.

Diagnosis: Major Depressive Episode, severe, without psychotic features.

Plan: Request laboratory workup and inpatient psychiatric admission under my care."""
    },
    "0102": {
        "title": "Case 0102 (Low) - Unequivocal suicide attempt",
        "text": """Emergency department case report. Patient evaluated by an emergency physician.

M.S.R.C., male, 30 years old, single, electrical technician.

Chief complaint: SUICIDE ATTEMPT - EXOGENOUS INTOXICATION.

Patient arrived by wheelchair, brought by family members in an emergency situation.

Mother reports that the patient is a user of multiple substances (alcohol, crack cocaine, marijuana) and had been followed at a public outpatient service for six months, with five months of reported abstinence.

"He had really stopped, doctor," she states.

She reports that the patient had been isolated in his room for over one day and, during lunch, expressed: "I cause too much trouble." "I'm a burden to everyone."

Mother reports finding the patient hyporesponsive, lying in bed, pale, cold, diaphoretic, with white-greenish frothy secretion around the lips and oropharynx.

According to the accompanying family member, the patient was taking: Naltrexone (dose unknown), Valproic acid 1 g every 12 hours, Diazepam 5 mg every 8 hours, Risperidone 1 mg every 8 hours, Chlorpromazine 25 mg at bedtime.

At triage: Heart rate 60 bpm, blood pressure 70/20 mmHg, Glasgow Coma Scale 6, oxygen saturation 71 percent, temperature 36 C.

Diagnosis: Exogenous intoxication.

Conduct: Endotracheal intubation.

Outcome: Patient progressed to shock, cardiac arrest, and death."""
    },
    "0103": {
        "title": "Case 0103 (Medium) - EMS post-mortem reconstruction",
        "text": """Emergency medical service (ambulance) report - SAMU, Londrina. Patient was not evaluated by a physician prior to death.

J.L.F.C.

Ambulance occurrence #2211. Location redacted. Monday, December 25, 2024.

A bystander contacted emergency services in the morning reporting that they had heard a gunshot. The caller was instructed to contact Military Police.

Police units responded and subsequently reactivated emergency medical services, initially requesting ambulance support due to a possible firearm injury to the left temporal region.

An advanced life support unit (mobile ICU) was dispatched at 23:33 to the location, where J.L.F.C. was found without vital signs. Death was confirmed, and referral to the Medical Examiner's Office was requested.

A statement was obtained from the patient's father, who reported that the patient had been experiencing problems with depression, had posted farewell messages on social media, and had left a letter.

Death was confirmed, and the body was referred to the Medical Examiner's Office.

Cause of death: Cardiorespiratory arrest / Traumatic brain injury / Depression - firearm injury. Final cause pending official autopsy report."""
    },
}


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def make_extractor(backend: BackendName) -> Extractor:
    if backend == "rules":
        return Extractor(llm_client=RuleLLMClient())
    return Extractor(llm_client=DummyLLMClient())


def load_case(case_id: str) -> None:
    st.session_state["input_text"] = SYNTHETIC_CASES[case_id]["text"]


def collect_all_evidence(result) -> List[EvidenceSpan]:
    evidence: List[EvidenceSpan] = []
    for value in result.signals.__dict__.values():
        if hasattr(value, "evidence"):
            evidence.extend(value.evidence)
    return evidence


def build_highlighted_html(text: str, evidence: List[EvidenceSpan]) -> str:
    spans = sorted(
        [e for e in evidence if e.start is not None and e.end is not None],
        key=lambda e: e.start,
    )

    html = ""
    cursor = 0

    for ev in spans:
        html += escape(text[cursor:ev.start])
        tooltip = f"source={ev.source}"
        html += (
            f"<mark title='{tooltip}' "
            f"style='background-color:#ffe066;'>"
            f"{escape(text[ev.start:ev.end])}</mark>"
        )
        cursor = ev.end

    html += escape(text[cursor:])
    return html


# --------------------------------------------------
# UI
# --------------------------------------------------

st.set_page_config(page_title="DundiePlz - Test GUI", layout="wide")

st.title("DundiePlz - Minimal Test GUI")
st.caption("Prototype interface for testing signal extraction pipelines (offline backends).")

st.warning(DISCLAIMER_TEXT)
ack = st.checkbox("I understand and acknowledge this disclaimer.")

if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

col_left, col_right = st.columns([2, 1], gap="large")

with col_right:
    st.subheader("Settings")
    backend = st.radio("Backend", options=["rules", "dummy"], index=0, disabled=not ack)
    show_meta = st.checkbox("Show meta", value=True, disabled=not ack)
    show_cue_hits = st.checkbox("Show cue_hits", value=True, disabled=not ack)
    pretty = st.checkbox("Pretty JSON", value=True, disabled=not ack)

    run_button = st.button(
        "Run extraction",
        type="primary",
        use_container_width=True,
        disabled=not ack,
    )

with col_left:
    st.subheader("Input")

    st.caption("Load synthetic cases:")
    b1, b2, b3 = st.columns(3)
    with b1:
        st.button("Case 0101", on_click=load_case, args=("0101",), disabled=not ack)
    with b2:
        st.button("Case 0102", on_click=load_case, args=("0102",), disabled=not ack)
    with b3:
        st.button("Case 0103", on_click=load_case, args=("0103",), disabled=not ack)

    text = st.text_area(
        "Clinical note / text",
        key="input_text",
        height=320,
        disabled=not ack,
    )

st.divider()

if run_button:
    if not text.strip():
        st.warning("Please provide some input text.")
    else:
        extractor = make_extractor(backend)
        result = extractor.extract(text)

        st.subheader("Evidence Highlighting")
        evidence = collect_all_evidence(result)
        highlighted_html = build_highlighted_html(text, evidence)
        st.markdown(highlighted_html, unsafe_allow_html=True)

        st.divider()

        payload = result.model_dump(mode="json")
        if not show_meta:
            payload.pop("meta", None)
        if not show_cue_hits:
            payload.pop("cue_hits", None)

        st.subheader("Output")
        if pretty:
            st.code(json.dumps(payload, indent=2), language="json")
        else:
            st.write(payload)

        st.success("Extraction completed.")
else:
    if not ack:
        st.info("Please acknowledge the disclaimer to enable inputs.")
    else:
        st.info("Load a case or enter text, then run extraction.")
