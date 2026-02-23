# src/embeddings/clip_embedder.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Any
import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


@dataclass
class ClipConfig:
    model_name: str = "openai/clip-vit-base-patch32"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class CLIPEmbedder:
    """
    Robust CLIP embedder that works across transformers versions.

    Produces:
      - text embedding (projected) 512-d
      - image embedding (projected) 512-d

    Always returns L2-normalized float32 vectors (cosine via FAISS IP).
    """

    def __init__(self, config: ClipConfig = ClipConfig()):
        self.config = config
        self.processor = CLIPProcessor.from_pretrained(config.model_name)
        self.model = CLIPModel.from_pretrained(config.model_name).to(config.device)
        self.model.eval()

    @staticmethod
    def _l2_normalize_np(x: np.ndarray) -> np.ndarray:
        denom = np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
        return x / denom

    @staticmethod
    def _to_tensor(output: Any) -> torch.Tensor:
        """
        Convert different HF outputs into a Tensor.
        """
        if isinstance(output, torch.Tensor):
            return output
        if hasattr(output, "pooler_output") and output.pooler_output is not None:
            return output.pooler_output
        if hasattr(output, "last_hidden_state") and output.last_hidden_state is not None:
            # CLS token
            return output.last_hidden_state[:, 0, :]
        # Some outputs are tuples; take first element
        if isinstance(output, (tuple, list)) and len(output) > 0:
            if isinstance(output[0], torch.Tensor):
                return output[0]
        raise TypeError(f"Cannot convert output type {type(output)} to Tensor.")

    @property
    def dim(self) -> int:
        return 512

    @torch.no_grad()
    def embed_text(self, text: str) -> np.ndarray:
        inputs = self.processor(text=[text], return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.config.device) for k, v in inputs.items()}

        # Use text_model output then projection (most robust)
        text_out = self.model.text_model(**inputs)                 # BaseModelOutputWithPooling
        pooled = self._to_tensor(text_out)                         # (1, hidden)
        proj = self.model.text_projection(pooled)                  # (1, 512)

        vec = proj.detach().cpu().numpy().astype("float32")
        vec = self._l2_normalize_np(vec)[0]
        return vec

    @torch.no_grad()
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        inputs = self.processor(text=texts, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.config.device) for k, v in inputs.items()}

        text_out = self.model.text_model(**inputs)
        pooled = self._to_tensor(text_out)                         # (n, hidden)
        proj = self.model.text_projection(pooled)                  # (n, 512)

        vecs = proj.detach().cpu().numpy().astype("float32")
        return self._l2_normalize_np(vecs)

    @torch.no_grad()
    def embed_image(self, image: Image.Image) -> np.ndarray:
        if image.mode != "RGB":
            image = image.convert("RGB")

        inputs = self.processor(images=[image], return_tensors="pt")
        inputs = {k: v.to(self.config.device) for k, v in inputs.items()}

        vision_out = self.model.vision_model(**inputs)             # BaseModelOutputWithPooling
        pooled = self._to_tensor(vision_out)                       # (1, hidden)
        proj = self.model.visual_projection(pooled)                # (1, 512)

        vec = proj.detach().cpu().numpy().astype("float32")
        vec = self._l2_normalize_np(vec)[0]
        return vec