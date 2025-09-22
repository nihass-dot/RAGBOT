# src/controllers/rag_controller.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
from src.services.rag_service import RAGService
from src.models.document import QueryRequest, QueryResponse
import traceback
import os

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint for testing"""
    return {"message": "RAG System API is running"}

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

@router.get("/check-env")
async def check_env():
    """
    Check environment variables.
    """
    return {
        "SUPABASE_URL": os.environ.get("SUPABASE_URL", "NOT SET"),
        "SUPABASE_KEY": os.environ.get("SUPABASE_KEY", "NOT SET")[:10] + "..." if os.environ.get("SUPABASE_KEY") else "NOT SET",
        "GROQ_API_KEY": os.environ.get("GROQ_API_KEY", "NOT SET")[:10] + "..." if os.environ.get("GROQ_API_KEY") else "NOT SET",
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "NOT SET")[:10] + "..." if os.environ.get("GEMINI_API_KEY") else "NOT SET",
    }

@router.post("/process-document", response_model=dict)
async def process_document(file: UploadFile = File(...), title: str = Form(...)):
    """
    Process a document file, chunk it, generate embeddings, and store in database.
    """
    try:
        # Check if file is empty
        if file.filename == "":
            raise HTTPException(status_code=400, detail="No file selected")
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Save the uploaded file
        file_path = f"data/{file.filename}"
        print(f"Saving file to: {file_path}")
        
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
            print(f"File size: {len(content)} bytes")
        
        # Process the document
        print(f"Processing document: {title}")
        success = RAGService.process_document(file_path, title)
        
        if success:
            return {"status": "success", "message": f"Document '{title}' processed and stored successfully."}
        else:
            raise HTTPException(status_code=500, detail="Failed to process document.")
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query_documents(query_request: QueryRequest):
    """
    Process a user query by retrieving relevant documents and generating a response.
    """
    try:
        return RAGService.query(query_request)
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.delete("/clear-database", response_model=dict)
async def clear_database():
    """
    Clear all documents from the database.
    """
    try:
        success = RAGService.clear_database()
        
        if success:
            return {"status": "success", "message": "Database cleared successfully."}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear database.")
    except Exception as e:
        print(f"Error clearing database: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")