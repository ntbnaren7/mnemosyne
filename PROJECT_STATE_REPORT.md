# Mnemosyne: Project State Report
*Last Updated: 2026-01-12*

This document serves as the high-level context sync for Mnemosyne. It summarizes the project's evolution, current capabilities, and architectural boundaries.

---

## 1. System Definition
Mnemosyne is an **Organizational Epistemic Operating System**. It tracks institutional beliefs (Assumptions), reasons about them semantically, ensures safety through confidence rails, and manages human governance over automated execution.

---

## 2. Completed Milestones (The Evolution)

### [COMPLETED] V0: The Belief Core
- **Primitives**: `Assumption`, `Insight`, `StrategyChange`.
- **Function**: Defined how strategies are anchored to explicit, risk-weighted bets.
- **Outcome**: Established the first "Why" layer for strategy.

### [COMPLETED] V1: Semantic Accuracy
- **Engine**: Local `sentence-transformers` (all-MiniLM-L6-v2).
- **Function**: Replaced keyword matching with cosine similarity for signal interpretation.
- **Safety**: Introduced the `MAX_CONFIDENCE_DROP_PER_CYCLE = 0.20` cap to prevent belief collapse.

### [COMPLETED] V2: Temporal Intelligence
- **Intelligence**: `TemporalAnalyzer`.
- **Function**: Reconstructs belief trajectories to determine **Momentum**, **Volatility**, and **Health** (e.g., "Stable" vs. "Volatile/Unstable").
- **Constraint**: Purely observational (Read-only).

### [COMPLETED] V3: Governance & Override
- **Authority**: `AuthorityLevel` (Observer, Strategist, Executive).
- **Function**: Explicitly allows humans to mandate actions that contradict system reasoning.
- **Debt**: Records "Override Debt" so the system remembers where it was overruled.

### [COMPLETED] Content Execution Sandbox
- **Module**: `sandbox/` (Architecturally isolated from Core).
- **Function**: Consumes `ContentBrief` to generate assets via Gemini.
- **Constraint**: Must NOT specify image model names; uses dynamic discovery to avoid API failures.
- **Traceability**: Every generated image is tagged with the **Governing Assumption ID**.

---

## 3. Current System State
As of now, Mnemosyne can:
1. **Reason**: Turn a spreadsheet of comments into a semantic critique of a strategy.
2. **Protect**: Refuse to let a single bad day zero out a long-held belief (Safety Rail).
3. **Analyze**: Warn a human if a belief is "Degrading" based on current trajectory.
4. **Govern**: Execute a high-risk plan mandated by an Executive, while logging the disagreement.
5. **Execute**: Create creative assets (images) that are mathematically linked to a specific institutional belief.

---

## 4. Key Invariants (Do Not Change)
- **Epistemic Hierarchy**: Belief Core > Calibration/Safety > Temporal Intelligence > Consumers.
- **Isolation**: Mnemosyne Core (Logic) must never depend on the Sandbox (Execution).
- **Authority**: Mnemosyne explains; Humans decide.

---

## 5. Latest Technical Changes
- Created `ContentBrief` schema in `schemas.py`.
- Developed `sandbox/gemini_client.py` for model-agnostic image generation.
- Implemented `ContentExecutor` to translate briefs into prompts.
- Verified flow via `run_sandbox_demo.py`.

---

## 6. Verification
Run the following to see the latest full-stack logic:
```bash
uv run run_sandbox_demo.py
```
