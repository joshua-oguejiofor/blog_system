import json
import logging
import sys
from contextlib import asynccontextmanager

from admin import admin
from core.config import settings
from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from middleware.logging import LoggingMiddleware
from middleware.rate_limiter import setup_rate_limiter
from routes import (
    audit,
    auth,
    bookmark,
    categories,
    comments,
    likes,
    media,
    notification,
    post,
    tags,
    user,
)
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

logging.basicConfig(
    level= logging.INFO,
    format= ("%(asctime)s - %(levelname)s - %(name)s - %(message)s"),    
    handlers= [
        logging.StreamHandler(sys.stdout)
        ]
)

logger= logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Blog API...")
    await admin.register_admin_user()
    
    yield
    logger.info("Shutting down Blog API...")


app= FastAPI(
    title= settings.PROJECT_NAME, 
    version= settings.VERSION, 
    docs_url= "/api/v1/docs",
    redoc_url= "/api/v1/redoc",
    lifespan= lifespan,
    openapi_url="/api/v1/openapi.json",
)


setup_rate_limiter(app)



app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(LoggingMiddleware)


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {
        "status": "Healthy", 
        "version": settings.VERSION, 
        "service": "Blog API"}


app.include_router(tags.router, prefix= "/api/v1/tags", tags=["tag"])
app.include_router(post.router, prefix= "/api/v1/posts", tags=["post"])
app.include_router(user.router, prefix= "/api/v1/users", tags=["user"])
app.include_router(media.router, prefix= "/api/v1/medias", tags=["media"])
app.include_router(likes.router, prefix= "/api/v1/likes", tags=["likes"])
app.include_router(auth.router, prefix= "/api/v1/auth", tags=["Authentication"])
app.include_router(audit.router, prefix="/api/v1/auditlogs", tags=["auditlogs"])
app.include_router(bookmark.router, prefix= "/api/v1/bookmarks", tags=["bookmark"])
app.include_router(comments.router, prefix= "/api/v1/comments", tags=["comments"])
app.include_router(categories.router, prefix= "/api/v1/categories", tags=["categories"])
app.include_router(notification.router, prefix= "/api/v1/notifications", tags=["notification"])



@app.exception_handler(RateLimitExceeded)
async def ratelimit_error_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error {exc}", exc_info= True)
    return JSONResponse(
        status_code= 429,
        content={
            "status":"error",
            "message": "Too may request. Try again after some time."
        }
    )

@app.exception_handler(json.JSONDecodeError)
async def json_error_handler(request, exc: json.JSONDecodeError):
    logger.info(f"Unhandled error {exc}", exc_info= True)
    return JSONResponse(
        status_code= 400,
        content= {
         "status":"error",
            "message": "social_links must be valid JSON."
        }
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc: IntegrityError):
    error = str(exc.orig)

    if "UNIQUE constraint failed" in error:
        field= error.split(":")[-1].strip()# this splits the error message and return the last value
        field= field.split(".")[0]
        logger.warning(f"Unhandled error: {error}")
        return JSONResponse(
            status_code=409,
            content={
                "status": "error",
                "message": f"Duplicate value for {field}"
            }
        )
    logger.warning(f"Unhandled error: {error}")
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "message": error
        }
    )
 
 
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error {exc}", exc_info= True)
    return JSONResponse(
        status_code= 500,
        content={
            "status":"error",
            "message":"Something went wrong, try again later."
        }
    )


