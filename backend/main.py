from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from src.settings.settings import BackendBaseSettings
from src.utils import RootLoggerConfig
import logging
from src.routers.v1.document import Document_Api_Router

# Application class
class DocSyncApp:
    def __init__(self):
        RootLoggerConfig()
        logging.info("Setting up application")
        self.settings = BackendBaseSettings()
        if not os.getenv("CLERK_JWT_ISSUER"):
            logging.warning("CLERK_JWT_ISSUER not set: auth DISABLED, all requests act as user 'local'")
        self.app = FastAPI(**self.settings.set_backend_app_attributes)
        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        """Configure CORS middleware"""
        logging.info("Setting up middleware")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """Setup all application routes"""
        # Health Check Endpoint
        @self.app.get("/health", tags=["Health"])
        async def health_check():
            logging.info("Health check endpoint")
            return {"status": "healthy"}

        # Include API router when needed
        self.app.include_router(Document_Api_Router, tags=["Documents"])

    def run(self):
        """Run the application server"""
        logging.info("Running application")
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=self.settings.PORT,
            workers=self.settings.NUMBER_OF_WORKERS,
            reload=False
        )


# Create application instance
app_instance = DocSyncApp()
app = app_instance.app

if __name__ == "__main__":
    app_instance.run()