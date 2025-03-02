from .api_version import API_VERSION
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from src.models.document import Document
from src.settings.settings import BackendBaseSettings