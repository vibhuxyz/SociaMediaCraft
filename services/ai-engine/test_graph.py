from workflow.graph import build_graph
import asyncio
import json
from uuid import uuid4


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


async def run():
    graph = build_graph(interrupt_after_clarification=True)

    print("╔════════════════════════════════════════════════════════════╗")
    print("║ VideoCraft AI Engine                                      ║")
    print("║ Enter your video prompt. The graph will ask follow-ups     ║")
    print("║ if it needs critical details before final planning.        ║")
    print("╚════════════════════════════════════════════════════════════╝")

    prompt = ask("\nYour prompt: ")
    if not prompt:
        print("Prompt is required.")
        return

    config = {"configurable": {"thread_id": f"cli_{uuid4()}"}}
    initial_state = {"prompt": prompt}

    print("\n--- STARTING WORKFLOW ---")
    paused_state = await graph.ainvoke(initial_state, config)
    if paused_state.get("is_valid") is False:
        print(f"\nCould not plan this prompt: {paused_state.get('validation_error')}")
        return

    questions = paused_state.get("clarification_questions", [])
    answers = {}

    if questions:
        print("\n--- NEED MORE DETAILS ---")
        for index, question in enumerate(questions, start=1):
            answer = ask(f"{index}. {question}\n> ")
            if answer:
                answers[question] = answer
    else:
        print("\n--- NO CLARIFICATION NEEDED ---")

    if answers:
        graph.update_state(config, {"clarification_answers": answers})

    print("\n--- RESUMING PLANNING ---")
    final_state = await graph.ainvoke(None, config)

    print("\n--- FINAL PRODUCTION PLAN ---")
    if "production_plan" not in final_state:
        print(json.dumps(final_state, indent=2, default=str))
        return
    print(json.dumps(final_state["production_plan"], indent=2))


asyncio.run(run())
