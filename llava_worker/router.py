from io import BytesIO

from PIL import Image
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import status
import httpx

from contracts import WorkerRequest
from llm_worker import Worker


router = APIRouter(tags=["worker"])
worker = Worker()


@router.post("/worker")
async def responce(data: WorkerRequest):
    if data.img:
        async with httpx.AsyncClient() as client:
            response = await client.get(data.img)
            if response.status_code == 200:
                buf = BytesIO(response.read())
                data.img = Image.open(buf)
            else:
                data.img = None

    return JSONResponse(
        status_code=status.HTTP_200_OK, content=worker.answer(data)
    )
