import logging
from fastapi import HTTPException
from src.models.document import Document
from src.database.connectors.redis_connector import get_redis_client
from src.utils.database.mongo_handler import MongoHandler
import traceback
from datetime import datetime
from typing import List, Dict, Tuple
from src.utils.serializers import serialize_doc

class DocumentService:
    def __init__(self):
        self.redis_client = get_redis_client()
        self.mongo_handler = MongoHandler()
        self.cache_ttl = 3600  # 1 hour
        self.collection = "documents"
        self.history_collection = "document_history"

    async def create(self, document: Document) -> Document:
        try:
            # Store in MongoDB
            await self.mongo_handler.insert_one(self.collection, document.dict())
            
            # Store in Redis
            self.redis_client.setex(
                f"document:{document.id}",
                self.cache_ttl,
                document.json()
            )
            await self.add_to_history(document)
            return document
        except Exception as e:
            logging.error(f"Error creating document: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create document")

    async def list_all(self, skip: int = 0, limit: int = 10) -> Tuple[List[Document], int]:
        try:
            docs = await self.mongo_handler.find_many(
                self.collection,
                query={},
                skip=skip,
                limit=limit
            )
            total = await self.mongo_handler.count_documents(self.collection, {})
            return [Document(**doc) for doc in docs], total
        except Exception as e:
            logging.info(f"traceback: {traceback.format_exc()}")
            logging.error(f"Error listing documents: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve documents")

    async def get(self, document_id: str) -> Document:
        try:
            cached_doc = await self._get_cached_document(document_id)
            if cached_doc:
                logging.info(f"Document id {document_id} retrieved from cache")
                return cached_doc
            
            mongo_doc = await self.mongo_handler.find_one(
                self.collection, 
                {"id": int(document_id)}
            )
            logging.info(f"Document id {document_id} retrieved from MongoDB result: {mongo_doc}")
            
            if not mongo_doc:
                raise HTTPException(status_code=404, detail="Document not found")
            
            document = Document(**mongo_doc)
            await self._cache_document(document)
            return document
        except HTTPException:
            raise
        except Exception as e:
            logging.info(f"traceback: {traceback.format_exc()}")
            logging.error(f"Error retrieving document: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve document")

    async def _cache_document(self, document: Document):
        self.redis_client.setex(
            f"document:{document.id}",
            self.cache_ttl,
            document.json()
        )

    async def _get_cached_document(self, document_id: str) -> Document | None:
        cached_doc = self.redis_client.get(f"document:{document_id}")
        if cached_doc:
            return Document.parse_raw(cached_doc)
        return None

    async def add_to_history(self, document: Document) -> None:
        try:
            history_entry = {
                "document_id": document.id,
                "content": document.content,
                "version": document.version,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.mongo_handler.insert_one(self.history_collection, history_entry)
        except Exception as e:
            logging.error(f"Error adding document history: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to record document history")

    async def get_history(self, document_id: str, skip: int = 0, limit: int = 10) -> List[Dict]:
        try:
            query = {"document_id": int(document_id)}
            history = await self.mongo_handler.find_many(
                self.history_collection,
                query,
                skip=skip,
                limit=limit,
                sort=[("timestamp", -1)]
            )
            return [serialize_doc(entry) for entry in history]
        except Exception as e:
            logging.error(f"Error retrieving document history: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve document history")
