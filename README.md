# Mnemosyne

**Mnemosyne** is an organizational epistemic system designed to bridge the gap between AI-driven reasoning and institutional memory. It treats "Assumptions" as first-class, risk-weighted beliefs that evolve over time based on semantic evidence.

## Core Philosophy
1. **Mnemosyne remembers.** It never forgets why a strategy changed.
2. **Mnemosyne reasons.** It interprets feedback semantically, not through brittle keywords.
3. **Mnemosyne cautions.** It enforces epistemic safety rails to prevent belief collapse.
4. **Humans decide.** The system provides transparency and trajectory; humans maintain final authority through an explicit governance layer.

---

## Technical Stack
- **Language**: Python 3.10+
- **Environment**: [uv](https://github.com/astral-sh/uv) (Strictly enforced)
- **Embeddings**: Local `sentence-transformers` (all-MiniLM-L6-v2)
- **Architecture**: Epistemic Hierarchy (V0-V3)

---

## Features & Implementation

### V0: Belief Core (Authoritative)
The foundation of the system. Strategies are anchored to explicit **Assumptions**.
- **Risk Derivation**: Automatically escalas risk based on belief confidence.
- **Strategic Pivots**: Records the *why* behind every change in direction.

```python
# Sample: Registering an Assumption
asm = Assumption(
    id="asm_trust",
    statement="Engineering audiences trust technical depth over marketing polish.",
    current_confidence=0.90,
    risk_level=RiskLevel.LOW
)
memory.add_assumption(asm)
```

### V1: Semantic Accuracy & Safety
Replaces heuristic matching with local vector similarity.
- **Link Strength**: WEAK, MODERATE, or STRONG associations between signals and beliefs.
- **The Safety Rail**: Aggregated confidence loss is capped at **0.20 per cycle** to prevent panic.

```python
# V1 Logic: Weighted Invalidation
# If a signal has a 'Strong' semantic overlap with an assumption:
# confidence_delta = 0.15 
# If two strong signals arrive in one cycle (0.30 total), the Safety Rail clamps the drop to 0.20.
```

### V2: Temporal Intelligence (Observational)
Reconstructs belief trajectories from event logs to understand health, not just state.
- **Momentum**: Velocity of confidence change.
- **Volatility**: Frequency and variance of updates.

```python
# Sample: Querying Trajectory
analyzer = TemporalAnalyzer()
analysis = analyzer.analyze_assumption_trajectory(current_conf, created_at, logs)
print(f"Status: {analysis['metrics'].status_label}") # e.g., "Degrading" or "Stable"
```

### V3: Governance & Override (Authority)
Defines the boundary between system reasoning and human mandate.
- **Authority Levels**: Observer, Strategist, Executive.
- **Override Debt**: Tracking how far the human mandate has drifted from system logic.

```python
# Sample: Human Executive Override
override = Override(
    target_id="plan_launch_q1",
    previous_state="Plan A (Conservative)",
    override_action="Execute Plan B (Aggressive)",
    rationale="Strategic funding secured.",
    authority_level=AuthorityLevel.EXECUTIVE
)
memory.add_override(override)
```

---

## Sample Output

### The Safety Rail in Action
```text
[INJECTING SIGNALS]
1. 'Signal A: Strong Contradiction' (Delta: 0.15)
2. 'Signal B: Strong Contradiction' (Delta: 0.15)

[SAFETY RAIL ACTIVATED]
Assumption: asm_format
Calculated Delta: -0.30
Capped Delta: -0.20
Reason: Single-cycle confidence drop exceeded allowed maximum.
```

### Temporal Differentiation
```text
Assumption: OLD SCAR (Conf: 0.60)
  Status: STABLE
  History: Major hit 20 days ago. Equilibrium since.

Assumption: FRESH WOUND (Conf: 0.60)
  Status: VOLATILE/UNSTABLE
  History: Hit 3 times in last 48 hours. Active decay.
```

---

## System Invariants
- **Frozen Core**: The Assumption schema and confidence update math are immutable.
- **Auditable History**: Overrides and contradictions sit alongside history; they never delete it.
- **Semantic First**: No keyword-based logic is permitted in the Interpret stage.

---

## Development
This project manages dependencies using `uv`. 

```bash
# Setup
uv sync

# Run the Demo
uv run main.py
```

*Mnemosyne: Because institutional memory shouldn't be a guess.*