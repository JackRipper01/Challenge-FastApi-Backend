# FastCRUD API

This is a RESTful API built with FastAPI, Pydantic v2, and SQLAlchemy, demonstrating a full CRUD (Create, Read, Update, Delete) implementation with advanced features like authentication, soft-delete, and pagination.

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
*   **Docker & Docker Compose** for containerized deployment (covered in a later section).

---

## Getting Started Locally

Follow these steps to set up and run the project on your local machine without Docker.

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.11+**:
    *   [Download Python](https://www.python.org/downloads/)
*   **PostgreSQL**:
    *   [Download PostgreSQL](https://www.postgresql.org/download/)

### 1. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone https://github.com/your-username/your-repo-name.git # Replace with your actual repo URL
cd your-repo-name/project # Navigate into the 'project' directory
```
**Note**: The instructions assume you are inside the `project` directory.

### 2. Set up a Virtual Environment

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

### 3. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Database Setup (PostgreSQL)

You need a running PostgreSQL instance. If you don't have one, install it natively as per the prerequisites.

#### 4.1. Create Database and User

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

#### 4.2. Configure Environment Variables

Create a `.env` file in the `project` directory with the following content. This file stores your database connection string and application secrets.

```dotenv
DATABASE_URL="postgresql+asyncpg://fastcrud_user:fastcrud_password@localhost:5432/fastcrud_db"
SECRET_KEY="700f128be9d6bf9b675ac0266faf580b707165e6aagafac82e0708ad51aacbcf"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
**Important:** For `SECRET_KEY`, ensure you use a strong, random string in a production environment. The provided key is for demonstration purposes.

### 5. Run Database Migrations

Apply the database schema changes using Alembic:

```bash
alembic upgrade head
```
This command will create all necessary tables and relationships in your `fastcrud_db` database.

### 6. Run the FastAPI Application

With all dependencies installed and the database set up, you can now run the FastAPI application:

```bash
uvicorn app.api.main:app --reload
```

The `--reload` flag enables auto-reloading of the server when code changes are detected, which is useful for development.

Your API will be accessible at `http://127.0.0.1:8000`.
You can view the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

---
