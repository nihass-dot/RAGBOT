# src/config/models.py
import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

# Configure Gemini
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY must be set in environment variables")
genai.configure(api_key=gemini_api_key)

# Embedding model configuration
EMBEDDING_MODEL = "models/embedding-001"

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
generation_model = "llama3-70b-8192"  # Using Llama 3 70B for generation