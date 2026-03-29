from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict
import time
import re
import requests
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class EvalConfig:
    model_name: str = field(default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY"))


class RAGEvaluator:

    def __init__(self, cfg: EvalConfig | None = None):
        self.cfg = cfg or EvalConfig()
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def _call_llm(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.cfg.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.cfg.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }

        try:
            res = requests.post(self.url, headers=headers, json=data)
            output = res.json()

            if "error" in output:
                return "0.5"

            return output["choices"][0]["message"]["content"].strip()

        except Exception:
            return "0.5"

    def _extract_score(self, text: str) -> float:
        match = re.search(r"(\d+\.?\d*)", text)
        if match:
            val = float(match.group(1))
            return min(max(val, 0.0), 1.0)
        return 0.5

    def score(self, question: str, answer: str, context: str) -> Dict[str, Any]:
        start = time.time()

        # CONFIDENCE
        confidence = self._extract_score(self._call_llm(f"""
        Question: {question}
        Answer: {answer}
        Score between 0 and 1 ONLY.
        """))

        # FAITHFULNESS
        faithfulness = self._extract_score(self._call_llm(f"""
        Context: {context}
        Answer: {answer}
        Does answer follow context? Score 0–1 ONLY.
        """))

        # CONTEXT RELEVANCE
        context_relevance = self._extract_score(self._call_llm(f"""
        Question: {question}
        Context: {context}
        Relevance score 0–1 ONLY.
        """))

        hallucination = 1 if faithfulness < 0.4 else 0

        latency = round(time.time() - start, 3)

        return {
            "confidence": confidence,
            "faithfulness": faithfulness,
            "context_relevance": context_relevance,
            "hallucination": hallucination,
            "latency": latency
        }