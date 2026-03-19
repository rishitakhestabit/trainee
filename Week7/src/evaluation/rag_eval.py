from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict
import time

from sentence_transformers import SentenceTransformer, util


@dataclass
class EvalConfig:
    model_name: str = "all-MiniLM-L6-v2"


class RAGEvaluator:
    """
    Production-style evaluator:
    - Context match
    - Faithfulness
    - Answer relevancy
    - Hallucination
    - Confidence
    - Quality flags
    """

    def __init__(self, cfg: EvalConfig | None = None):
        self.cfg = cfg or EvalConfig()
        self.model = SentenceTransformer(self.cfg.model_name)

    def score(self, question: str, answer: str, context: str) -> Dict[str, Any]:
        start = time.time()

        try:
            question = question or ""
            answer = answer or ""
            context = context or ""

            # embeddings
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

            #  Improved confidence weighting
            confidence = float(
                0.4 * faithfulness +
                0.3 * context_match +
                0.3 * answer_relevancy
            )

            #  Quality flags (VERY useful in UI)
            if confidence > 0.75:
                quality = "HIGH"
            elif confidence > 0.4:
                quality = "MEDIUM"
            else:
                quality = "LOW"

            latency = round(time.time() - start, 3)

            return {
                "context_match": context_match,
                "faithfulness": faithfulness,
                "answer_relevancy": answer_relevancy,
                "hallucination": hallucination,
                "confidence": confidence,
                "quality": quality,
                "eval_latency": latency
            }

        except Exception as e:
            return {
                "context_match": 0.0,
                "faithfulness": 0.0,
                "answer_relevancy": 0.0,
                "hallucination": 1.0,
                "confidence": 0.0,
                "quality": "ERROR",
                "error": str(e)
            }