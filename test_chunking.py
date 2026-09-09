import sys
from rag_core.chunking import TextChunker

def run_test():
    chunker = TextChunker(chunk_size=50, overlap=10)
    
    # A sample long sentence for testing
    sample_text = (
        "This is a long sentence that we will use to test our custom chunking "
        "algorithm. It should split this text into smaller overlapping chunks."
    )
    
    print(f"Original Text Length: {len(sample_text)}")
    print(f"Chunk Size: {chunker.chunk_size}, Overlap: {chunker.overlap}\n")
    
    chunks = chunker.chunk_text(sample_text)
    
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1} (Length: {len(chunk)}):\n'{chunk}'\n")
        
    if len(chunks) > 1 and len(chunks[0]) > 0:
        print("Chunking test passed!")
        sys.exit(0)
    else:
        print("Chunking test failed!")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
