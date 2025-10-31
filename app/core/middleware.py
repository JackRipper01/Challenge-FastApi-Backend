import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


async def request_logging_middleware(request: Request, call_next):
    """
    Middleware to log the response time of each request.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(
        f"Request: {request.method} {request.url.path} - Processed in: {process_time:.4f}s")
    return response
