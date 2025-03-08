from fastapi import APIRouter, status
from typing import List
from src.models.document import Document
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
            response_model=List[Document]
        )
        self.router.add_api_route(
            f"/{self.API_VERSION}/documents/{{document_id}}",
            self.get_document,
            methods=["GET"],
            response_model=Document
        )

    async def create_document(self, document: Document) -> Document:
        return await self.service.create(document)

    async def list_documents(self) -> List[Document]:
        return await self.service.list_all()

    async def get_document(self, document_id: str) -> Document:
        return await self.service.get(document_id)

# Initialize the controller and expose the router
document_controller = DocumentController()
Document_Api_Router = document_controller.router