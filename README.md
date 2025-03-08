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
   Create a `.env` file in the backend directory:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   REDIS_URL=redis://localhost:6379
   RABBITMQ_URL=amqp://guest:guest@localhost:5672
   ```

5. **Run the application**
   ```bash
   cd backend
   python main.py
   ```

The server will start at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Running Tests

```bash
pytest backend/tests
```

## 📦 Deployment

The application can be deployed using Docker:

```bash
docker compose up -d
```

## 📜 License

MIT License

## 👥 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
