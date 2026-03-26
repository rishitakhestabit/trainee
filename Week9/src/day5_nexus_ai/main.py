import asyncio
import json
import os
import shutil
import re
import sys
import glob
from autogen_agentchat.messages import TextMessage

from agents.planner import planner, ExecutionPlan
from agents.orchestrator import run_autonomous_loop, memory_manager
from config import OUTPUT_DIR, LOG_DIR, LOG_FILE_PATH
from tools import create_log_entry


def initialize_workspace(clear_output=False):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    if clear_output:
        clear_output_dir()


def clear_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        return

    for f in os.listdir(OUTPUT_DIR):
        p = os.path.join(OUTPUT_DIR, f)

        try:
            if os.path.isfile(p):
                os.unlink(p)
            else:
                shutil.rmtree(p)
        except Exception as e:
            print(f"Warning: Could not delete {p}: {e}")


async def generate_execution_plan(query):

    memory_context = memory_manager.retrieve_context(query)

    enhanced_query = f"""
USER REQUEST:
{query}

MEMORY CONTEXT:
{memory_context[:1000]}
"""

    result = await planner.run(
        task=TextMessage(content=enhanced_query, source="user")
    )

    raw = result.messages[-1].content

    try:
        plan_data = json.loads(raw)

    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)

        if match:
            plan_data = json.loads(match.group())
        else:
            raise ValueError(f"Planner returned non-JSON response:\n{raw}")

    execution_plan = ExecutionPlan(**plan_data)

    create_log_entry(
        str(LOG_FILE_PATH),
        "planner",
        "plan_generated",
        {"steps": plan_data},
    )

    return execution_plan


def print_results(results):
    import glob
    import os
    from config import OUTPUT_DIR

    # First check if any markdown files already exist
    md_files = glob.glob(f"{OUTPUT_DIR}/*.md")

    if md_files:
        for md_file in md_files:
            print(f"\n {md_file}")
            print("=" * 60)
            with open(md_file, "r", encoding="utf-8") as f:
                print(f.read())
            print("=" * 60 + "\n")
        return

    # Otherwise print agent outputs and save files if needed
    for agent_name, agent_result in results.items():

        if isinstance(agent_result, dict):
            status = "✔" if agent_result.get("success") else "✘"
            output = str(agent_result.get("output", ""))
        else:
            status = "✔"
            output = str(agent_result)

        print(f"\n  {status} {agent_name}:\n{output}")

        #  SAVE CODE FILE
        if agent_name == "Coder" and output.strip():
            file_path = os.path.join(OUTPUT_DIR, "generated_code.py")
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(output)
                print(f"\n Code saved to: {file_path}")
            except Exception as e:
                print(f" Failed to save code: {e}")

        #  SAVE REPORT FILE
        if agent_name == "Reporter" and output.strip():
            file_path = os.path.join(OUTPUT_DIR, "final_report.md")
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(output)
                print(f"\n Report saved to: {file_path}")
            except Exception as e:
                print(f" Failed to save report: {e}")


async def run_nexus(query, clear_output=False):

    print("\n" + "=" * 60)
    print("NEXUS AI — AUTONOMOUS MULTI-AGENT SYSTEM")
    print("=" * 60)
    print(f"USER QUERY: {query}")
    print("=" * 60 + "\n")

    initialize_workspace(clear_output)

    execution_plan = await generate_execution_plan(query)

    print(f"[PLAN] {len(execution_plan.steps)} steps generated.\n")

    for step in execution_plan.steps:
        print(f"{step.agent} -> depends on {step.depends_on}")

    results = await run_autonomous_loop(execution_plan, query)

    return {
        "success": True,
        "query": query,
        "results": results,
    }


async def main():

    args = sys.argv[1:]
    clear = False

    if "--clear" in args:
        clear = True
        args = [a for a in args if a != "--clear"]

    if args:
        query = " ".join(args).strip()
        result = await run_nexus(query, clear)

        print("\n" + "=" * 60)
        print("EXECUTION COMPLETE")
        print("=" * 60 + "\n")

        print_results(result.get("results", {}))
        return

    if not sys.stdin.isatty():
        print("No interactive input available. Pass a query as arguments.")
        return

    print("\nNEXUS AI Interactive Shell")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:

        query = input("Enter your task: ").strip()

        if not query:
            print("Please enter a query.\n")
            continue

        if query.lower() in ["exit", "quit"]:
            print("Shutting down Nexus AI.")
            break

        clear = input("Clear previous output? (y/n): ").strip().lower() == "y"

        try:

            result = await run_nexus(query, clear)

            print("\n" + "=" * 60)
            print("EXECUTION COMPLETE")
            print("=" * 60 + "\n")

            results = result.get("results", {})
            print_results(results)

            create_log_entry(
                str(LOG_FILE_PATH),
                "system",
                "run_complete",
                {
                    "query": query,
                    "agents_run": list(results.keys()),
                },
            )

        except Exception as e:

            print(f"\n[FATAL ERROR] {e}")

            create_log_entry(
                str(LOG_FILE_PATH),
                "system",
                "fatal_error",
                {"error": str(e)},
            )


if __name__ == "__main__":
    asyncio.run(main())