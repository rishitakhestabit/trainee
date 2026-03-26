# AGENT FUNDAMENTALS — DAY 1

## Overview

This document describes the implementation of a multi-agent system built as part of Week 9 (Agentic AI Systems). The system follows a message-based pipeline architecture where each agent performs a strictly defined role.

Pipeline:
User → Research Agent → Summarizer Agent → Answer Agent → Final Output

The goal of this implementation is to demonstrate role-based intelligence, message passing, and separation of reasoning stages.

---

![Query](../../ss/day1/querytest1.png)
![Result](../../ss/day1/finalans1.png)

## Concepts Implemented

Based on Week 9 requirements:

- Agent vs Chatbot vs Pipeline
- ReAct Pattern (Reason → Act)
- Role isolation
- Message-based communication
- Short-term memory using buffered context

---

## Project Structure

src/
 └── agents/
      ├── research_agent.py
      ├── summarizer_agent.py
      ├── answer_agent.py
      └── run_agents.py

logs/

---

## Research Agent

File: agents/research_agent.py

Role:
- Collect raw information
- Provide structured findings
- Include pseudocode or technical details

Restrictions:
- Does not summarize
- Does not generate final answers
- Does not write full working code

Behavior:
- Produces structured research output
- Ends with: RESEARCH COMPLETE. PASSING TO SUMMARIZER.

---

## Summarizer Agent

File: agents/summarizer_agent.py

Role:
- Convert research into concise summary
- Preserve key technical details

Restrictions:
- No new information
- No final answers
- No full code

Behavior:
- Outputs 1–2 paragraph summary
- Ends with: SUMMARY COMPLETE. PASSING TO ANSWER AGENT.


---

## Answer Agent

File: agents/answer_agent.py

Role:
- Generate final response for the user
- Use only summarized input

Restrictions:
- No hallucination
- No external information
- Must be complete and accurate

Behavior:
- Produces final polished answer


---

## Execution Pipeline

File: agents/run_agents.py

The pipeline executes agents sequentially:

1. Research Agent processes the user query
2. Output is passed to Summarizer Agent
3. Summary is passed to Answer Agent
4. Final answer is returned

Logging:
- Logs stored in logs/ directory
- Each run generates timestamped log file

---

## Key Observations

- Strict role separation prevents overlap
- Message passing ensures modular design
- Buffered memory allows short context retention
- Logging helps in debugging and tracing execution

---

## Conclusion

The system successfully demonstrates a basic multi-agent architecture using message passing and role isolation. Each agent performs a single responsibility, making the system modular, scalable, and easy to debug. This forms the foundation for more complex multi-agent orchestration in later stages.

![Query](../../ss/day1/querytest2.png)
![Result](../../ss/day1/finalans2.png)
