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
    hprompt = hprompt.replace("CTX", data.last_resp)
    hprompt = hprompt.replace("RRR", str(request.state.rag.keys()))

    pload = {"prompt": hprompt, "max_new_tokens": MAX_NEW_TOKENS}
    resp = await llm_request(request.state.llm_addr, pload)

    resp = resp.strip(" ").replace("\n", "").replace("\\", "").replace(" ", "")
    gen_json = json.loads(resp[resp.find("{") : resp.rfind("}") + 1])

    intent = gen_json["transit"]
    if not intent in AVAIL_INTENTS:
        raise HTTPException(status_code=500, detail="Generation error")

    country = gen_json.get("country")
    if intent == "c_descr" and (not country or country not in request.state.rag):
        country = "NA"

    if intent == "visiting":
        c_from, c_to = gen_json.get("c_from"), gen_json.get("c_to")
        date_from, date_to = gen_json.get("date_from"), gen_json.get("date_to")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=(
            {"transit": intent}
            | ({"country": country} if intent == "c_descr" else {})
            | (
                {
                    "c_from": c_from,
                    "c_to": c_to,
                    "date_from": date_from,
                    "date_to": date_to,
                }
                if intent == "visiting"
                else {}
            )
        ),
    )


@router.post("/master")
async def response_master(request: Request, data: DFFMasterRequest):
    if data.country == "NA":
        data.country = None

    if not data.country:
        # assuming we always have img and text
        mprompt = S_INFO_PROMPT.replace("UUU", data.request)
        if "<image>" in data.llm_ctx:
            mprompt = mprompt.replace("<image>", "")

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
        mprompt = C_DESCR_PROMPT.replace("UUU", data.request)
        if rag_info[:15] not in data.llm_ctx:
            mprompt = mprompt.replace("RRR", rag_info)
        else:
            mprompt = mprompt.replace("RRR", "")

        if "<image>" in data.llm_ctx:
            mprompt = mprompt.replace("<image>", "")

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
