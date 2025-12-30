import os
from supabase import create_client, Client
from backend.core.logger import logger
from backend.services.gemini_service import GeminiService

class SupabaseService:
    def __init__(self, url: str = None, key: str = None):
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            logger.warning("Supabase credentials missing. RAG features will be disabled.")
            self.client = None
        else:
            self.client = create_client(self.url, self.key)


            
        self.ai = GeminiService()

    def generate_embedding(self, text: str) -> list:
        return self.ai.generate_embedding(text)

    def store_document(self, content: str, metadata: dict, summary: str):
        if not self.client:
            return
            
        embedding = self.generate_embedding(content)
        
        data = {
            "content": content,
            "metadata": metadata,
            "summary": summary,
            "embedding": embedding
        }
        
        try:
            self.client.table("documents").insert(data).execute()
            logger.info(f"Document stored in Supabase: {metadata.get('filename')}")
        except Exception as e:
            logger.error(f"Failed to store document in Supabase: {str(e)}")
            raise

    def search_documents(self, query: str, threshold: float = 0.7, count: int = 5):
        if not self.client:
            return []
            
        query_embedding = self.generate_embedding(query)
        
        try:
            # Assumes pgvector RPC 'match_documents' is set up in Supabase
            response = self.client.rpc("match_documents", {
                "query_embedding": query_embedding,
                "match_threshold": threshold,
                "match_count": count
            }).execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
