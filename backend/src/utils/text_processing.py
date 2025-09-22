# src/utils/text_processing.py
import re
import tiktoken
from typing import List

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into chunks of specified size with overlap.
    """
    # Clean the text
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Initialize tokenizer
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    
    chunks = []
    start_idx = 0
    
    while start_idx < len(tokens):
        end_idx = min(start_idx + chunk_size, len(tokens))
        chunk_tokens = tokens[start_idx:end_idx]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)
        
        # Move to next chunk with overlap
        start_idx = end_idx - overlap if end_idx < len(tokens) else end_idx
    
    return chunks

def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters.
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\@\#\$\%\^\&\*\+\=\~\`]', '', text)
    
    return text.strip()