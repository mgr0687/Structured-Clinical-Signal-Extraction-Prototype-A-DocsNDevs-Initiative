# 🩺 DonDiePlz - Development Report

![Status](https://img.shields.io/badge/Status-Early%20Prototype-orange)
![Focus](https://img.shields.io/badge/Focus-Safety%20%26%20Governance-blue)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---


12 13 2025 22:00 - 03:33am Brazil 
First Development Report — DonDiePlz 1.0 (Early Prototype)

This is my first development report.

The initial goal of this project was to build a framework-conditional clinical text structuring pipeline, starting with a fully local, deterministic prototype. At this stage, the focus is governance, epistemic limits, and error discovery—not performance, scale, or clinical validity.

Early on, I realized I had underestimated how contextual and subjective psychiatric signals can be, even when mapped to structured instruments. My first implementation attempt felt “dead on arrival”: I had sketched a pipeline that would likely get stuck in an endless loop of underfitting—not because I lacked ML theory, but because I was trying to force highly contextual language into brittle heuristics too early.

That said, I also realized that the prototype can—and arguably should—expose mistakes. Demonstrating how subjectivity and unpredictable external patterns can interfere with rating instruments is itself informative. In other words, part of the value here is to show where structured frameworks fail gracefully, even before we talk about bias.

After this realization, I restarted with a different architecture (the one described in the README). I will have a developer joining soon, but so far I have been using Claude/GPT to assist with the implementation while I drive the clinical constraints and evaluation criteria.

Key difficulties and fixes

The first major difficulty was heuristic design. I initially attempted to include many phrase cues, including Portuguese (pt-BR) expressions and mixed-language triggers. This increased complexity and slowed debugging. I therefore decided to standardize English as the project default and keep non-English cues inert for now.

A second issue emerged around temporal reasoning. I initially overlooked an explicit representation of future time as a separate temporal state. As a result, the dummy extractor incorrectly conflated temporal references (e.g., “tomorrow”) with suicide planning, which is a distinct construct in frameworks like the C-SSRS. This produced false positives where a future-oriented word alone triggered a “plan” signal.

This error was detected using a minimal test with a single input case. The root cause was traced to two factors:

Temporal markers were incorrectly included in the suicide plan heuristic list.

The schema did not support a future temporal state, causing valid model output to be silently downgraded to unknown (this took time to notice and debug).

Both issues were resolved by:

Separating temporal markers from suicide plan markers

Adding future as an explicit value in the Temporal enum (and acknowledging that temporal extraction becomes increasingly ambiguous when the text includes prior attempts, episodes, diagnoses, and treatments)

Ensuring that suicide plan detection requires method/means context, not time alone.


I'm also having difficulty with CHATBOTS. It's very hard to set up a mental health project, even when I make it clear that I'm a doctor who works in the area. I keep getting red flags.



Current status

At the current state, the system:

Runs fully locally

Uses a deterministic dummy LLM client (no external API calls yet)

Processes one case at a time

Produces structured, auditable outputs

Correctly distinguishes temporal references from suicide planning (validated on 1 case so far)

Avoids overreach and unsupported assertions (validated on 1 case so far)

Only one synthetic case has been processed intentionally, to validate correctness before scaling.

Next steps

Next steps will include:

Organizing papers collected from public databases (SciELO, PubMed). Even though the C-SSRS and PHQ-9 are widely used, it is surprisingly difficult to find ready-to-use raw text data. Psychiatry is often “punished” by the lack of objective exams: data is highly contextual and subjective.

Tightening the definition of suicide plan to require explicit self-harm context

Testing a small set of carefully chosen synthetic cases

Gradually expanding toward batch processing

Setting up the project database for tracking inputs/outputs and iterations (I expect this to take time)

At this stage, the priority remains correctness, safety, and interpretability, not coverage or optimization.


12 13 2025 21:12 am Brazil 


Second Project Report

The developer implemented a new feature and fixed several of my files.
As a result, the project now feels more human-centered and extends beyond my initial technical limitations.

I tried to understand which fixes and improvements were introduced.

Before pulling the changes, I reviewed the patched files and asked GPT and Claude for guidance. Im not using other LLMs due to bias-related concerns and red flags that were previously attributed to the use of the “s” word.

From what I could see, the developer also added a preliminary OpenAI API integration for testing purposes.

Here is my understanding so far:

pyproject.toml – the developer added a future-facing OpenAI binding.

scripts/openAI.py – a demo script that calls the OpenAI API and returns a JSON-formatted example.

I noticed that the implementation was using gpt-3.5-turbo, which I assume was chosen due to the small size of our dataset and the exploratory nature of the project.

The response type was configured as json_object. However, I believe my schemas would not scale well with this approach in the long term. It could lead to overlapping fields, loss of sensitivity, or even infinite retry loops. As a consequence, the model might default to “uncertain” too frequently, especially when users provide insufficiently detailed prompts.

For this reason, I am considering switching back to schema-based outputs or, alternatively, implementing proper timeout and retry logic if we decide to continue using JSON mode.

I also realized that I had initially defined only two extraction layers — C-SSRS and PHQ-9 — but that the system actually requires a more fundamental layer running underneath both.

GPT suggested adding a “core layer” beneath the PHQ-9 and C-SSRS layers. Conceptually, this core layer functions as a framework-agnostic, non-clinical normalization stage. Its role is to decompose “NaN” and “indeterminate” outputs into explicit, structured components, preventing ambiguity from propagating into higher-level clinical frameworks.

After reviewing the codebase more carefully, I realized that this core layer already existed under the name core_signals. Because the naming was not explicit, I initially duplicated functionality by recreating a similar schema. This experience reinforced the importance of clear naming conventions when building layered extraction pipelines.

I resolved several minor issues that stemmed from my limited engineering background. While running a basic extraction test script against my synthetic cases — where the expected outputs were already known — I initially encountered an Enum-to-string comparison bug. These kinds of integration and plumbing details are currently my main bottleneck.

Once fixed, the tests executed correctly, but the baseline extractor proved more conservative than I had expected. Given that this is only a prototype, I chose to introduce targeted, case-driven cues derived from my synthetic evaluation set.

At this point, we replaced the naive dummy backend with a deterministic, rule-based backend. This backend does not perform clinical inference; rather, it exists to simulate NLP behavior and validate the extraction pipeline using synthetic cases.

After implementing this change with GPT’s help, the tests passed successfully. However, I then encountered a familiar issue: handling PT-BR text is considerably more cumbersome to implement and maintain.

After packaging everything together, I realized I could add three full, clinically realistic synthetic examples, each accompanied by a sensitive content warning and an explicit fiction/synthetic case disclaimer.

I felt this addition created a strong convergence point between clinical reasoning and engineering practice. For me, this is precisely where “docs and devs” truly meet.

I admit that, at one point, I felt like an expert chess player for having built all of this within roughly 24 hours. It also made me reflect on what well-resourced Stanford or Harvard MSc programs can achieve with dedicated teams and infrastructure.

My developer implemented the pre-LLM (non-local) schema, and our plan is to begin configuring more robust datasets moving forward.

Since I introduced synthetic case prompts, I also added a sensitive content warning.
In addition, I implemented evidence highlighting — an idea originally suggested by Claude, though GPT ultimately provided the stronger implementation.

I must also acknowledge that I was genuinely impressed by GPT’s coding capabilities. It effectively guided a physician with almost no formal programming background into building a functional, structured prototype.

I hope that both of my reports prove useful.
Physicians and developers will be working increasingly closely, and this project reflects that convergence.

DR EDSON HERINGER
Psychiatrist & AI Researcher/Bridger with a focus on Clinical Safety