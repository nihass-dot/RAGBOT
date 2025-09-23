import os
import time
import json
import numpy as np
from typing import List, Dict, Any
from src.config.models import groq_client, generation_model, text_splitter, EMBEDDING_MODEL, EMBEDDING_DIMENSION, FALLBACK_MODELS
from src.dao.document_dao import DocumentDAO
from src.models.document import DocumentCreate, QueryRequest, QueryResponse
from langchain.docstore.document import Document
import traceback
import ollama
# Implements document processing, querying, and response generation
class RAGService:
    # Rate limiting constants
    REQUEST_DELAY = 0.5  # seconds between requests
    MAX_RETRIES = 3
    RETRY_DELAY = 5.0  # seconds to wait after error
#Embedding generation, document chunking, similarity search, response generation with fallback 
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """Generate embedding using Ollama"""
        try:
            print(f"Generating embedding for text (length: {len(text)})")
            # Use Ollama to generate embedding
            response = ollama.embeddings(
                model=EMBEDDING_MODEL,
                prompt=text
            )
            embedding = response["embedding"]
            print(f"Successfully generated embedding with {len(embedding)} dimensions")
            
            # Validate embedding dimensions
            if len(embedding) != EMBEDDING_DIMENSION:
                print(f"Warning: Embedding has {len(embedding)} dimensions, expected {EMBEDDING_DIMENSION}")
                
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            print(traceback.format_exc())
            raise
    
    @staticmethod
    def generate_response_with_groq(prompt: str) -> str:
        """Generate response using Groq with fallback models"""
        # Try primary model first
        models_to_try = [generation_model] + FALLBACK_MODELS
        
        for model in models_to_try:
            try:
                print(f"Trying Groq model: {model}")
                response = groq_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that provides accurate information about India."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1024
                )
                print(f"Successfully generated response using Groq model: {model}")
                return response.choices[0].message.content
            except Exception as e:
                error_message = str(e)
                print(f"Error with Groq model {model}: {error_message}")
                
                # Skip models that require terms acceptance
                if "terms acceptance" in error_message:
                    print(f"Skipping model {model} as it requires terms acceptance")
                    continue
                    
                # For other errors, continue to next model
                continue
        
        # If all Groq models fail, return None to fall back to Ollama
        return None
    
    @staticmethod
    def generate_response_with_ollama(prompt: str) -> str:
        """Generate response using Ollama"""
        try:
            print("Falling back to Ollama for generation")
            response = ollama.chat(
                model="llama3",  # Use a reliable model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides accurate information about India."},
                    {"role": "user", "content": prompt}
                ]
            )
            print("Successfully generated response using Ollama")
            return response['message']['content']
        except Exception as e:
            print(f"Error generating response with Ollama: {str(e)}")
            return f"I apologize, but I'm currently experiencing technical difficulties. Error: {str(e)}"
    
    @staticmethod
    def generate_response(prompt: str) -> str:
        """Generate response using Groq or Ollama"""
        # First try Groq
        groq_response = RAGService.generate_response_with_groq(prompt)
        if groq_response:
            return groq_response
        
        # Fall back to Ollama
        return RAGService.generate_response_with_ollama(prompt)
    
    @staticmethod
    def process_document(file_path: str, title: str) -> bool:
        """
        Process a document file, chunk it, generate embeddings, and store in database.
        """
        try:
            print(f"Starting to process document: {file_path}")
            
            # Read the file
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                print(f"File read successfully. Length: {len(text)} characters")
                print(f"First 100 characters: {text[:100]}")
            except Exception as e:
                print(f"Error reading file: {str(e)}")
                return False
            
            # Create a LangChain document
            doc = Document(page_content=text, metadata={"title": title})
            
            # Split the document using LangChain
            try:
                chunks = text_splitter.split_documents([doc])
                print(f"Document split into {len(chunks)} chunks")
            except Exception as e:
                print(f"Error splitting document: {str(e)}")
                return False
            
            # Generate embeddings for each chunk and store in database
            documents = []
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}")
                print(f"Chunk length: {len(chunk.page_content)} characters")
                
                # Retry logic for errors
                retry_count = 0
                success = False
                
                while retry_count < RAGService.MAX_RETRIES and not success:
                    try:
                        # Generate embedding using Ollama
                        chunk_embedding = RAGService.generate_embedding(chunk.page_content)
                        print(f"Generated embedding with {len(chunk_embedding)} dimensions")
                        
                        # Create document
                        doc = DocumentCreate(
                            title=title,
                            content=chunk.page_content,
                            chunk_id=f"{title}_{i}",
                            embedding=chunk_embedding
                        )
                        documents.append(doc)
                        success = True
                        
                        # Add delay between successful requests
                        time.sleep(RAGService.REQUEST_DELAY)
                        
                    except Exception as e:
                        retry_count += 1
                        wait_time = RAGService.RETRY_DELAY * retry_count
                        print(f"Error processing chunk (attempt {retry_count}/{RAGService.MAX_RETRIES}): {str(e)}")
                        if retry_count < RAGService.MAX_RETRIES:
                            print(f"Waiting {wait_time} seconds before retry...")
                            time.sleep(wait_time)
                
                if not success:
                    print(f"Failed to process chunk {i+1} after {RAGService.MAX_RETRIES} attempts")
                    continue
            
            print(f"Created {len(documents)} document objects")
            
            if not documents:
                print("No documents were created successfully")
                return False
            
            # Store documents in database
            try:
                result = DocumentDAO.create_documents(documents)
                print(f"Stored {len(result)} documents in database")
                return True
            except Exception as e:
                print(f"Error storing documents in database: {str(e)}")
                print(traceback.format_exc())
                return False
            
        except Exception as e:
            print(f"Error in RAGService.process_document: {str(e)}")
            print(traceback.format_exc())
            return False
    
    @staticmethod
    def query(query_request: QueryRequest) -> QueryResponse:
        """
        Process a user query by retrieving relevant documents and generating a response.
        """
        try:
            print(f"Processing query: {query_request.query}")
            
            # Retry logic for query embedding
            retry_count = 0
            query_embedding = None
            
            while retry_count < RAGService.MAX_RETRIES and query_embedding is None:
                try:
                    # Generate embedding for the query using Ollama
                    query_embedding = RAGService.generate_embedding(query_request.query)
                    print(f"Generated query embedding with {len(query_embedding)} dimensions")
                    
                except Exception as e:
                    retry_count += 1
                    wait_time = RAGService.RETRY_DELAY * retry_count
                    print(f"Error generating query embedding (attempt {retry_count}/{RAGService.MAX_RETRIES}): {str(e)}")
                    if retry_count < RAGService.MAX_RETRIES:
                        print(f"Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
            
            if query_embedding is None:
                return QueryResponse(
                    query=query_request.query,
                    response="Sorry, I'm experiencing issues processing your query right now. Please try again later.",
                    sources=[]
                )
            
            # Retrieve relevant documents
            documents = DocumentDAO.search_documents(query_embedding, query_request.top_k)
            print(f"Retrieved {len(documents)} relevant documents")
            
            # Prepare context from retrieved documents
            context = "\n\n".join([f"Document: {doc.title}\nContent: {doc.content}" for doc in documents])
            print(f"Context length: {len(context)} characters")
            
            # Generate response using Groq or Ollama
            prompt = f"""
            You are a helpful assistant that provides accurate information about India based on the given context.
            If the information is not in the context, politely say that you don't have that information.
            Do not make up answers. Stick to the provided context.
            
            Context:
            {context}
            
            Question: {query_request.query}
            
            Answer:
            """
            
            answer = RAGService.generate_response(prompt)
            print(f"Generated answer: {answer}")
            
            # Extract sources
            sources = list(set([doc.title for doc in documents]))
            
            return QueryResponse(
                query=query_request.query,
                response=answer,
                sources=sources
            )
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            print(traceback.format_exc())
            return QueryResponse(
                query=query_request.query,
                response=f"Sorry, I encountered an error while processing your query: {str(e)}",
                sources=[]
            )
    
    @staticmethod
    def clear_database() -> bool:
        """
        Clear all documents from the database.
        """
        try:
            print("Clearing database...")
            success = DocumentDAO.delete_all_documents()
            print(f"Database cleared: {success}")
            return success
        except Exception as e:
            print(f"Error clearing database: {str(e)}")
            print(traceback.format_exc())
            return False