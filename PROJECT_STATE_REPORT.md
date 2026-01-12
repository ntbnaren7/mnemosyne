# Mnemosyne: Update for AI Model Sync
*Status: V3 Governance & Content Execution Sandbox Complete*

This update summarizes the current state of Mnemosyne and the latest architectural additions.

---

## 1. Latest Implementations

### Governance & Authority (V3)
- **Explicit Override System**: Humans can now explicitly mandate actions (e.g., "Force Plan B") that contradict the AI's internal reasoning.
- **Authority Levels**: Introduced `Executive`, `Strategist`, and `Observer` roles.
- **Dissent Tracking**: The system calculates "Override Debt"—logging where and why a human diverged from the system's recommended belief or path.

### A/B Experiment
To run the main Mnemosyne system:
```bash
uv run main.py
```
To verify the A/B Belief Toggle:
```bash
uv run run_ab_experiment.py
```
To verify the Belief Adaptation:
```bash
uv run run_stress_test.py
```
To run the Web Orchestrator Interface:
```bash
uv run streamlit run app.py
```
### Content Execution Sandbox
- **Isolated Execution Layer**: A dedicated module (`sandbox/`) handles creative asset generation without contaminating the core reasoning logic.
- **Contract-Based Handoff**: Mnemosyne emits a `ContentBrief` (Visual/Narrative Intent + Assumptions referenced) which the sandbox translates into assets.
- **Gemini Integration**: Functional image generation via Gemini API with autonomous model selection (Auto-Model discovery).
- **Traceability**: All generated assets are programmatically linked back to the specific `Assumption ID` that governed their creation.

### A/B Belief Toggle Experiment
- **Primitive**: `BeliefToggleExperiment` (Sandbox-only).
- **Function**: Proves causal link between beliefs and outputs.
- **Method**: Runs two identical `ContentBriefs` with opposing `Risk Notes` derived from conflicting assumptions.
- **Outcome**: Generates materially different imagery (e.g., "Chaos" vs "Zen") while holding all other variables constant.

### Belief Stress Test (Adaptation)
- **Function**: Demonstrates institutional learning under pressure.
- **Process**:
    1. Seeds competing beliefs.
    2. Injects semantic feedback challenging one belief.
    3. **Semantic Engine** detects contradictions.
    4. **Memory Manager** updates confidence (respecting safety rails).
- **Result**: The system automatically downgrades the failing belief and pivots future execution strategy.

### Web Orchestration Interface
- **Type**: Streamlit Web Application (`app.py`).
- **Function**: End-to-end product test harness.
- **Workflow**:
    1. User inputs a topic/prompt.
    2. **Semantic Engine** identifies the relevant Assumption.
    3. System generates a `ContentBrief` with belief-derived Risk Notes.
    4. **Sandbox** executes the brief via Gemini Image Generation (Auto-Model).
    5. UI displays 4+ variations with traceability metadata.

---

## 2. Updated System Capabilities
Mnemosyne is now a fully capable **Epistemic Pipeline**:
1. **Governed Decisioning**: It can offer a recommendation, receive an executive override, execute the mandate, and log the disagreement for future audit.
2. **Belief-Governed Content**: It can translate abstract institutional beliefs (e.g., "Our audience values technical precision") into specific visual mandates and real generated images.
3. **Traceable Creative**: Every asset in the sandbox is now "explainable" by the underlying Mnemosyne belief system.

---

## 3. Active Constraints
- **Architectural Isolation**: Logic (src) vs. Execution (sandbox) separation is strictly enforced.
- **Dependency Guard**: Mnemosyne Core remains zero-dependency (No Gemini/Model logic in core).
- **Frozen History**: Overrides sit alongside history—they never overwrite or delete the AI's original reasoning.
