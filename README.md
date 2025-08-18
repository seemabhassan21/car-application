# Car Application

A Flask-based REST API for managing car registration data with a scalable architecture. The app uses Flask-Smorest for API documentation, fetches data from an external car API, stores it in MySQL, and supports secure JWT authentication. Background tasks are handled by Celery with Redis.

---

## Features

- Modern API Framework with Flask-Smorest and Swagger UI
- JWT Authentication: `/api/auth/signup` & `/api/auth/login`
- Full CRUD operations on cars: `/api/cars`
- Normalized Database Schema: Makes, CarModels, Cars, Users
- External API Integration for car data sync
- Background Tasks with Celery
- Periodic Data Sync with Celery Beat
- Database Migrations with Flask-Migrate
- Containerized Deployment with Docker Compose

---

## Tech Stack

- **Backend:** Flask 3.1.1, Flask-Smorest  
- **Database:** MySQL 8, SQLAlchemy ORM  
- **Authentication:** Flask-JWT-Extended  
- **Task Queue:** Celery 5.3.6, Redis  
- **Validation:** Marshmallow  
- **Containerization:** Docker & Docker Compose  
- **Migration:** Flask-Migrate (Alembic)  

---

## API Endpoints

| Method | Route                  | Auth | Description             |
|--------|-----------------------|------|-------------------------|
| POST   | `/api/auth/signup`     | No   | Register a new user     |
| POST   | `/api/auth/login`      | No   | Login & get JWT token   |
| GET    | `/api/cars`            | Yes  | List all cars (paginated) |
| GET    | `/api/cars/<id>`       | Yes  | Get car by ID           |
| POST   | `/api/cars`            | Yes  | Create a new car        |
| PATCH  | `/api/cars/<id>`       | Yes  | Update a car by ID      |
| PUT    | `/api/cars/<id>`       | Yes  | Replace a car by ID     |
| DELETE | `/api/cars/<id>`       | Yes  | Delete car by ID        |

**Swagger UI:** `http://localhost:5000/api/swagger-ui`  

---

## Database Schema

- **Makes:** Car manufacturers  
- **CarModels:** Models with year & make relationship  
- **Cars:** Individual car instances  
- **Users:** Authentication  

---

## Setup (Local Development)

### Prerequisites
- Python 3.8+, MySQL 8.0+, Redis, Git  

### Clone & Setup
```bash
git clone https://github.com/seemabhassan21/car-application.git
cd car-application
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

```

## Environment File

Create `.env` with:

```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
SQLALCHEMY_DATABASE_URI=mysql+pymysql://caruser:carpass@localhost:3306/carbase
CAR_API_ID=your-parse-app-id
CAR_API_KEY=your-parse-master-key
CAR_API_URL=https://parseapi.back4app.com/classes/Car_Model_List?limit=10000
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```


## Database Setup

```bash
mysql -u root -p
CREATE DATABASE carbase;
CREATE USER 'caruser'@'localhost' IDENTIFIED BY 'carpass';
GRANT ALL PRIVILEGES ON carbase.* TO 'caruser'@'localhost';
FLUSH PRIVILEGES;
EXIT;

flask db upgrade
```

## Start Services

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Flask app
python run.py

# Terminal 3: Celery worker
celery -A app.tasks.celery_worker.celery worker --loglevel=info

# Terminal 4 (optional): Celery beat
celery -A app.tasks.celery_worker.celery beat --loglevel=info


## Docker Setup

Create `.env` for Docker (update hostnames for containers):

```env
SQLALCHEMY_DATABASE_URI=mysql+pymysql://caruser:carpass@mysql:3306/carbase
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```


### Start services:
```
docker-compose up --build

```

### Car Management Examples
## List Cars
```
curl -X GET "http://localhost:5000/api/cars?page=1&per_page=10" \
  -H "Authorization: Bearer <your_jwt_token>"

  ```
## Create / Update / Delete
```
curl -X POST / PATCH / PUT / DELETE ... \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{...}'
  ```
Use /api/cars routes with the JWT token in the Authorization header.

## Project Structure

car-application/
├── app
│   ├── config.py
│   ├── extensions.py
│   ├── __init__.py
│   ├── models
│   │   ├── car.py
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routes
│   │   ├── auth
│   │   ├── cars
│   │   ├── common
│   │   └── __init__.py
│   ├── tasks
│   │   ├── celery_worker.py
│   │   ├── __init__.py
│   │   └── sync_cars.py
│   └── utils
│       ├── auth.py
│       ├── db_helper.py
│       └── __init__.py
├── beat-celery.sh
├── docker-compose.yml
├── Dockerfile
├── migrations
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
├── README.md
├── requirements.txt
├── run.py
├── start-celery.sh
└── start.sh

## Background Tasks
sync_cars: Updates DB from external API

Scheduled tasks via Celery Beat

## Manual execution:


celery -A app.tasks.celery_worker.celery call app.tasks.sync_cars.sync_cars


### Authentication
JWT tokens for protected routes

Password hashing with Werkzeug

Include token in Authorization: Bearer <your_jwt_token> header


