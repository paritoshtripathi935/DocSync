from fastapi import APIRouter, Depends, status, Query, Response
from typing import List, Dict, Optional
from src.models.document import Document, DocumentList, DocumentUpdate
from src.utils.auth import get_user_id
from src.services.document_service import DocumentService

class DocumentController:
    def __init__(self):
        self.API_VERSION = "v1"
        self.router = APIRouter(dependencies=[Depends(get_user_id)])
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
            f"/{self.API_VERSION}/documents/{{document_id}}",
            self.update_document,
            methods=["PATCH"],
            response_model=Document
        )
        self.router.add_api_route(
            f"/{self.API_VERSION}/documents/{{document_id}}",
            self.delete_document,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT
        )
        self.router.add_api_route(
            f"/{self.API_VERSION}/documents/{{document_id}}/history",
            self.get_document_history,
            methods=["GET"],
            response_model=List[Dict]
        )

    async def create_document(self, document: Document, user_id: str = Depends(get_user_id)) -> Document:
        return await self.service.create(document, user_id)

    async def list_documents(
        self,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
        q: Optional[str] = Query(default=None, description="Search title, content and tags"),
        user_id: str = Depends(get_user_id)
    ) -> DocumentList:
        documents, total = await self.service.list_all(user_id, skip, limit, q)
        return DocumentList(
            items=documents,
            total=total,
            skip=skip,
            limit=limit
        )

    async def get_document(self, document_id: str, user_id: str = Depends(get_user_id)) -> Document:
        return await self.service.get(document_id, user_id)

    async def update_document(self, document_id: str, changes: DocumentUpdate, user_id: str = Depends(get_user_id)) -> Document:
        return await self.service.update(document_id, changes, user_id)

    async def delete_document(self, document_id: str, user_id: str = Depends(get_user_id)) -> Response:
        await self.service.delete(document_id, user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def get_document_history(
        self,
        document_id: str,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
        user_id: str = Depends(get_user_id)
    ) -> List[Dict]:
        return await self.service.get_history(document_id, user_id, skip, limit)

# Initialize the controller and expose the router
document_controller = DocumentController()
Document_Api_Router = document_controller.router