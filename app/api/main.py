from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.api.routes import users, auth, posts, comments,tags
from app.core.middleware import request_logging_middleware


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Generates unique operation IDs for OpenAPI schema.
    This improves readability in the generated documentation (e.g., Swagger UI).
    """
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title="FastCRUD API",
    version="0.1.0",
    description="A RESTful API built with FastAPI, Pydantic v2, and SQLAlchemy.",
    generate_unique_id_function=custom_generate_unique_id,
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(posts.router, prefix="/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
app.include_router(tags.router, prefix="/tags", tags=["Tags"])

app.middleware("http")(request_logging_middleware)
