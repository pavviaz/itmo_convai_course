import json

from fastapi.responses import JSONResponse
from fastapi import APIRouter, status, Request, HTTPException
import aiohttp

from app.contracts import DFFHelperRequest, DFFMasterRequest
from app.config import (
    HELPER_PROMPT,
    C_DESCR_PROMPT,
    C_DESCR_NO_RAG,
    S_INFO_PROMPT,
    MAX_NEW_TOKENS,
    AVAIL_INTENTS,
)
from app.utils import llm_request


router = APIRouter(tags=["neural_api"])


@router.post("/helper")
async def response_helper(request: Request, data: DFFHelperRequest):
    hprompt = HELPER_PROMPT.replace("UUU", data.request).strip("\n ")
    if not data.img:
        hprompt = hprompt.replace("<image> ", "")

    hprompt = hprompt.replace("RRR", str(request.state.rag.keys()))

    pload = {"prompt": hprompt, "img": data.img, "max_new_tokens": MAX_NEW_TOKENS}
    resp = await llm_request(request.state.llm_addr, pload)

    resp = resp.strip(" ").replace("\n", "").replace("\\", "").replace(" ", "")
    gen_json = json.loads(resp[resp.find("{") : resp.rfind("}") + 1])

    intent = gen_json["transit"]
    if not intent in AVAIL_INTENTS:
        raise HTTPException(status_code=500, detail="Generation error")

    country = gen_json.get("country")
    if intent == "c_descr" and (not country or country not in request.state.rag):
        country = "NA"

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=(
            {"transit": intent} | ({"country": country} if intent == "c_descr" else {})
        ),
    )


@router.post("/master")
async def response_master(request: Request, data: DFFMasterRequest):
    # s_info
    if not data.country:
        # assuming we always have img and text
        mprompt = S_INFO_PROMPT.replace("UUU", data.request)
        data.llm_ctx += f" {mprompt}"
        data.llm_ctx = data.llm_ctx.strip()

        pload = {
            "prompt": data.llm_ctx,
            "img": data.img,
            "max_new_tokens": MAX_NEW_TOKENS,
        }
        resp = await llm_request(request.state.llm_addr, pload)
        resp = resp.strip()

    else:
        rag_info = request.state.rag.get(data.country, "")
        mprompt = C_DESCR_PROMPT.replace("UUU", data.request).replace("RRR", rag_info)

        data.llm_ctx += f" {mprompt}"
        data.llm_ctx = data.llm_ctx.strip()

        pload = {
            "prompt": data.llm_ctx,
            "img": data.img,
            "max_new_tokens": MAX_NEW_TOKENS,
        }
        resp = await llm_request(request.state.llm_addr, pload)
        resp = resp.strip()

        if not rag_info:
            resp = C_DESCR_NO_RAG + resp

    data.llm_ctx += f" {resp}"

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"llm_ctx": data.llm_ctx, "response": resp},
    )
