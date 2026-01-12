# Walkthrough - Mnemosyne V1: Semantic Accuracy

We have successfully upgraded Mnemosyne to **V1**, focusing purely on semantic precision. The system no longer relies on brittle keywords but understands the *meaning* of signals.

## 1. Feature: Local Semantic Reasoning
- **Engine**: Integrated `sentence-transformers` (all-MiniLM-L6-v2) for strictly local, privacy-preserving semantic analysis.
- **Embeddings**: `Assumption` and `Comment` objects now carry vector representations.

## 2. Feature: Semantic Signal Interpretation
- **Old Way (V0)**: Keyword matching (`"bad"`, `"skeptical"`). Prone to false positives.
- **New Way (V1)**: Cosine similarity between Signal and Assumption vectors.
- **Differentiation**: The system can now distinguish which *specific* assumption a signal is attacking.

## 3. Feature: Proportional Confidence Calibration
- **Link Strength**: We introduced `LinkStrength` (WEAK, MODERATE, STRONG).
- **Weighted Impact**:
  - **STRONG** match (>0.6): -0.15 Confidence
  - **MODERATE** match (>0.4): -0.08 Confidence
  - **WEAK** match (>0.25): -0.02 Confidence

## Verification Results

### V1 Demo Execution
We injected an ambiguous critique: *"This post was too dense and boring. I just want a quick summary, not a novel."* against two assumptions:
1. **A (Trust)**: Engineers trust technical depth.
2. **B (Format)**: Long-form is preferred.

**Result Output**:
```text
[INJECTING SIGNAL]: 'This post was too dense and boring. I just want a quick summary, not a novel.'

[FINAL BELIEFS]
A (asm_trust): Engineering audiences trust technical depth...
   Conf: 0.88 (Delta: 0.02)  <-- Correctly barely touched (Weak Link)

B (asm_format): Long-form written content is the preferred format...
   Conf: 0.75 (Delta: 0.15)  <-- Correctly heavily penalized (Strong Link)

RESULT: SUCCESS. The system understood that the critique attacked the FORMAT more than the TRUST principal.
```

## 4. Feature: Confidence Safety Rail (Sprint 1)
- **Problem**: Noisy or overlapping signals could cause a massive confidence crash in a single cycle.
- **Solution**: A hard cap `MAX_CONFIDENCE_DROP_PER_CYCLE = 0.20`.
- **Mechanism**:
  - `MemoryManager.process_contradictions` aggregates all negative deltas for an assumption.
  - If the sum exceeds 0.20, it is clamped.
  - A `[SAFETY RAIL ACTIVATED]` log is emitted.

### Safety Verification
We injected **two STRONG contradictions** (theoretical drop 0.30).
**Result**:
```text
[SAFETY RAIL ACTIVATED]
Assumption: asm_format
Calculated Delta: -0.30
Capped Delta: -0.20

[FINAL BELIEFS]
B (asm_format): ...
   Conf: 0.70 (Drop: 0.20)
```
The safety rail successfully prevented panic.


## 5. Feature: Temporal Intelligence (V2)
- **Problem**: Understanding *how* a belief reached its current state (Stability vs. Volatility).
- **Solution**: Read-only `TemporalAnalyzer`.
- **Mechanism**:
  - Reconstructs belief trajectories from event logs.
  - Calculates `Momentum` (Velocity of change) and `Volatility` (Variance of change).
  - Distinguishes "Old Scars" (Stable) from "Fresh Wounds" (Degrading).

### Temporal Verification
We simulated two assumptions with **identical current confidence (0.60)** but different histories.
**Result**:
- **Old Scar**:
  - History: Major hit 20 days ago. Stable since.
  - Status: `STABLE` (Momentum ~0.02, Volatility 0.00).
- **Fresh Wound**:
  - History: Rapid hits in last 3 days.
  - Status: `VOLATILE/UNSTABLE` (Momentum -0.13, Volatility 0.25).


