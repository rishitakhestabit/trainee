
import asyncio
import json
import os
import re
import shutil
from collections import defaultdict, deque
from autogen_agentchat.messages import TextMessage

from config import MAX_PLAN_RETRIES, LOG_FILE_PATH, OUTPUT_DIR
from tools import create_log_entry
from memory.memory_manager import MemoryManager

from agents.planner import planner, ExecutionPlan
from agents.researcher import researcher
from agents.coder import coder
from agents.analyst import analyst
from agents.critic import critic
from agents.optimizer import optimizer
from agents.validator import validator
from agents.reporter import reporter


# ================== AGENT REGISTRY ==================
AGENT_REGISTRY = {
    "Researcher": researcher,
    "Coder": coder,
    "Analyst": analyst,
    "Critic": critic,
    "Optimizer": optimizer,
    "Validator": validator,
    "Reporter": reporter,
}

memory_manager = MemoryManager()


# ================== DAG COMPUTATION ==================
def compute_levels(execution_plan):
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    for step in execution_plan.steps:
        in_degree.setdefault(step.agent, 0)
        in_degree[step.agent] = len(step.depends_on)

        for dep in step.depends_on:
            graph[dep].append(step.agent)
            in_degree.setdefault(dep, 0)

    queue = deque([n for n in in_degree if in_degree[n] == 0])
    levels = []

    while queue:
        level = list(queue)
        levels.append(level)
        next_queue = deque()

        for node in level:
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_queue.append(neighbor)

        queue = next_queue

    return levels


# ================== CONTEXT ==================
def compress_context(context, limit=1000):
    formatted = []
    for agent, output in context.items():
        truncated = str(output)[:limit]
        formatted.append(f"{agent} OUTPUT:\n{truncated}\n")
    return "\n".join(formatted)


# ================== FILE SAVING ==================

def extract_filename_from_query(user_query: str):
    """Extract user-specified output filename — only md/txt/py/json, never csv."""
    match = re.search(r'\b([\w\-]+\.(?:md|txt|py|json))\b', user_query, re.IGNORECASE)
    return match.group(1) if match else None


def make_project_folder_name(user_query: str) -> str:
    """Generate a clean folder name from the user query."""
    words = re.sub(r'[^\w\s]', '', user_query.lower()).split()
    stop_words = {"a", "an", "the", "for", "in", "of", "to", "and", "or", "with", "build",
                  "create", "generate", "write", "make", "design", "implement", "full", "complete"}
    meaningful = [w for w in words if w not in stop_words and len(w) > 2]
    folder = "_".join(meaningful[:4])
    return folder if folder else "project"


def extract_files_from_coder_output(text: str) -> dict:
    """
    Extract multiple files from coder output.
    Looks for ### FILE: filename patterns followed by code blocks.
    Returns dict of {filename: content}
    """
    files = {}

    # Pattern: ### FILE: filename\n```lang\ncontent\n```
    pattern = r'###\s*FILE:\s*([\w\-./]+)\s*\n```[^\n]*\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)

    for filename, content in matches:
        filename = filename.strip()
        content = content.strip()
        if filename and content:
            files[filename] = content

    # Fallback: if no ### FILE: pattern found, extract all code blocks with language hints
    if not files:
        # try to find ```lang\ncontent``` blocks
        all_blocks = re.findall(r'```(\w+)?\n(.*?)```', text, re.DOTALL)
        for i, (lang, content) in enumerate(all_blocks):
            content = content.strip()
            if not content:
                continue
            # determine extension from language hint
            ext_map = {
                "python": ".py", "py": ".py",
                "javascript": ".js", "js": ".js",
                "typescript": ".ts", "ts": ".ts",
                "html": ".html", "css": ".css",
                "dockerfile": "Dockerfile", "docker": "Dockerfile",
                "yaml": ".yaml", "yml": ".yml",
                "json": ".json", "sql": ".sql",
                "bash": ".sh", "shell": ".sh",
                "go": ".go", "rust": ".rs",
                "java": ".java", "kotlin": ".kt",
            }
            if lang and lang.lower() in ext_map:
                ext = ext_map[lang.lower()]
                if ext == "Dockerfile":
                    fname = "Dockerfile"
                else:
                    fname = f"output{ext}" if i == 0 else f"file_{i}{ext}"
            else:
                fname = f"output_{i}.txt" if i > 0 else "output.txt"
            files[fname] = content

        # last fallback — raw text looks like code
        if not files and text.strip().startswith(("import ", "def ", "class ", "#!", "FROM ", "<!DOCTYPE")):
            files["output.txt"] = text.strip()

    return files


