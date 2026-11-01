import logging
from fastapi import HTTPException
from src.models.document import Document, DocumentUpdate
from src.database.connectors.redis_connector import get_redis_client
from src.utils.database.mongo_handler import MongoHandler
import re
from pymongo.errors import DuplicateKeyError
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
        try:  # ids are global; the unique index makes max+1 assignment race-safe
            self.mongo_handler.db[self.collection].create_index("id", unique=True)
        except Exception as e:
            logging.error(f"Could not create unique index on documents.id: {e}")

    def _key(self, owner_id: str, doc_id) -> str:
        return f"document:{owner_id}:{doc_id}"

    @staticmethod
    def _int_id(document_id) -> int:
        try:
            return int(document_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=404, detail="Document not found")

    async def create(self, document: Document, owner_id: str) -> Document:
        try:
            now = datetime.utcnow().isoformat()
            document.created_at = document.created_at or now
            document.updated_at = document.updated_at or now
            # The server always assigns the id (a client-supplied one could collide with another user's doc).
            for _ in range(10):
                last = await self.mongo_handler.find_many(self.collection, {}, limit=1, sort=[("id", -1)])
                document.id = last[0]["id"] + 1 if last else 1
                try:
                    await self.mongo_handler.insert_one(self.collection, {**document.dict(), "owner_id": owner_id})
                    break
                except DuplicateKeyError:
                    continue  # lost the race for this id; recompute
            else:
                raise RuntimeError("could not allocate a unique document id")
            await self._cache_document(document, owner_id)
            await self.add_to_history(document, owner_id)
            return document
        except Exception as e:
            logging.error(f"Error creating document: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create document")

    async def list_all(self, owner_id: str, skip: int = 0, limit: int = 10, q: str | None = None) -> Tuple[List[Document], int]:
        try:
            query = {"owner_id": owner_id}
            if q:
                pattern = {"$regex": re.escape(q), "$options": "i"}
                query["$or"] = [{"title": pattern}, {"content": pattern}, {"tags": pattern}]
            docs = await self.mongo_handler.find_many(
                self.collection,
                query=query,
                skip=skip,
                limit=limit,
                sort=[("updated_at", -1)]
            )
            total = await self.mongo_handler.count_documents(self.collection, query)
            return [Document(**doc) for doc in docs], total
        except Exception as e:
            logging.info(f"traceback: {traceback.format_exc()}")
            logging.error(f"Error listing documents: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve documents")

    async def get(self, document_id: str, owner_id: str) -> Document:
        doc_id = self._int_id(document_id)
        try:
            cached_doc = await self._get_cached_document(doc_id, owner_id)
            if cached_doc:
                logging.info(f"Document id {document_id} retrieved from cache")
                return cached_doc
            
            mongo_doc = await self.mongo_handler.find_one(
                self.collection, 
                {"id": doc_id, "owner_id": owner_id}
            )
            
            if not mongo_doc:
                raise HTTPException(status_code=404, detail="Document not found")
            
            document = Document(**mongo_doc)
            await self._cache_document(document, owner_id)
            return document
        except HTTPException:
            raise
        except Exception as e:
            logging.info(f"traceback: {traceback.format_exc()}")
            logging.error(f"Error retrieving document: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve document")

    async def update(self, document_id: str, changes: DocumentUpdate, owner_id: str) -> Document:
        current = await self.get(document_id, owner_id)
        fields = changes.dict(exclude_unset=True, exclude_none=True)
        if not fields:
            return current
        updated = current.copy(update={
            **fields,
            "version": current.version + 1,
            "updated_at": datetime.utcnow().isoformat(),
        })
        try:
            await self.mongo_handler.update_one(self.collection, {"id": updated.id, "owner_id": owner_id}, updated.dict())
            await self._cache_document(updated, owner_id)
        except Exception as e:
            logging.error(f"Error updating document: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update document")
        await self.add_to_history(updated, owner_id)
        return updated

    async def delete(self, document_id: str, owner_id: str) -> None:
        doc_id = self._int_id(document_id)
        try:
            deleted = await self.mongo_handler.delete_one(self.collection, {"id": doc_id, "owner_id": owner_id})
            self.redis_client.delete(self._key(owner_id, doc_id))
        except Exception as e:
            logging.error(f"Error deleting document: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete document")
        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")

    async def _cache_document(self, document: Document, owner_id: str):
        self.redis_client.setex(self._key(owner_id, document.id), self.cache_ttl, document.json())

    async def _get_cached_document(self, doc_id: int, owner_id: str) -> Document | None:
        cached_doc = self.redis_client.get(self._key(owner_id, doc_id))
        if cached_doc:
            return Document.parse_raw(cached_doc)
        return None

    async def add_to_history(self, document: Document, owner_id: str) -> None:
        try:
            history_entry = {
                "document_id": document.id,
                "owner_id": owner_id,
                "content": document.content,
                "title": document.title,
                "version": document.version,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.mongo_handler.insert_one(self.history_collection, history_entry)
        except Exception as e:
            logging.error(f"Error adding document history: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to record document history")

    async def get_history(self, document_id: str, owner_id: str, skip: int = 0, limit: int = 10) -> List[Dict]:
        try:
            query = {"document_id": self._int_id(document_id), "owner_id": owner_id}
            history = await self.mongo_handler.find_many(
                self.history_collection,
                query,
                skip=skip,
                limit=limit,
                sort=[("timestamp", -1)]
            )
            return [{k: v for k, v in serialize_doc(entry).items() if k != "owner_id"} for entry in history]
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error retrieving document history: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve document history")
