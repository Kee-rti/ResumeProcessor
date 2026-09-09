import os
import logging
from typing import List
import numpy as np

import truststore
truststore.inject_into_ssl()

from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Embedder:
    """
    Manual embedding generator using sentence-transformers.
    Converts text chunks into dense vector representations.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        logger.info("Model loaded successfully.")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embeds a single string into a numpy vector.
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def embed_chunks(self, chunks: List[str]) -> np.ndarray:
        """
        Embeds a list of strings into a 2D numpy array of vectors.
        """
        if not chunks:
            return np.array([])
        
        logger.info(f"Embedding {len(chunks)} chunks...")
        embeddings = self.model.encode(chunks, convert_to_numpy=True)
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings
