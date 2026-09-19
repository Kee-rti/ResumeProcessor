import numpy as np
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NumpyVectorStore:
    """
    A naive vector store using pure numpy arrays.
    Keeps a parallel list of text chunks and their corresponding embedding vectors.
    """
    def __init__(self):
        self.chunks: List[str] = []
        self.embeddings: np.ndarray = None

    def add_documents(self, chunks: List[str], embeddings: np.ndarray):
        """
        Add chunks and their pre-computed embeddings to the store.
        """
        if len(chunks) != embeddings.shape[0]:
            raise ValueError("Number of chunks must match number of embeddings.")
            
        if self.embeddings is None:
            self.embeddings = embeddings
            self.chunks = list(chunks)
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])
            self.chunks.extend(chunks)
            
        logger.info(f"Added {len(chunks)} documents. Total in store: {len(self.chunks)}.")

    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Tuple[float, str]]:
        """
        Calculate cosine similarity between the query and all stored embeddings.
        Returns the top_k most similar chunks along with their similarity scores.
        """
        if self.embeddings is None or len(self.chunks) == 0:
            logger.warning("Vector store is empty.")
            return []

        # Ensure query is 1D
        query_vec = query_embedding.flatten()
        
        # Calculate Cosine Similarity
        # dot_product(a, b) / (norm(a) * norm(b))
        
        # 1. Compute dot products of the query with all stored embeddings
        dot_products = np.dot(self.embeddings, query_vec)
        
        # 2. Compute norms
        query_norm = np.linalg.norm(query_vec)
        embeddings_norms = np.linalg.norm(self.embeddings, axis=1)
        
        # 3. Compute cosine similarities
        # Add a tiny epsilon to avoid division by zero
        similarities = dot_products / (query_norm * embeddings_norms + 1e-10)
        
        # 4. Sort indices in descending order
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((float(similarities[idx]), self.chunks[idx]))
            
        return results
