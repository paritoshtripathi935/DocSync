# DocSync

A real-time collaborative document editing system with conflict resolution and performance optimization
basically it will be obsidian with AI.

## 🚀 Features

- Real-time document collaboration using WebSocket
- Document version control and conflict resolution
- High-performance caching with Redis
- Scalable message queue system using RabbitMQ
- RESTful API endpoints for document CRUD operations
- Authentication and authorization
- Monitoring and performance metrics

## 🛠️ Tech Stack

- **Backend**: Python (FastAPI)
- **Database**: MongoDB
- **Caching**: Redis
- **Message Queue**: RabbitMQ
- **Frontend**: React + Vite

## 🏗️ Project Structure

```
DocSync/
├── backend/
│   ├── src/
│   │   ├── models/       # Pydantic models
│   │   ├── routers/      # API endpoints
│   │   ├── settings/     # Configuration
│   │   └── utils/        # Helper functions
│   ├── main.py          # Application entry point
│   └── requirements.txt  # Python dependencies
```

## 🚦 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/DocSync.git
   cd DocSync
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env.local   # git-ignored; edit values
   ```

   | Variable | Required | Purpose |
   |---|---|---|
   | `MONGO_URI` | yes | MongoDB connection string |
   | `REDIS_URI` | yes | Redis connection string |
   | `CLERK_JWT_ISSUER` | prod | Clerk Frontend API URL (e.g. `https://xxx.clerk.accounts.dev`). Session JWTs are verified against `<issuer>/.well-known/jwks.json`. **Unset = auth disabled**, every request acts as user `local` (local dev only). |
   | `ALLOWED_ORIGINS` | prod | Comma-separated CORS origins (default `http://localhost:5173`) |
   | `CLERK_JWKS_TTL_SECONDS` | no | JWKS cache TTL (default 3600) |
   | `ENVIRONMENT` | no | `development` (default) exposes `/docs`; anything else hides it |
   | `PORT` | no | Listen port (default 8000) |

   All `/v1/documents/*` endpoints require `Authorization: Bearer <Clerk session JWT>` when auth is enabled. Documents and history are scoped to the caller; other users' documents return 404.

5. **Run the application**
   ```bash
   cd backend
   python main.py
   ```

The server will start at `http://localhost:8000` (health check: `/health`).

## 📚 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Running Tests

```bash
pip install pytest mongomock fakeredis
cd backend && pytest tests/test_auth_and_isolation.py
```

(`tests/test_api.py` is a live-server suite and needs the app running on localhost:8000.)

## 📦 Deployment

**Render** (backend): `backend/render.yaml` is a Blueprint (rootDir `backend`, gunicorn + uvicorn workers, health check `/health`). Create a Blueprint from the repo, then set the secret env vars in the dashboard: `MONGO_URI`, `REDIS_URI` (managed Mongo/Redis, e.g. Atlas + Upstash/Render Redis), `CLERK_JWT_ISSUER`, `ALLOWED_ORIGINS` (your frontend URL). Do not deploy without `CLERK_JWT_ISSUER`, or the API is open to everyone as one shared user.

**Docker** (local stack): `cd backend && docker compose up -d`

## 📜 License

MIT License

## 👥 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
