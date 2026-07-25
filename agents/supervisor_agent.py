"""supervisor_agent -- owns the pipeline sequence and the shared GraphState.

This is the only file that knows the overall order. Every other agent only
knows its own single job and reads/writes its own slice of state; wiring
them together into "script -> hook -> visual_prompt -> asset -> motion ->
transition -> qc -> render" lives here, not scattered across the agents.

qc_agent is a real gate, not just another step: if it marks the state
invalid, the pipeline stops there instead of handing broken beats to
render_agent.
"""

from langgraph.graph import END, StateGraph

from asset_agent import asset_agent
from hook_agent import hook_agent
from motion_agent import motion_agent
from qc_agent import qc_agent
from render_agent import render_agent
from script_agent import script_agent
from state import GraphState
from transition_agent import transition_agent
from visual_prompt_agent import visual_prompt_agent


def _after_qc(state: GraphState) -> str:
    return "render_agent" if state["qc_report"]["valid"] else END


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("script_agent", script_agent)
    graph.add_node("hook_agent", hook_agent)
    graph.add_node("visual_prompt_agent", visual_prompt_agent)
    graph.add_node("asset_agent", asset_agent)
    graph.add_node("motion_agent", motion_agent)
    graph.add_node("transition_agent", transition_agent)
    graph.add_node("qc_agent", qc_agent)
    graph.add_node("render_agent", render_agent)

    graph.set_entry_point("script_agent")
    graph.add_edge("script_agent", "hook_agent")
    graph.add_edge("hook_agent", "visual_prompt_agent")
    graph.add_edge("visual_prompt_agent", "asset_agent")
    graph.add_edge("asset_agent", "motion_agent")
    graph.add_edge("motion_agent", "transition_agent")
    graph.add_edge("transition_agent", "qc_agent")
    graph.add_conditional_edges(
        "qc_agent", _after_qc, {"render_agent": "render_agent", END: END}
    )
    graph.add_edge("render_agent", END)

    return graph.compile()


def run_pipeline(topic: str) -> GraphState:
    graph = build_graph()
    return graph.invoke({"topic": topic, "beats": []})
