import json
import logging
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from src.models.document import Document
from src.database.connectors.redis_connector import get_redis_client
from src.database.connectors.mongo_connector import get_mongo_instance
import traceback

class DocumentService:
    def __init__(self):
        self.redis_client = get_redis_client()
        self.mongo_db = get_mongo_instance()
        self.cache_ttl = 3600  # 1 hour

    async def create(self, document: Document) -> Document:
        try:
            # Store in MongoDB using document's own id
            self.mongo_db.documents.insert_one(document.dict())
            
            # Store in Redis
            self.redis_client.setex(
                f"document:{document.id}",
                self.cache_ttl,
                document.json()
            )
            return document
        except Exception as e:
            logging.error(f"Error creating document: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create document")

    async def list_all(self) -> list[Document]:
        try:
            documents = []
            # Convert to list to properly handle async cursor
            docs = self.mongo_db.documents.find({}).to_list(length=None)
            for doc in docs:
                documents.append(Document(**doc))
            return documents
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
            
            collection = self.mongo_db.documents
            mongo_doc = collection.find_one({"id": int(document_id)})
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
