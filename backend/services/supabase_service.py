import os
from supabase import create_client, Client
from core.logger import logger
from services.gemini_service import GeminiService


class SupabaseService:
    def __init__(self, url: str = None, key: str = None):
        from dotenv import load_dotenv
        from pathlib import Path
        BASE_DIR = Path(__file__).resolve().parent.parent
        load_dotenv(dotenv_path=BASE_DIR / '.env')
        
        self.url = url or os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_ANON_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            logger.warning(f"Supabase credentials missing! URL: {bool(self.url)}, Key: {bool(self.key)}")
            self.client = None
        else:
            logger.info(f"Connecting to Supabase at {self.url[:15]}...")
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
            logger.info(f"Attempting to insert into Supabase: {metadata.get('filename')}")
            response = self.client.table("documents").insert(data).execute()
            
            if response.data and len(response.data) > 0:
                doc_id = response.data[0].get('id')
                logger.info(f"Document stored successfully. ID: {doc_id}")
                return doc_id
            
            logger.warning(f"Supabase returned empty data. Response: {response}")
            return None
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
