# Adaptive Resume ATS Scorer

A **production-grade, deterministic, and explainable Resume ATS Scoring System** built in Python using an **Evolutionary SDLC model**.  
The system incrementally evolves from basic resume parsing to role-aware and NLP-assisted analysis while remaining **usable, testable, and backward-compatible at every phase**.

This project is designed to reflect **real-world ATS evaluation logic**, not black-box AI scoring.

---

## Key Capabilities

- Deterministic ATS Score (0–100)
- Section-wise scoring with transparent weights
- Role-based evaluation using configurable role definitions
- NLP-assisted keyword relevance analysis
- Grammar and readability assessment
- ATS compatibility and structural validation
- Explicit penalties and warnings (no silent deductions)
- Fully explainable, auditable outputs
- Phase-gated unit testing
- Backend-first, API-ready architecture

---

## Design Principles

- Logic-first, AI-later approach  
- No black-box scoring  
- AI never affects numeric scores  
- Backward compatibility is mandatory  
- Configuration over hardcoding  
- Clear separation of concerns  
- Models act as data contracts  
- Production-grade engineering discipline  

---

## Tech Stack

- Python 3.x  
- NLP: TF-IDF / semantic similarity  
- YAML / JSON for configuration  
- PyTest for unit testing  

---

## Project Structure (Simplified)

src/
├── parser/           # Resume ingestion and section detection
├── scoring/          # Deterministic ATS scoring logic
├── roles/            # Role definitions and role-based scoring
├── nlp/              # Keyword relevance and semantic analysis
├── language/         # Grammar and readability analysis
├── ats/              # ATS compatibility and structural checks
├── models/           # Data contracts
├── pipeline/         # Orchestration pipelines
├── utils/            # Logging, helpers, exceptions
tests/
├── test_phase0 ... test_phase6
data/
├── input/
├── output/
├── sample_resumes/



---

## Evolutionary Phase Overview

### Phase 0 – Environment Setup
Stable environment, logging, configuration, and test scaffolding.

### Phase 1 – Resume Parsing
PDF/DOCX ingestion, text extraction, section detection, structured output.

### Phase 2 – Baseline ATS Scoring
Rule-based section completeness and keyword presence scoring.

### Phase 3 – Role-Adaptive Scoring
Role-specific keyword sets and configurable section weighting.

### Phase 4 – NLP Keyword Relevance
TF-IDF / semantic similarity scoring and keyword stuffing penalties.

### Phase 5 – Grammar & Readability
Grammar checks and readability metrics generated independently.

### Phase 6 – ATS Compatibility Validation
Detection of ATS-breaking elements and explicit structural penalties.

(Phases beyond 6 are intentionally not implemented yet.)

---

## Installation

### 1. Clone the Repository
git clone https://github.com/TamalBht/ATS_prod

cd ATS_prod

### 2. Create and Activate Virtual Environment
python -m venv venv
source venv/bin/activate # Linux / macOS
venv\Scripts\activate # Windows


### 3. Install Dependencies

Optional editable install:

---

## Usage Examples

### ATS Compatibility Check
python test_components/ats_compatibility_check.py
--resume data/sample_resumes/sample.pdf


---

## Output

All outputs are **JSON-first** and stored in `data/output/`.  
Each output includes explicit scores, penalties, warnings, and explanations.

No hidden adjustments.  
No opaque scoring.

---

## Testing

Run all tests:
Run phase-wise tests:


Each evolution phase is independently testable and phase-gated.

---

## What This Project Does NOT Do

- No resume rewriting or formatting
- No AI-driven numeric scoring
- No candidate ranking or comparison
- No recruiter feedback loop
- No frontend or UI
- No API layer (yet)
- No ATS vendor integration
- No fairness or bias reweighting logic

---

## Intended End Goal

To build a **resume-grade, enterprise-aligned ATS intelligence system** that:

- Produces deterministic and explainable scores
- Evolves safely using an Evolutionary SDLC model
- Separates logic from AI
- Remains auditable and production-ready
- Can be extended with APIs or human-in-the-loop feedback

---

