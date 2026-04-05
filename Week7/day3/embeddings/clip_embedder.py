from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np


@dataclass
class CLIPConfig:
    model_name: str = "openai/clip-vit-base-patch32"
    device: Optional[str] = None  # "cpu" or "cuda" (auto if None)
    normalize: bool = True


class CLIPEembedder:
    """
    CLIP embedder:
      - image -> vector
      - text  -> vector
    Both vectors are in same space => text->image, image->image.
    """

    def __init__(self, cfg: Optional[CLIPConfig] = None):
        self.cfg = cfg or CLIPConfig()

        import torch
        from transformers import CLIPModel, CLIPProcessor

        self.torch = torch
        self.device = self.cfg.device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.model = CLIPModel.from_pretrained(self.cfg.model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(self.cfg.model_name)
        self.model.eval()

    def _normalize(self, arr: np.ndarray) -> np.ndarray:
        arr = arr.astype(np.float32)
        if not self.cfg.normalize:
            return arr
        n = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
        return arr / n

    def embed_text(self, text: str) -> np.ndarray:
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        with self.torch.no_grad():
            feats = self.model.get_text_features(**inputs)  # (1, d)
        arr = feats.detach().cpu().numpy()
        return self._normalize(arr)[0]

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        inputs = self.processor(text=texts, return_tensors="pt", padding=True).to(self.device)
        with self.torch.no_grad():
            feats = self.model.get_text_features(**inputs)  # (n, d)
        arr = feats.detach().cpu().numpy()
        return self._normalize(arr)

    def embed_image(self, pil_image) -> np.ndarray:
        inputs = self.processor(images=[pil_image], return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            feats = self.model.get_image_features(**inputs)  # (1, d)
        arr = feats.detach().cpu().numpy()
        return self._normalize(arr)[0]

    def embed_images(self, pil_images: List) -> np.ndarray:
        inputs = self.processor(images=pil_images, return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            feats = self.model.get_image_features(**inputs)  # (n, d)
        arr = feats.detach().cpu().numpy()
        return self._normalize(arr)