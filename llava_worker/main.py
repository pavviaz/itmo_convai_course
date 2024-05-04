import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from router import router


app = FastAPI(
    title="CONVAI_LLM",
    description="LLM worker",
    version="0.0.1",
    docs_url="/docs",
    redoc_url=None
)

app.include_router(router)


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    """
    Middleware function that manages the database
    session for each incoming request and closes
    the session after the response is sent.

    Args:
        request (Request): The incoming request object.

        call_next (function): The function to call
        the next middleware or the main application handler.

    Returns:
        Response: The response object returned by the
        next middleware or the main application handler.
    """
    try:
        response = await call_next(request)
    except Exception as exc:
        detail = getattr(exc, "detail", None)
        unexpected_error = not detail
        if unexpected_error:
            args = getattr(exc, "args", None)
            detail = args[0] if args else str(exc)
        status_code = getattr(exc, "status_code", 500)
        response = JSONResponse(
            content={"detail": str(detail), "success": False}, status_code=status_code
        )

    return response


if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=7870,
    )
