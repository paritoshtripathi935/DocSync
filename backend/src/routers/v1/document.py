from fastapi import APIRouter, status, Query
from typing import List, Dict, Tuple
from src.models.document import Document, DocumentList
from src.services.document_service import DocumentService

class DocumentController:
    def __init__(self):
        self.API_VERSION = "v1"
        self.router = APIRouter()
        self.service = DocumentService()
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            f"/{self.API_VERSION}/documents/",
            self.create_document,
            methods=["POST"],
            response_model=Document,
            status_code=status.HTTP_201_CREATED
        )
        self.router.add_api_route(
            f"/{self.API_VERSION}/documents/",
            self.list_documents,
            methods=["GET"],
            response_model=DocumentList
        )
        self.router.add_api_route(
            f"/{self.API_VERSION}/documents/{{document_id}}",
            self.get_document,
            methods=["GET"],
            response_model=Document
        )
        self.router.add_api_route(
            f"/{self.API_VERSION}/documents/{{document_id}}/history",
            self.get_document_history,
            methods=["GET"],
            response_model=List[Dict]
        )

    async def create_document(self, document: Document) -> Document:
        return await self.service.create(document)

    async def list_documents(
        self,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100)
    ) -> DocumentList:
        documents, total = await self.service.list_all(skip, limit)
        return DocumentList(
            items=documents,
            total=total,
            skip=skip,
            limit=limit
        )

    async def get_document(self, document_id: str) -> Document:
        return await self.service.get(document_id)

    async def get_document_history(
        self,
        document_id: str,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100)
    ) -> List[Dict]:
        return await self.service.get_history(document_id, skip, limit)

# Initialize the controller and expose the router
document_controller = DocumentController()
Document_Api_Router = document_controller.router