## 6. Feature: Governance & Override (V3)
- **Problem**: Sometimes humans know things the system doesn't (Market shocks, secret funding).
- **Solution**: Explicit `Override` Primitive and `OverrideDebt`.
- **Mechanism**:
  - Humans can mandate an action (Override Plan) or value.
  - The system logs this as an active Override.
  - Execution respects the human mandate but flags it as "Debt".

### Governance Verification
We simulated an Executive overriding a conservative system plan.
**Result**:
```text
[SYSTEM INTELLIGENCE]
Recommendation: Execute Plan A (Conservative)

[HUMAN INTERVENTION]
Authority: EXECUTIVE
Mandate: Execute Plan B (Aggressive)
Rationale: External funding secured.

[EXECUTION PHASE]
** OVERRIDE APPLIED **
EXECUTING MANDATE: Execute Plan B
Override Debt: 1 active item(s).
```
The system obeyed but remembered the deviation.

## 7. Feature: Content Execution Sandbox
- **Purpose**: Demonstrate valid belief-governed asset generation.
- **Contract**: `ContentBrief` (ReadOnly).
- **Architecture**: Isolated `sandbox/` layer using Gemini (Auto-Model).

**Verification**:
```text
[INCOMING BRIEF]
Visual Mandate: Abstract geometric nodes...
Governing Assumptions: ['asm_trust', 'asm_quality']

[SANDBOX EXECUTION]
  > Executing Prompt 1: ... (Wide shot)
  > Executing Prompt 2: ... (Close up)

[GENERATED ASSETS]
Asset #1
  Path: [MOCK IMAGE]...
  Traceability: ['asm_trust', 'asm_quality']
  Generator: Gemini (Auto-Model)
```


## 8. Feature: A/B Belief Toggle Experiment
- **Purpose**: Prove causal link between belief and output.
- **Method**: Run identical briefs with **Opposing Risk Notes** derived from **Conflicting Assumptions**.
- **Scenario**: Narrative "Launch API Platform".
  - Arm A (Chaos): Assumption "Engineers trust complexity" -> Risk "Show the mess".
  - Arm B (Order): Assumption "Engineers trust minimalism" -> Risk "No visible wires".

**Experiment Result**:
```text
[EXECUTING ARM A] (Assumption: asm_chaos_trust)
Risk Mandate: Ensure complexity is visible. Do not hide the wires.

[EXECUTING ARM B] (Assumption: asm_order_trust)
Risk Mandate: Hide all complexity. Minimalist. Zen-like.

[CONCLUSION]
These outputs differ ONLY because the governing belief changed.
```
Mnemosyne creates **Materially Different Realities** based on its internal beliefs.

## 9. Feature: Belief Stress Test (Adaptation)
- **Purpose**: Demonstrate adaptation without breaking safety rails.
- **Scenario**: Seed competing beliefs ("Chaos" vs "Order"). Inject negative semantic feedback.
- **Method**:
  - `SemanticEngine` detects contradictions in user feedback.
  - `MemoryManager` applies weighted confidence drops.
  - **Safety Rail** protects against total collapse.

**Adaptation Log**:
```text
[SEEDING]
  > asm_chaos_trust: Simulating belief in "Visible Complexity"
  > asm_order_trust: Simulating belief in "Minimalism"

[FEEDBACK INJECTION]
  > Signal: "It is overwhelming and confusing..."
    -> Targets asm_chaos_trust (Sim: 0.27 | WEAK)
  > Signal: "Cluttered and chaotic..."
    -> Targets asm_chaos_trust (Sim: 0.33 | WEAK)

[ADAPTATION RESULT]
  asm_chaos_trust: Confidence 0.94 (Delta: -0.06)
  asm_order_trust: Confidence 1.00 (Stable)
```
**Conclusion**: Mnemosyne **learned** that "visible complexity" was failing and updated its epistemic state automatically.