def save_outputs(global_context: dict, user_query: str):
    """
    Python backend saves all output files.
    - For coding tasks: creates a project folder with all extracted files + report.md
    - For non-coding tasks: saves report.md directly in Output/
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    user_filename = extract_filename_from_query(user_query)
    is_coding_task = (
        "Coder" in global_context
        and global_context["Coder"] != "Skipped coder"
        and len(str(global_context.get("Coder", "")).strip()) > 10
    )

    # ── CODING TASK: create project folder with multiple files ────────────────
    if is_coding_task:
        folder_name = make_project_folder_name(user_query)
        project_dir = os.path.join(OUTPUT_DIR, folder_name)
        os.makedirs(project_dir, exist_ok=True)

        coder_output = str(global_context["Coder"])
        files = extract_files_from_coder_output(coder_output)

        if files:
            for filename, content in files.items():
                # handle nested paths like src/models.py
                file_path = os.path.join(project_dir, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f" Saved → {file_path}")
        else:
            # fallback — save raw coder output as text
            with open(os.path.join(project_dir, "output.txt"), "w", encoding="utf-8") as f:
                f.write(coder_output)
            print(f" Saved → {project_dir}/output.txt")

        # save report inside project folder
        if "Reporter" in global_context:
            report_path = os.path.join(project_dir, "report.md")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(str(global_context["Reporter"]))
            print(f" Saved → {report_path}")

        print(f" Project saved in → {project_dir}/")

    # ── NON-CODING TASK: save report.md in Output/ ───────────────────────────
    else:
        if "Reporter" in global_context:
            reporter_output = str(global_context["Reporter"])

            if user_filename and not user_filename.endswith(".csv"):
                report_path = os.path.join(OUTPUT_DIR, user_filename)
            else:
                report_path = os.path.join(OUTPUT_DIR, "report.md")

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(reporter_output)
            print(f" Saved report → {report_path}")

        # save analyst output if no reporter
        elif "Analyst" in global_context:
            analysis_path = os.path.join(OUTPUT_DIR, "analysis.md")
            with open(analysis_path, "w", encoding="utf-8") as f:
                f.write(str(global_context["Analyst"]))
            print(f" Saved analysis → {analysis_path}")


# ================== AGENT EXECUTION ==================
async def run_agent(agent_name, instruction, global_context, user_query):

    agent = AGENT_REGISTRY.get(agent_name) or AGENT_REGISTRY.get(agent_name.capitalize())

    # Skip coder for pure planning tasks
    if agent_name == "Coder" and any(
        word in user_query.lower()
        for word in ["plan a", "plan an", "startup plan", "business plan", "business strategy"]
    ):
        print(" Skipping Coder for planning task")
        return {"agent": agent_name, "success": True, "output": "Skipped coder"}

    context_text = compress_context(global_context)

    prompt = f"""
SYSTEM GOAL:
{user_query}

AGENT ROLE:
You are the {agent_name} agent.

YOUR TASK:
{instruction}

CONTEXT:
{context_text}
"""

    try:
        print(f"\nRunning {agent_name} Agent")

        result = await agent.run(
            task=TextMessage(content=prompt, source="orchestrator")
        )

        output = result.messages[-1].content or ""

        if agent_name == "Coder" and len(output.strip()) < 10:
            raise Exception("EMPTY_CODE_OUTPUT")

        memory_manager.store_interaction(agent_name, output)

        create_log_entry(
            str(LOG_FILE_PATH),
            agent_name.lower(),
            "success",
            {"output": output},
        )

        return {"agent": agent_name, "success": True, "output": output}

    except Exception as e:
        error = str(e)

        if "429" in error or "rate limit" in error.lower():
            print(f" Rate limit reached for {agent_name}")

        create_log_entry(
            str(LOG_FILE_PATH),
            agent_name.lower(),
            "failed",
            {"error": error},
        )

        return {"agent": agent_name, "success": False, "error": error}


# ================== LEVEL EXECUTION ==================
async def run_level(level_agents, step_map, context, user_query):
    tasks = [
        run_agent(agent, step_map[agent], context, user_query)
        for agent in level_agents
    ]
    return await asyncio.gather(*tasks)


# ================== EXECUTION ==================
async def execute_plan(execution_plan, user_query):

    levels = compute_levels(execution_plan)

    if not levels or all(len(level) == 0 for level in levels):
        print(" Invalid execution levels — forcing execution")
        levels = [[step.agent for step in execution_plan.steps]]

    step_map = {step.agent: step.instruction for step in execution_plan.steps}
    global_context = {}

    for level_agents in levels:

        results = await run_level(level_agents, step_map, global_context, user_query)

        for res in results:

            if not res["success"]:
                raise Exception(f"EXEC_FAIL::{res['agent']}::{res['error']}")

            global_context[res["agent"]] = res["output"]

            if res["agent"] == "Validator":
                if "FAIL" in res["output"].upper() or "REJECTED" in res["output"].upper():
                    print("⚠️ Validation failed — continuing to Reporter")
                    global_context["validator_feedback"] = res["output"]
                    continue

    # ── Python backend saves all files ───────────────────────────────────────
    save_outputs(global_context, user_query)

    return global_context


# ================== MAIN LOOP ==================
async def run_autonomous_loop(initial_plan, user_query):

    current_plan = initial_plan
    validator_feedback = None

    for attempt in range(MAX_PLAN_RETRIES):

        print(f"\nATTEMPT {attempt + 1}/{MAX_PLAN_RETRIES}")

        try:
            return await execute_plan(current_plan, user_query)

        except Exception as e:

            err = str(e)

            if err.startswith("VALIDATION_FAIL::"):

                validator_feedback = err.replace("VALIDATION_FAIL::", "")
                memory_manager.store_interaction("validator_feedback", validator_feedback)
                clear_output_dir()

                replan_prompt = f"""
SYSTEM GOAL:
{user_query}

VALIDATOR FEEDBACK:
{validator_feedback}

Generate a NEW improved execution plan.
Return JSON only.
"""

                result = await planner.run(
                    task=TextMessage(content=replan_prompt, source="orchestrator")
                )

                raw = result.messages[-1].content

                try:
                    plan_data = json.loads(raw)
                except:
                    match = re.search(r"\{.*\}", raw, re.DOTALL)
                    if not match:
                        raise
                    plan_data = json.loads(match.group())

                create_log_entry(
                    str(LOG_FILE_PATH),
                    "planner",
                    "updated_plan_generated",
                    {"steps": plan_data},
                )

                current_plan = ExecutionPlan(**plan_data)
                continue

            return {"system_error": err}

    return {
        "warning": "Maximum retries reached",
        "validator_feedback": validator_feedback,
    }


# ================== CLEANUP ==================
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
        except:
            pass