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
    """
    LLM-based confidence using Groq
    Returns only:
    - confidence
    - latency
    """
    def __init__(self, cfg: EvalConfig | None = None):
        self.cfg = cfg or EvalConfig()
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def _get_confidence(self, question: str, answer: str) -> float:
        prompt = f"""
        Question: {question}
        Answer: {answer}
        Give a confidence score between 0 and 1 ONLY.
        Do not explain. Just return a number.
        """
        headers = {
            "Authorization": f"Bearer {self.cfg.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.cfg.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0
        }
        try:
            res = requests.post(self.url, headers=headers, json=data)
            output = res.json()
            print(f"[RAGEvaluator] full API response: {output}")

            # check for API errors
            if "error" in output:
                print(f"[RAGEvaluator] API error: {output['error']}")
                return 0.5

            text = output["choices"][0]["message"]["content"].strip()
            print(f"[RAGEvaluator] raw text: '{text}'")

            # extract float even if model adds extra text
            match = re.search(r"(\d+\.?\d*)", text)
            if match:
                score = float(match.group(1))
                print(f"[RAGEvaluator] parsed score: {score}")
                return min(max(score, 0.0), 1.0)  # clamp between 0 and 1

            return 0.5

        except Exception as e:
            print(f"[RAGEvaluator ERROR] {e}")
            return 0.5

    def score(self, question: str, answer: str, context: str) -> Dict[str, Any]:
        start = time.time()
        try:
            confidence = self._get_confidence(question, answer)
            latency = round(time.time() - start, 3)
            return {
                "confidence": confidence,
                "latency": latency
            }
        except Exception as e:
            return {
                "confidence": 0.0,
                "latency": 0.0,
                "error": str(e)
            }