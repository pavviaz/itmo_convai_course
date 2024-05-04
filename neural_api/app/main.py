import logging
from contextlib import asynccontextmanager
import os
from csv import DictReader

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import app.healthchecker as hc
from app.router import router
from app.config import WORKER_URL, LLM_EP, RAG_PATH


@asynccontextmanager
async def init_func(app: FastAPI):
    # Wait for LLAVA to start
    app.state.llm_addr = f"http://{WORKER_URL}:{os.getenv('WORKER_PORT')}/{LLM_EP}"
    hc.Readiness(urls=[app.state.llm_addr]).run()

    # Load RAG
    app.state.rag = dict()
    with open(RAG_PATH) as f:
        r = DictReader(f)
        for el in r:
            app.state.rag[el["country"]] = el["info"] 
    
    yield


app = FastAPI(
    title="ITMO_CONVAI",
    description="Main Script for ITMO Conversational AI",
    version="0.0.1",
    docs_url="/docs",
    redoc_url=None,
    lifespan=init_func,
)

app.state.Logger = logging.getLogger(name="neural_api")
app.state.Logger.setLevel("DEBUG")

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
    request.state.logger = app.state.Logger
    request.state.llm_addr = app.state.llm_addr
    request.state.rag = app.state.rag
    try:
        response = await call_next(request)
    except Exception as exc:
        detail = getattr(exc, "detail", None)
        unexpected_error = not detail
        if unexpected_error:
            args = getattr(exc, "args", None)
            detail = args[0] if args else str(exc)
        print(detail, flush=True)
        status_code = getattr(exc, "status_code", 500)
        response = JSONResponse(
            content={"detail": str(detail), "success": False}, status_code=status_code
        )

    return response


if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=7875,
    )
