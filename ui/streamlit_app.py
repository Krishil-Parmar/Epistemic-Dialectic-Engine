import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import streamlit as st

from ede.pipeline import EDEPipeline

st.set_page_config(page_title="Epistemic Dialectic Engine", layout="wide")
st.title("Epistemic Dialectic Engine")
st.caption("Mindset Elevation Framework — v0.1 Demo")


@st.cache_resource
def get_event_loop() -> asyncio.AbstractEventLoop:
    # A single persistent event loop is required so the async HTTP connection
    # pools inside the cached LLM clients remain bound to a live loop across
    # Streamlit reruns. Using asyncio.run() per query closes the loop and
    # leaves stale connections that raise "Event loop is closed" on the next call.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


@st.cache_resource
def get_pipeline():
    # Ensure the persistent loop is the current loop when the pipeline (and its
    # async LLM clients) are first constructed, so any loop-bound state binds
    # to the loop we will keep reusing.
    asyncio.set_event_loop(get_event_loop())
    return EDEPipeline()


def run_async(coro):
    loop = get_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# Session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "session_id" not in st.session_state:
    import uuid
    st.session_state["session_id"] = str(uuid.uuid4())

# Display conversation history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "diagnostics" in msg:
            with st.expander("Diagnostics"):
                st.json(msg["diagnostics"])

# Chat input
query = st.chat_input("Enter a business dilemma or decision scenario...")

if query:
    st.session_state["messages"].append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing mindset and generating response..."):
            pipeline = get_pipeline()
            try:
                result = run_async(
                    pipeline.run(
                        query=query,
                        session_id=st.session_state["session_id"],
                    )
                )
            except Exception as e:
                st.error(
                    "Something went wrong while generating the response. "
                    "Please try again."
                )
                with st.expander("Error details"):
                    st.code(f"{type(e).__name__}: {e}")
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": "_The previous attempt failed. Please try again._",
                })
                st.stop()

        if result["type"] == "clarification":
            st.markdown(result["question"])
            diagnostics = {
                "classification": result["classification"],
            }
            st.session_state["messages"].append({
                "role": "assistant",
                "content": result["question"],
                "diagnostics": diagnostics,
            })
        else:
            st.markdown(result["response"])
            diagnostics = {
                "classification": {
                    "current_cell": f"({result['classification']['top_interaction']}, {result['classification']['top_scope']})",
                    "confidence": result["classification"]["confidence"],
                    "justification": result["classification"]["justification"],
                    "context_signals": result["classification"].get("context_signals", []),
                },
                "elevation": {
                    "target_cell": f"({result['decision']['target_interaction']}, {result['decision']['target_scope']})",
                    "decision_type": result["decision"]["decision_type"],
                    "rationale": result["decision"]["rationale"],
                    "pre_mortem_priority": result["decision"]["pre_mortem_priority"],
                },
                "pre_mortem": result["draft"]["pre_mortem_outputs"] if result.get("draft") else None,
                "critique": {
                    "passed": result["critique"]["passed"],
                    "cell_match_score": result["critique"]["target_cell_match_score"],
                    "completeness_score": result["critique"]["pre_mortem_completeness_score"],
                    "instruction_adherence": result["critique"]["instruction_adherence_score"],
                    "issues": result["critique"]["issues"],
                } if result.get("critique") else None,
            }
            with st.expander("Diagnostics"):
                st.json(diagnostics)
            st.session_state["messages"].append({
                "role": "assistant",
                "content": result["response"],
                "diagnostics": diagnostics,
            })

    st.rerun()
