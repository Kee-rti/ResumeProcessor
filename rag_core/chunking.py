import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextChunker:
    """
    A custom manual implementation of a sliding-window text chunker.
    Splits a large text into smaller chunks of a specified size (in characters),
    with a specified overlap to preserve context across boundaries.
    """
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Splits the input text into a list of chunks.
        """
        if not text:
            return []
            
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            # If we're not at the end of the text, try to find a nice breaking point
            # like a newline or space, rather than cutting a word in half.
            if end < text_length:
                # Look for a newline or space near the end to break cleanly
                last_newline = text.rfind('\n', start, end)
                last_space = text.rfind(' ', start, end)
                
                if last_newline != -1 and last_newline > start + (self.chunk_size // 2):
                    end = last_newline + 1
                elif last_space != -1 and last_space > start + (self.chunk_size // 2):
                    end = last_space + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
                
            if end >= text_length:
                break
                
            # Move the start forward by (chunk_size - overlap)
            # We base it on the actual end we used to ensure the overlap is accurate
            next_start = end - self.overlap
            if next_start <= start:
                next_start = start + 1  # Guarantee forward progress
            start = next_start
            
        logger.info(f"Split text of length {text_length} into {len(chunks)} chunks.")
        return chunks
