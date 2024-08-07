from fastapi import Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.database.connector import connect_to_db
from app.database.schemas.logs import RequestLog

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request_body = await request.body()

        async def receive() -> dict:
            return {"type": "http.request", "body": request_body, "more_body": False}

        original_receive = request._receive
        request._receive = receive

        try:
            response = await call_next(request)
        finally:
            request._receive = original_receive

        engine, SessionLocal = connect_to_db()
        session = SessionLocal()

        try:
            log_entry = RequestLog(
                endpoint=request.url.path,
                method=request.method,
                request_body=request_body.decode('utf-8') if request_body else None
            )
            session.add(log_entry)
            session.commit()
        except Exception as e:
            print(f"Logging error: {e}")
        finally:
            session.close()  

        return response

def setup_middleware(app: FastAPI):
    app.add_middleware(RequestLoggerMiddleware)