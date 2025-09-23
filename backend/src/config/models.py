import os
from groq import Groq
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
import ollama

load_dotenv()

# Configure Ollama for embeddings
EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIMENSION = 768  # nomic-embed-text produces 768-dimensional embeddings

# LangChain text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)

# Configure Groq
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY must be set in environment variables")
groq_client = Groq(api_key=groq_api_key)

# Use one of the available models that doesn't require terms acceptance
generation_model = "llama-3.1-8b-instant"  # Primary model

# Fallback models (other available models that don't require terms acceptance)
FALLBACK_MODELS = [
    "gemma2-9b-it",
    "llama-3.3-70b-versatile",
    "qwen/qwen3-32b",
    "deepseek-r1-distill-llama-70b"
]