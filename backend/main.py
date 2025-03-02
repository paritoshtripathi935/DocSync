from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.settings.settings import BackendBaseSettings
from src.utils import RootLoggerConfig
import logging


class DocSyncApp:
    def __init__(self):
        RootLoggerConfig()
        logging.info("Setting up application")
        self.settings = BackendBaseSettings()
        self.app = FastAPI(**self.settings.set_backend_app_attributes)
        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        """Configure CORS middleware"""
        logging.info("Setting up middleware")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
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
        # self.app.include_router(router, prefix="/api/v1")

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