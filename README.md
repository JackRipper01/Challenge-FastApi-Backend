# FastCRUD API

This is a RESTful API built with FastAPI, Pydantic v2, and SQLAlchemy, demonstrating a full CRUD (Create, Read, Update, Delete) implementation with advanced features like authentication, soft-delete, pagination and containerized deployment with Docker.

## Features

*   **FastAPI** for building the API endpoints.
*   **Pydantic v2** for data validation and serialization.
*   **SQLAlchemy** with `asyncpg` for asynchronous database operations.
*   **PostgreSQL** as the primary database.
*   **Alembic** for database migrations.
*   **OAuth2 with JWT** for secure endpoint protection (registration, login, token generation).
*   **Generic Mixins** for `created_at`, `updated_at` timestamps and `is_deleted` (soft-delete).
*   **Custom Soft-Delete** implementation, excluding deleted items from default queries.
*   **Role-Based Access Control** (Superuser for user management, Post/Comment ownership for modification/deletion).
*   **Modular Routers** for organized endpoint structure.
*   **Custom Middleware** for logging request response times.
*   **Pagination** for efficient data retrieval in listing endpoints.
*   **Docker & Docker Compose** for containerized deployment.

---

## Getting Started

You can run this project either locally with a native Python environment and PostgreSQL, or using Docker for a fully containerized setup.

### Getting Started with Docker (Recommended)

This method provides a consistent and isolated environment, simplifying setup and deployment.

#### Prerequisites

Ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running on your system.

#### 1. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone https://github.com/JackRipper01/Challenge-FastApi-Backend 
cd project # the directory name should be 'Challenge-FastApi-Backend' but for generalization let's call it 'project'
```
**Note**: The following instructions assume you are inside the `project` directory.

#### 2. Configure Environment Variables

Create a `.env` file in the `project` directory. This file stores your database connection string and application secrets.

```dotenv
DATABASE_URL="postgresql+asyncpg://fastcrud_user:fastcrud_password@db:5432/fastcrud_db"
SECRET_KEY="YOUR_SUPER_SECRET_KEY_HERE" # IMPORTANT: Replace with a strong, random 32-byte hex string (e.g., secrets.token_hex(32))
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# These will be used by the 'db' service in docker-compose.yml
DB_USER="fastcrud_user"
DB_PASSWORD="fastcrud_password"
DB_NAME="fastcrud_db"
```
**Important:**
*   For `SECRET_KEY`, generate a strong, random string for production. A quick way to generate one in Python is `import secrets; print(secrets.token_hex(32))`.
*   Notice that `DATABASE_URL` for Docker uses `db` as the host, which is the service name of our PostgreSQL container within the Docker network, not `localhost`.

#### 3. Build and Run the Containers

From the `project` directory, execute the following command to build the Docker images and start the services:

```bash
docker compose up --build -d
```
*   `--build`: Forces a rebuild of images, useful after code changes.
*   `-d`: Runs the containers in detached mode (in the background).

This command will:
*   Pull the `postgres:16-alpine` image if not already present.
*   Build your FastAPI application's Docker image using the `Dockerfile`.
*   Start the PostgreSQL database service (`db`).
*   Wait for the database to become healthy.
*   Start the FastAPI application service (`app`), running Alembic migrations (`alembic upgrade head`) before starting the Uvicorn server.

#### 4. Verify Services and Access API

*   **Check container status:**
    ```bash
    docker compose ps
    ```
    You should see `fastcrud_db` and `fastcrud_app` running.

*   **View application logs:**
    ```bash
    docker compose logs -f app
    ```
    (Press `Ctrl+C` to exit the log stream)

*   **Access the API:**
    Your FastAPI application will be accessible at `http://localhost:8000`.
    Open your web browser and navigate to `http://localhost:8000/docs` to view the interactive API documentation (Swagger UI).

#### 5. Stop and Remove Containers

When you're finished, you can stop and remove all services:

```bash
docker compose down
```
To also remove the persistent database volume (which will delete all your data), use:

```bash
docker compose down -v
```

---

### Getting Started Locally (Without Docker)

Follow these steps to set up and run the project on your local machine using a native Python environment and PostgreSQL.

#### Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.11+**:
    *   [Download Python](https://www.python.org/downloads/)
*   **PostgreSQL**:
    *   [Download PostgreSQL](https://www.postgresql.org/download/)

#### 1. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone https://github.com/JackRipper01/Challenge-FastApi-Backend 
cd project # the directory name should be 'Challenge-FastApi-Backend' but for generalization let's call it 'project'
```
**Note**: The instructions assume you are inside the `project` directory.

#### 2. Set up a Virtual Environment

It's recommended to use a virtual environment to manage project dependencies.

```bash
python3 -m venv .venv
```

Activate the virtual environment:

*   **macOS/Linux:**
    ```bash
    source ./.venv/bin/activate
    ```
*   **Windows:**
    ```bash
    .venv\Scripts\activate
    ```

#### 3. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

#### 4. Database Setup (PostgreSQL)

You need a running PostgreSQL instance. If you don't have one, install it natively as per the prerequisites.

##### 4.1. Create Database and User

Access your PostgreSQL command line (e.g., `psql`) as the `postgres` superuser:

```bash
sudo -u postgres psql
```

Then, execute the following SQL commands to create a dedicated database and user for the application:

```sql
CREATE DATABASE fastcrud_db;
CREATE USER fastcrud_user WITH PASSWORD 'fastcrud_password';
GRANT ALL PRIVILEGES ON DATABASE fastcrud_db TO fastcrud_user;
\q
```

##### 4.2. Configure Environment Variables

Create a `.env` file in the `project` directory with the following content. This file stores your database connection string and application secrets.

```dotenv
DATABASE_URL="postgresql+asyncpg://fastcrud_user:fastcrud_password@localhost:5432/fastcrud_db"
SECRET_KEY="YOUR_SUPER_SECRET_KEY_HERE" # IMPORTANT: Replace with a strong, random 32-byte hex string
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
**Important:** For `SECRET_KEY`, ensure you use a strong, random string in a production environment. The provided key is for demonstration purposes.

#### 5. Run Database Migrations

Apply the database schema changes using Alembic:

```bash
alembic upgrade head
```
This command will create all necessary tables and relationships in your `fastcrud_db` database.

#### 6. Run the FastAPI Application

With all dependencies installed and the database set up, you can now run the FastAPI application:

```bash
uvicorn app.api.main:app --reload
```

The `--reload` flag enables auto-reloading of the server when code changes are detected, which is useful for development.

Your API will be accessible at `http://127.0.0.1:8000`.
You can view the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.