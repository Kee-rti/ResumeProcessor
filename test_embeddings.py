import sys
import numpy as np
from rag_core.embeddings import Embedder

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def run_test():
    embedder = Embedder()
    
    # ---------------------------------------------------------
    # 1. Smoke Test
    # ---------------------------------------------------------
    chunks = [
        "This is the first chunk of text from the resume.",
        "This is the second chunk discussing machine learning.",
        "The third chunk mentions Python and React."
    ]
    
    print("\n--- Running Smoke Test ---")
    print(f"Embedding {len(chunks)} chunks...")
    embeddings = embedder.embed_chunks(chunks)
    
    print(f"Embeddings generated with shape: {embeddings.shape}")
    if embeddings.shape[0] != 3 or embeddings.shape[1] == 0:
        print("Smoke test failed: Incorrect shape.")
        sys.exit(1)
        
    print("Smoke test passed!\n")
    
    # ---------------------------------------------------------
    # 2. Correctness Test
    # ---------------------------------------------------------
    print("--- Running Correctness Test ---")
    A = "I love Python"
    B = "I write Python code"
    C = "The sky is blue"
    
    vecs = embedder.embed_chunks([A, B, C])
    sim_AB = cosine_similarity(vecs[0], vecs[1])
    sim_AC = cosine_similarity(vecs[0], vecs[2])
    
    print(f"Similarity(A, B): {sim_AB:.4f}")
    print(f"Similarity(A, C): {sim_AC:.4f}")
    
    if sim_AB > sim_AC:
        print("Correctness test passed! Semantics are preserved.\n")
    else:
        print("Correctness test failed! Similarity logic is broken.\n")
        sys.exit(1)
        
    sys.exit(0)

if __name__ == "__main__":
    run_test()
