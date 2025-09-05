# Car Application

A FastAPI-based REST API for managing car registration data with a scalable architecture using a Neo4j graph database. The app supports secure JWT authentication, handles background tasks with Celery, and is fully containerized with Docker.

---

## Features

- **Modern Tech Stack**: Built with FastAPI for high performance.
- **Graph Database**: Uses Neo4j to manage  relationships between cars, models, and makes.
- **JWT Authentication**: Secure endpoints with `POST /login` and `POST /register`.
- **Full CRUD Operations**: Complete control over car data.
- **Background Tasks**: Asynchronous tasks like data syncing are handled by Celery with Redis.
- **Containerized Deployment**: Easy setup and deployment with Docker and Docker Compose.
- **Schema Validation**: Pydantic is used for robust data validation.

---

## Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Database**: Neo4j
- **Authentication**: JWT (python-jose)
- **Task Queue**: Celery, Redis
- **Validation**: Pydantic
- **Containerization**: Docker & Docker Compose

---

## API Endpoints

All car endpoints require a valid JWT token in the `Authorization: Bearer <token>` header.

| Method | Route                  | Auth | Description                |
|--------|------------------------|------|----------------------------|
| POST   | `/register`            | No   | Register a new user        |
| POST   | `/login`               | No   | Login & get JWT token      |
| GET    | `/`                    | Yes  | List all cars (paginated)  |
| GET    | `/{car_id}`            | Yes  | Get a car by its ID        |
| POST   | `/`                    | Yes  | Create a new car           |
| PATCH  | `/{car_id}`            | Yes  | Partially update a car     |
| PUT    | `/{car_id}`            | Yes  | Replace a car              |
| DELETE | `/{car_id}`            | Yes  | Delete a car by its ID     |

**API Documentation:** `http://localhost:8000/docs`

---

## Database Schema

The data is modeled as a graph in Neo4j:

- **Nodes**: `(:User)`, `(:Car)`, `(:Make)`, `(:Model)`
- **Relationships**:
  - `(:Car)-[:HAS_MODEL]->(:Model)`
  - `(:Model)-[:HAS_MAKE]->(:Make)`

---

## Setup (Local Development)

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- Git

### Clone & Setup
```bash
git clone https://github.com/seemabhassan21/car-application.git
cd car-application
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment File

Create a `.env` file in the project root with the following variables:

```env
# For generating JWT tokens
SECRET_KEY=your-super-secret-key

# Neo4j connection details
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password

# Celery configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# External Car API Credentials
CAR_API_ID=your-api-id
CAR_MASTER_KEY=your-master-key
```

### Start Services (Docker)

The easiest way to run the required services (Neo4j, Redis) is with Docker Compose.

```bash
docker compose up -d neo4j redis
```
Wait for the containers to be fully up and running.

### Start Application

```bash
# Terminal 1: FastAPI App
uvicorn main:app --reload

# Terminal 2: Celery Worker
celery -A app.task.celery_worker.celery worker --loglevel=info

# Terminal 3 (Optional): Celery Beat for scheduled tasks
celery -A app.task.celery_worker.celery beat --loglevel=info
```
Your API will be available at `http://localhost:8000`.

---

## Docker Setup (Full)

To run the entire application stack (including the FastAPI app) in Docker, first configure the `.env` file to use Docker's networking.

### Docker Environment File

Update your `.env` file to point to the service hostnames defined in `docker-compose.yml`:

```env
# Other keys remain the same...

# Use service hostnames for Docker
NEO4J_URI=bolt://neo4j:7687
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Start Services

```bash
# Build and start all services defined in docker-compose.yml
docker compose build --no-cache
docker compose up -d
```

---

## Project Structure

```
car-app/
├── app/
│   ├── api/
│   │   ├── cars/
│   │   └── users/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── repositories/
│   │   ├── car_repository.py
│   │   └── user_repository.py
│   ├── task/
│   │   ├── __init__.py
│   │   ├── celery_worker.py
│   │   └── sync_cars.py
├── docker-compose.yml
├── Dockerfile
├── main.py
├── requirements.txt
└── README.md
```
