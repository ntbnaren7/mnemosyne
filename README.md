# Mnemosyne: Organizational Epistemic System

**Mnemosyne** is a powerful framework designed to bridge the gap between AI-driven reasoning and institutional memory. It treats strategic "Assumptions" as first-class, risk-weighted beliefs that evolve over time based on semantic evidence, governing the entire lifecycle of content strategy and execution.

---

## 🏛️ Project Workflow: The Epistemic Cycle

Mnemosyne follows a structured 5-stage workflow to ensure every piece of content is grounded in institutional knowledge:

1.  **Reason**: The **Semantic Engine** identifies relevant institutional beliefs (Assumptions) based on the user's input topic.
2.  **Plan**: The **Monthly Production Agent** orchestrates a high-level content plan (e.g., 5-week schedule) governed by the active beliefs.
3.  **Execute**: The **Sandbox Executor** translates content briefs into high-fidelity visual and narrative assets using the Gemini/Imagen 3 API.
4.  **Edit (Magic Decomposition)**: Generated images are passed through the **Layered Editing Engine**, which uses AI to decompose the flat image into editable layers (Text & Objects).
5.  **Refine**: Humans interact with the **Web Orchestrator** to override, audit, or manually polish the generated output, feeding "Override Debt" back into the system for transparency.

---

## 🏛️ Core Philosophy

1.  **Memory as Foundation**: Mnemosyne never forgets *why* a strategy changed. Every pivot is anchored to an evolving belief.
2.  **Semantic Reasoning**: It interprets feedback and signals semantically, moving beyond brittle keyword matching to understand deep contextual contradictions.
3.  **Epistemic Safety**: Built-in safety rails prevent "belief collapse" by capping confidence volatility during high-pressure cycles.
4.  **Governance First**: A clear hierarchy (V0-V3) ensures humans remain the final authority, with explicit tracking of "Override Debt."

---

## 🛠️ Technical Stack

Mnemosyne uses a state-of-the-art stack for both reasoning and asset manipulation:

### Core Reasoning
-   **Language**: Python 3.10+
-   **Package Manager**: [uv](https://github.com/astral-sh/uv) (Strictly enforced performance)
-   **Embeddings**: Local `sentence-transformers` (`all-MiniLM-L6-v2`) for private, local semantic search.
-   **Logic Engine**: Pure Python core with zero-dependency immutable schemas.

### Content & Visuals
-   **Generation**: Gemini 1.5 Pro & Imagen 3 (via `google-genai` SDK).
-   **Decomposition**: **MobileSAM** (Segment Anything Model) for autonomous object extraction.
-   **OCR**: **EasyOCR** for detecting and lifting text from generated images into editable layers.
-   **Image Processing**: **OpenCV** for inpainting and background reconstruction during decomposition.

### Interfaces
-   **Orchestration**: **Streamlit** for the high-level epistemic dashboard.
-   **API Layer**: **FastAPI** for handling heavy decomposition tasks and serving assets.
-   **Frontend**: Vanilla JS/HTML/CSS for the layered image editor.

---

## 🏗️ The Epistemic Stack (V0 - V3)

### V0: Belief Core
The foundation where strategy meets assumptions.
-   **Risk Derivation**: Scales risk levels based on belief confidence.
-   **Strategic Anchoring**: Every content brief is anchored to a specific set of active assumptions.

### V1: Semantic Accuracy & Safety
-   **Vector Similarity**: Uses local embeddings to calculate "Link Strength" between signals and beliefs.
-   **The Safety Rail**: Automatically clamps confidence drops (e.g., max 0.20 per cycle) to ensure stability during market turbulence.

### V2: Temporal Intelligence
-   **Trajectory Analysis**: Reconstructs belief history to differentiate between a stable "Old Scar" and a volatile "Fresh Wound."
-   **Momentum & Volatility**: Measures the velocity of confidence changes.

### V3: Governance & Mandate
-   **Executive Overrides**: Allows humans to force actions that contradict system reasoning.
-   **Override Debt**: Tracks the divergence between human mandates and system logic for future auditing.

---

## 🎨 Magic Layered Editing

Mnemosyne doesn't just produce flat images; it creates **fully editable creative assets**.

-   **Autonomous Decomposition**: Using MobileSAM and EasyOCR, the system "lifts" objects and text from generated images into independent layers.
-   **Inpainted Backgrounds**: When an object is "lifted," Mnemosyne uses OpenCV-based inpainting to reconstruct the background behind it.
-   **Live Manipulation**: Once decomposed, users can move, resize, or replace text and objects while keeping the underlying brand logic intact.
-   **Traceability**: Every individual layer (object/text) maintains its metadata link back to the `Assumption ID` that inspired its generation.

---

## 🚀 Getting Started

### Prerequisites
1.  Install [uv](https://github.com/astral-sh/uv).
2.  Set your `GEMINI_API_KEY` in a `.env` file.

### Installation
```bash
uv sync
```

### Running the System

**1. The Web Orchestrator (Demo Platform)**
The primary interface for running end-to-end content generation governed by beliefs.
```bash
uv run streamlit run app.py
```

**2. Core Reasoning Demo**
```bash
uv run main.py
```

**3. A/B Belief Experiment**
Proves the causal link between internal beliefs and generated visual output.
```bash
uv run run_ab_experiment.py
```

**4. Belief Stress Test**
Demonstrates how the system adapts and pivots beliefs based on incoming semantic feedback.
```bash
uv run run_stress_test.py
```

---

## 📜 System Invariants

-   **Frozen Core**: The fundamental reasoning logic and confidence math are immutable.
-   **Auditable History**: Overrides and contradictions are preserved alongside history; they never delete it.
-   **Isolated Execution**: Core reasoning logic exists independently of the generation sandbox.

---

*Mnemosyne: Because institutional memory shouldn't be a guess.*