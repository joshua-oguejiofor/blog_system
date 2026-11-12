import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger= logging.getLogger(__name__)


#----Initializing logging middleware 
# This register request method, path, status code and the response time duration
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start= time.time()
        response= await call_next(request) # for the next request
        duration= time.time() - start
        logger.info( #logs the full infomation
            f"{request.method} {request.url.path} "
            f"status={response.status_code} duration={duration:.3f}s"
        )
        return response
 
