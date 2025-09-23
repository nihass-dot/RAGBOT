import numpy as np
import json
from typing import List, Dict, Any
from src.config.db import supabase
from src.models.document import Document, DocumentCreate
#Vector search, batch operations, error handling
class DocumentDAO:
    @staticmethod
    def create_document(document: DocumentCreate) -> Document:
        data = document.dict()
        if data["embedding"]:
            # Convert list to string for storage
            data["embedding"] = json.dumps(data["embedding"])
        
        response = supabase.table("documents").insert(data).execute()
        
        if response.data:
            return Document(**response.data[0])
        raise Exception("Failed to create document")
    
    @staticmethod
    def create_documents(documents: List[DocumentCreate]) -> List[Document]:
        data_list = [doc.dict() for doc in documents]
        for data in data_list:
            if data["embedding"]:
                # Convert list to string for storage
                data["embedding"] = json.dumps(data["embedding"])
        
        response = supabase.table("documents").insert(data_list).execute()
        
        if response.data:
            return [Document(**item) for item in response.data]
        raise Exception("Failed to create documents")
    
    @staticmethod
    def search_documents(query_embedding: List[float], top_k: int = 5) -> List[Document]:
        # Convert to numpy array for proper formatting
        query_embedding_np = np.array(query_embedding)
        
        # Perform vector search using Supabase rpc
        response = supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding_np.tolist(),
                "match_count": top_k
            }
        ).execute()
        
        if response.data:
            return [Document(**item) for item in response.data]
        return []
    
    @staticmethod
    def get_all_documents() -> List[Document]:
        response = supabase.table("documents").select("*").execute()
        
        if response.data:
            return [Document(**item) for item in response.data]
        return []
    
    @staticmethod
    def delete_all_documents() -> bool:
        response = supabase.table("documents").delete().neq("id", 0).execute()
        
        if response.data:
            return True
        return False