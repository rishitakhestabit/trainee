from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from sentence_transformers import SentenceTransformer, util


@dataclass
class EvalConfig:
    model_name: str = "all-MiniLM-L6-v2"


class RAGEvaluator:
    """
    Launchpad Day-5:
    - Context match
    - Faithfulness
    - Answer relevancy
    - Hallucination (1-faithfulness)
    - Confidence (weighted)
    """

    def __init__(self, cfg: EvalConfig | None = None):
        self.cfg = cfg or EvalConfig()
        self.model = SentenceTransformer(self.cfg.model_name)

    def score(self, question: str, answer: str, context: str) -> Dict[str, Any]:
        question = question or ""
        answer = answer or ""
        context = context or ""

        q_emb = self.model.encode(question, convert_to_tensor=True)
        a_emb = self.model.encode(answer, convert_to_tensor=True)

        if context.strip():
            c_emb = self.model.encode(context, convert_to_tensor=True)

            context_match = float(util.cos_sim(q_emb, c_emb).max().item())
            faithfulness = float(util.cos_sim(a_emb, c_emb).max().item())
        else:
            context_match = 0.0
            faithfulness = 0.0

        answer_relevancy = float(util.cos_sim(q_emb, a_emb).item())
        hallucination = float(1.0 - faithfulness)

        confidence = float(context_match * 0.25 + faithfulness * 0.25 + answer_relevancy * 0.5)

        return {
            "context_match": context_match,
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy,
            "hallucination": hallucination,
            "confidence": confidence,
        }