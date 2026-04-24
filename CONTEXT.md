# Technical Dictation Repair

Technical Dictation Repair turns a raw Voxtype transcription into insertion-ready dictated text. It exists to repair predictable transcription defects while preserving the speaker's intended meaning.

## Language

**Raw Voxtype Transcription**:
Text produced by Voxtype before this system changes it.
_Avoid_: source text, dirty text, prompt input

**Insertion-Ready Dictated Text**:
Text ready for Voxtype to type or paste into the active application.
_Avoid_: cleaned text, final answer, rewritten text

**Repair**:
The domain operation that converts a **Raw Voxtype Transcription** into **Insertion-Ready Dictated Text**.
_Avoid_: rewrite, answer, summarize, generic cleanup

**Post-Processing**:
The Voxtype integration phase after transcription and before output.
_Avoid_: all text transformation, model call

**Minimal Accurate Repair**:
The default stance of making the fewest changes necessary to produce accurate **Insertion-Ready Dictated Text**.
_Avoid_: conservative cleanup, polishing, editing

**Repair Policy**:
Durable rules that define what **Repair** may and must not change.
_Avoid_: prompt, style guide

**Repair Asset**:
An editable source of repair behavior such as policy, prompt, glossary, correction rules, examples, or profiles.
_Avoid_: memory, transcript history

**Glossary**:
Canonical technical terms and preferred spellings or casing.
_Avoid_: corrections, replacements

**Correction Rule**:
A known mistaken phrase mapped to its intended repair.
_Avoid_: glossary entry, model guess

**Repair Example**:
A curated raw-to-repaired example that demonstrates expected behavior.
_Avoid_: test case, correction rule

**Repair History**:
An append-only SQLite record of repair attempts and metadata.
_Avoid_: memory, source of truth

**Repair Observation**:
One stored event containing raw text, repaired text, metadata, and repair outcome.
_Avoid_: transcript, candidate

**Correction Candidate**:
An observed repair opportunity that may deserve durable asset support after human review.
_Avoid_: approved rule, automatic learning

**Candidate Review Queue**:
An asynchronous human review surface generated from stored **Correction Candidates**.
_Avoid_: interruption, required workflow, source of truth

## Relationships

- A **Raw Voxtype Transcription** is passed to **Repair** during **Post-Processing**.
- **Repair** produces exactly one **Insertion-Ready Dictated Text** output for each live call.
- **Repair** is governed by **Repair Assets**, not by **Repair History**.
- A **Correction Rule** is more authoritative than a **Glossary** entry for known mistakes.
- **Repair History** stores **Repair Observations** for debugging, replay/evaluation, and candidate mining.
- A **Correction Candidate** may become a **Correction Rule**, **Glossary** entry, **Repair Example**, profile-specific asset, or rejected no-op after review.
- The **Candidate Review Queue** is generated from SQLite; SQLite is authoritative for candidate state.

## Example dialogue

> **Dev:** "When Voxtype transcribes `OMACHI supports LLMMs in CI CD workflows`, should **Repair** rewrite the sentence?"
> **Domain expert:** "No. Use **Minimal Accurate Repair**: fix the obvious transcription defects to `Omarchy supports LLMs in CI/CD workflows`, but preserve my meaning and wording."
>
> **Dev:** "If the model is unsure whether `q and` means `Qwen`, should it ask or annotate the output?"
> **Domain expert:** "No. Preserve the raw phrase in the insertion-ready text and record a **Correction Candidate** for later review."

## Flagged ambiguities

- "Conservative" was too vague; resolved to **Minimal Accurate Repair**.
- "Post-processing" was overloaded; resolved to the Voxtype integration phase, while **Repair** names the core domain behavior.
- "Learning" must not silently mutate durable assets; resolved to **Correction Candidates** gathered for asynchronous human review.
- "SQLite" is authoritative for stored candidates, while Markdown is only the generated **Candidate Review Queue** surface.
