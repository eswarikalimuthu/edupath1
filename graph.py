"""
Module 2/3 - LangGraph orchestration.

Wires Profile -> Retrieval -> Scholarship Evaluation -> Recommendation -> Practice Plan -> Pathway Planner
into an end-to-end resilient graph pipeline.
"""
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, END

from src.agents import (
    profile_agent,
    retrieval_agent,
    scholarship_agent,
    practice_agent,
    recommendation_agent,
    pathway_agent,
)


class AdvisorState(TypedDict):
    student_text: str
    profile: dict
    retrieved: dict
    scholarships: list
    practice_plan: dict
    recommendation: str
    pathway: str


def profile_node(state: AdvisorState) -> AdvisorState:
    print("[Graph] Running Profile Agent...")
    profile = profile_agent.build_profile(state["student_text"])
    return {**state, "profile": profile}


def retrieval_node(state: AdvisorState) -> AdvisorState:
    print("[Graph] Running Retrieval Agent...")
    retrieved = retrieval_agent.retrieve_for_profile(state["profile"])
    return {**state, "retrieved": retrieved}


def scholarship_node(state: AdvisorState) -> AdvisorState:
    print("[Graph] Running Scholarship Evaluator Agent...")
    raw_scholarships = state.get("retrieved", {}).get("scholarship", [])
    evaluated = scholarship_agent.evaluate_scholarships(raw_scholarships, state["profile"])
    return {**state, "scholarships": evaluated}


def recommendation_node(state: AdvisorState) -> AdvisorState:
    print("[Graph] Running Recommendation Agent...")
    recommendation = recommendation_agent.generate_recommendation(state["profile"], state["retrieved"])
    return {**state, "recommendation": recommendation}


def practice_node(state: AdvisorState) -> AdvisorState:
    print("[Graph] Running Practice & Skills Agent...")
    practice_plan = practice_agent.generate_30_day_plan(state["profile"])
    return {**state, "practice_plan": practice_plan}


def pathway_node(state: AdvisorState) -> AdvisorState:
    print("[Graph] Running Pathway Planner Agent...")
    pathway = pathway_agent.generate_pathway(state["profile"], state["recommendation"])
    return {**state, "pathway": pathway}


def build_graph():
    graph = StateGraph(AdvisorState)

    graph.add_node("profile", profile_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("scholarship", scholarship_node)
    graph.add_node("recommendation", recommendation_node)
    graph.add_node("practice", practice_node)
    graph.add_node("pathway", pathway_node)

    graph.set_entry_point("profile")
    graph.add_edge("profile", "retrieval")
    graph.add_edge("retrieval", "scholarship")
    graph.add_edge("scholarship", "recommendation")
    graph.add_edge("recommendation", "practice")
    graph.add_edge("practice", "pathway")
    graph.add_edge("pathway", END)

    return graph.compile()


def run_advisor(student_text: str) -> AdvisorState:
    """Convenience function to run the whole pipeline in one call."""
    app = build_graph()
    initial_state = {
        "student_text": student_text,
        "profile": {},
        "retrieved": {},
        "scholarships": [],
        "practice_plan": {},
        "recommendation": "",
        "pathway": "",
    }
    result = app.invoke(initial_state)
    return result


if __name__ == "__main__":
    sample_input = (
        "I am a 12th standard student from Tamil Nadu, scored 88% in board exams, "
        "belong to SC category with family income 2 lakh per annum. Interested in computer science and robotics."
    )
    final_state = run_advisor(sample_input)

    print("\n" + "=" * 60)
    print("STRUCTURED PROFILE:")
    print(final_state["profile"])
    print("\n" + "=" * 60)
    print(f"EVALUATED SCHOLARSHIPS ({len(final_state['scholarships'])}):")
    for s in final_state["scholarships"][:3]:
        cat_m = str(s['category_match']).replace('\u2713', '[Y]')
        print(f"- {s['name']} | Status: {s['eligibility_status']} | Category: {cat_m}")
    print("\n" + "=" * 60)
    print("30-DAY PRACTICE PLAN:")
    print(final_state["practice_plan"]["title"])
    for w in final_state["practice_plan"]["weeks"]:
        print(f"  {w['days']}: {w['theme']} - {w['goal']}")
