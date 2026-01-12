import streamlit as st
import sys
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

# Ensure 'src' is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from mnemosyne.core.schemas import ContentBrief, Assumption
from mnemosyne.core.semantic import SemanticEngine
from sandbox.executor import ContentExecutor
from sandbox.gemini_client import GeminiImageClient

# Page Config
st.set_page_config(page_title="Mnemosyne Orchestrator", layout="wide")

# --- INITIALIZATION & STATE ---
def init_state():
    if 'engine' not in st.session_state:
        st.session_state.engine = SemanticEngine()
        
    if 'assumptions' not in st.session_state:
        # Seed Standard Assumptions for the Demo
        st.session_state.assumptions = [
            Assumption(
                id="asm_innovation",
                statement="We believe in radical innovation and futuristic technology.",
                supporting_insights=[],
                embedding=st.session_state.engine.encode("We believe in radical innovation and futuristic technology.")
            ),
            Assumption(
                id="asm_tradition",
                statement="We believe in timeless tradition and heritage craftsmanship.",
                supporting_insights=[],
                embedding=st.session_state.engine.encode("We believe in timeless tradition and heritage craftsmanship.")
            ),
            Assumption(
                id="asm_community",
                statement="We believe that human connection drives value.",
                supporting_insights=[],
                embedding=st.session_state.engine.encode("We believe that human connection drives value.")
            )
        ]
        
    if 'brief' not in st.session_state:
        st.session_state.brief = None
    if 'assets' not in st.session_state:
        st.session_state.assets = []
    if 'executor' not in st.session_state:
        st.session_state.executor = ContentExecutor()

init_state()

# --- HEADER ---
st.title("Mnemosyne: Epistemic Orchestrator")
st.markdown("---")

# --- VIEW 1: INPUT ---
st.subheader("1. Input Context")
user_input = st.text_input("What is the content idea?", placeholder="e.g. Launching a new secure cloud platform")

if st.button("Generate Execution Plan"):
    if not user_input:
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Mnemosyne is reasoning..."):
            # 1. Semantic Selection
            emb_input = st.session_state.engine.encode(user_input)
            
            best_match = None
            best_score = -1.0
            
            for asm in st.session_state.assumptions:
                score = st.session_state.engine.similarity(emb_input, asm.embedding)
                if score > best_score:
                    best_score = score
                    best_match = asm
            
            # 2. Emulate Risk Logic
            risk_note = "Standard compliance."
            visual_intent = "Standard corporate."
            
            if best_match.id == "asm_innovation":
                risk_note = "Do not look legacy. Must appear bleeding edge. Neon, dark mode, cyber aesthetic."
                visual_intent = "Futuristic, Neon, Cyberpunk, High Tech."
            elif best_match.id == "asm_tradition":
                risk_note = "Avoid flashiness. Must look established and premium. Stone, wood, classical."
                visual_intent = "Classic, Heritage, Warm tones, Analog texture."
            elif best_match.id == "asm_community":
                risk_note = "No cold tech. Must show faces and warmth. People over pixels."
                visual_intent = "Candid photography, Warm lighting, Diverse group, Office laughter."

            # 3. Create Brief
            st.session_state.brief = ContentBrief(
                id=str(uuid.uuid4()),
                target_id="web_demo_post",
                narrative_intent=user_input,
                visual_intent=visual_intent,
                assumptions_referenced=[best_match.id],
                risk_notes=risk_note,
                experiment_tag="web_orchestrator"
            )
            
            # Run Execution Immediately
            st.session_state.assets = st.session_state.executor.generate_assets(st.session_state.brief)
            
            st.success("Execution Complete.")


# --- VIEW 2: REASONING & RESULTS ---
if st.session_state.brief:
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("2. Epistemic Governance")
        st.info(f"**Governing Belief**: `{st.session_state.brief.assumptions_referenced[0]}`")
        st.markdown(f"**Narrative**: {st.session_state.brief.narrative_intent}")
        st.markdown(f"**Visual Mandate**: {st.session_state.brief.visual_intent}")
        st.error(f"**Risk Constraints**: {st.session_state.brief.risk_notes}")
        st.caption("Strategy: The system selected the assumption with highest semantic resonance to the topic.")
        
    with col2:
        st.subheader("3. Sandbox Execution (Gemini)")
        if st.session_state.assets:
            # Display Images in a Grid
            img_cols = st.columns(2)
            for i, asset in enumerate(st.session_state.assets):
                with img_cols[i % 2]:
                    # Check if mock or real
                    if "[MOCK" in asset.path or "[ERROR]" in asset.path:
                        st.warning(f"Output: {asset.path}")
                    else:
                        st.image(asset.path, caption=f"Prompt Variation: {i+1}")
                        st.caption(f"Trace: {asset.metadata['assumptions']}")
        else:
            st.warning("No assets generated yet.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("System Status")
    st.write("Core: **Active (Frozen)**")
    st.write("Sandbox: **Online**")
    
    api_key_status = "DETECTED" if os.environ.get("GEMINI_API_KEY") else "MISSING (MOCK MODE)"
    st.write(f"Gemini API: **{api_key_status}**")
