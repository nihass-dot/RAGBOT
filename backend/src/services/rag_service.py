# src/services/rag_service.py
import os
import time
from typing import List, Dict, Any
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from src.config.models import groq_client, generation_model, text_splitter, EMBEDDING_MODEL
from src.dao.document_dao import DocumentDAO
from src.models.document import DocumentCreate, QueryRequest, QueryResponse
from langchain.docstore.document import Document
import traceback

class RAGService:
    # Rate limiting constants
    REQUEST_DELAY = 1.0  # seconds between requests
    MAX_RETRIES = 3
    RETRY_DELAY = 60.0  # seconds to wait after rate limit error
    
    @staticmethod
    def process_document(file_path: str, title: str) -> bool:
        """
        Process a document file, chunk it, generate embeddings, and store in database.
        """
        try:
            print(f"Starting to process document: {file_path}")
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            print(f"File read successfully. Length: {len(text)} characters")
            print(f"First 100 characters: {text[:100]}")
            
            # Create a LangChain document
            doc = Document(page_content=text, metadata={"title": title})
            
            # Split the document using LangChain
            chunks = text_splitter.split_documents([doc])
            print(f"Document split into {len(chunks)} chunks")
            
            # Generate embeddings for each chunk and store in database
            documents = []
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}")
                print(f"Chunk length: {len(chunk.page_content)} characters")
                
                # Retry logic for rate limiting
                retry_count = 0
                success = False
                
                while retry_count < RAGService.MAX_RETRIES and not success:
                    try:
                        # Generate embedding using genai.embed_content directly
                        result = genai.embed_content(
                            model=EMBEDDING_MODEL,
                            content=chunk.page_content,
                            task_type="retrieval_document"
                        )
                        chunk_embedding = result['embedding']
                        print(f"Generated embedding with {len(chunk_embedding)} dimensions")
                        
                        # Validate embedding dimensions
                        if len(chunk_embedding) != 768:
                            print(f"Warning: Embedding has {len(chunk_embedding)} dimensions, expected 768")
                        
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
                        
                    except ResourceExhausted as e:
                        retry_count += 1
                        wait_time = RAGService.RETRY_DELAY * retry_count
                        print(f"Rate limit exceeded (attempt {retry_count}/{RAGService.MAX_RETRIES}). Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                    except Exception as e:
                        print(f"Error processing chunk {i+1}: {str(e)}")
                        print(traceback.format_exc())
                        break
                
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
                    # Generate embedding for the query using genai.embed_content directly
                    result = genai.embed_content(
                        model=EMBEDDING_MODEL,
                        content=query_request.query,
                        task_type="retrieval_query"
                    )
                    query_embedding = result['embedding']
                    print(f"Generated query embedding with {len(query_embedding)} dimensions")
                    
                    # Validate embedding dimensions
                    if len(query_embedding) != 768:
                        print(f"Warning: Query embedding has {len(query_embedding)} dimensions, expected 768")
                    
                except ResourceExhausted as e:
                    retry_count += 1
                    wait_time = RAGService.RETRY_DELAY * retry_count
                    print(f"Rate limit exceeded for query (attempt {retry_count}/{RAGService.MAX_RETRIES}). Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                except Exception as e:
                    print(f"Error generating query embedding: {str(e)}")
                    print(traceback.format_exc())
                    return QueryResponse(
                        query=query_request.query,
                        response=f"Sorry, I encountered an error while processing your query: {str(e)}",
                        sources=[]
                    )
            
            if query_embedding is None:
                return QueryResponse(
                    query=query_request.query,
                    response="Sorry, I'm experiencing high demand right now. Please try again later.",
                    sources=[]
                )
            
            # Retrieve relevant documents
            documents = DocumentDAO.search_documents(query_embedding, query_request.top_k)
            print(f"Retrieved {len(documents)} relevant documents")
            
            # Prepare context from retrieved documents
            context = "\n\n".join([f"Document: {doc.title}\nContent: {doc.content}" for doc in documents])
            print(f"Context length: {len(context)} characters")
            
            # Generate response using Groq
            prompt = f"""
            You are a helpful assistant that provides accurate information about India based on the given context.
            If the information is not in the context, politely say that you don't have that information.
            Do not make up answers. Stick to the provided context.
            
            Context:
            {context}
            
            Question: {query_request.query}
            
            Answer:
            """
            
            response = groq_client.chat.completions.create(
                model=generation_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides accurate information about India."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1024
            )
            
            answer = response.choices[0].message.content
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