import uuid
import json
import os
import re

from openai import OpenAI

from .session_memory import SessionMemory
from .vector_store import VectorStore
from .long_term_store import LongTermMemory


SIM_THRESHOLD = 0.80
DUP_THRESHOLD = 0.93


def clean_llm_json(text: str):
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

    return text.strip()


def safe_json_list(text: str):
    text = clean_llm_json(text)

    match = re.search(r"\[.*\]", text, re.S)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            return []

    return []


def safe_json_obj(text: str):
    text = clean_llm_json(text)

    match = re.search(r"\{.*\}", text, re.S)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            return {}

    return {}


class MemoryManager:

    def __init__(self):

        self.session = SessionMemory()
        self.vector = VectorStore()
        self.long_term = LongTermMemory()

        self.llm = OpenAI(
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1"
        )

    def _generate_id(self):
        return int(uuid.uuid4().int % (2**63 - 1))


    def summarize(self, text: str):

        prompt = f"""
You are extracting LONG-TERM SEMANTIC MEMORY about the USER.

Store ONLY facts that:
- describe user preferences
- describe the user's identity
- describe goals, projects, skills, or constraints
- will remain useful weeks later

DO NOT STORE:
- greetings
- temporary conversation flow
- assistant explanations
- small talk

Return JSON LIST only.

Format:
[
  {{"fact": "...", "category": "...", "importance": 0.0}}
]

Conversation:
{text}
"""

        try:
            response = self.llm.responses.create(
                model="openai/gpt-oss-20b",
                input=prompt
            )

            return safe_json_list(response.output_text)

        except Exception:
            return []


    def store_interaction(self, user_msg, agent_msg):

        self.session.add_message("User", user_msg)
        self.session.add_message("Agent", agent_msg)

        conversation = f"""
USER MESSAGE:
{user_msg}

AGENT RESPONSE:
{agent_msg}
"""

        facts = self.summarize(conversation) ## Sumarizer -> fact object returns (fact , category and importance ..)  

        facts = [f for f in facts if f.get("importance", 0) >= 0.5]

        for fact in facts:
            self.reconcile_and_store(fact)


    def retrieve_context(self, query):

        session_context = self.session.get_recent()

        results = self.vector.search(query, k=3) ## [(8127381, 0.94), (9123123, 0.83), (9812312, 0.72)]

        memory_ids = [mem_id for mem_id, _ in results]

        facts = self.long_term.get_by_ids(memory_ids)

        return f"""
SESSION MEMORY:
{session_context}

RELEVANT FACTS:
{facts}
"""


    def reconcile_memory(self, old_fact: str, new_fact: str):

        prompt = f"""
You are managing an AI memory system.

Compare these two facts.

OLD FACT:
{old_fact}

NEW FACT:
{new_fact}

Choose exactly one label:

[DUPLICATE]
[CONTRADICTS]
[UPDATES]
[MERGEABLE]
[UNRELATED]

Return STRICT JSON:

{{
 "relation": "DUPLICATE | CONTRADICTS | UPDATES | MERGEABLE | UNRELATED",
 "final_fact": "string or null"
}}

Rules:
DUPLICATE -> final_fact = null
CONTRADICTS -> final_fact = NEW
UPDATES -> final_fact = NEW
MERGEABLE -> return merged concise fact
UNRELATED -> final_fact = null
"""

        try:
            response = self.llm.responses.create(
                model="openai/gpt-oss-20b",
                input=prompt
            )

            return safe_json_obj(response.output_text)

        except Exception:
            return {}


    def reconcile_and_store(self, fact_obj):

        new_fact = fact_obj["fact"]

        candidates = self.vector.search(new_fact, k=3)

        if not candidates:
            self._store_new_fact(fact_obj)
            return

        for mem_id, score in candidates:

            if score < SIM_THRESHOLD: ## Ignore unrelated facts 
                continue

            if score > DUP_THRESHOLD: ## Duplicate removal 
                return
            ## We are only storing facts which are not related but not identical ...
            old_fact_list = self.long_term.get_by_ids([mem_id])

            if not old_fact_list:
                continue

            old_fact = old_fact_list[0]

            decision = self.reconcile_memory(old_fact, new_fact)

            relation = decision.get("relation")
            final_fact = decision.get("final_fact")

            if relation == "DUPLICATE":
                return

            if relation in {"CONTRADICTS", "UPDATES", "MERGEABLE"}:

                self.vector.delete(mem_id)
                self.long_term.delete(mem_id)

                if final_fact:
                    updated_fact = dict(fact_obj)
                    updated_fact["fact"] = final_fact
                    self._store_new_fact(updated_fact)

                return

        self._store_new_fact(fact_obj)


    def _store_new_fact(self, fact_obj):

        if fact_obj.get("importance", 0) < 0.5:
            return

        memory_id = self._generate_id()

        fact_text = fact_obj["fact"]

        self.vector.add_text(memory_id, fact_text)

        self.long_term.store(
            memory_id,
            fact_text,
            fact_obj.get("category", "general"),
            fact_obj.get("importance", 0.5),    
        )