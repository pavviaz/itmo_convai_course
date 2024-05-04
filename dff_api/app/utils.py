import os

import aiohttp
from dff.script import Context, NodeLabel3Type
from dff.pipeline import Pipeline
from dff.messengers.telegram import TelegramMessage
from config import HELPER_EP, MASTER_EP, API_URL, DEFAULT_TEXT, AVAIL_INTENTS


HELPER_URL = f"http://{API_URL}:{os.getenv('NEURAL_API_PORT')}/{HELPER_EP}"
MASTER_URL = f"http://{API_URL}:{os.getenv('NEURAL_API_PORT')}/{MASTER_EP}"
TG_IMAGE_INFO = "https://api.telegram.org/bot{}/getFile?file_id={}"
TG_IMAGE_URL = "https://api.telegram.org/file/bot{}/{}"


async def get_tg_img_url(file_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            TG_IMAGE_INFO.format(os.getenv("TG_BOT_TOKEN"), file_id)
        ) as response:
            if response.status == 200:
                resp = await response.json()
            else:
                raise Exception("tg error")

    return TG_IMAGE_URL.format(os.getenv("TG_BOT_TOKEN"), resp["file_path"])


async def helper(req: str, img: str = None):
    pload = {"request": req, "img": img}
    async with aiohttp.ClientSession() as session:
        async with session.post(HELPER_URL, json=pload) as response:
            if response.status == 200:
                resp = await response.json()
            else:
                raise Exception("api error")

    return resp


async def master(llm_ctx: str, req: str, img: str = None, country: str = None):
    pload = {"llm_ctx": llm_ctx, "request": req, "img": img, "country": country}
    async with aiohttp.ClientSession() as session:
        async with session.post(MASTER_URL, json=pload) as response:
            if response.status == 200:
                resp = await response.json()
            else:
                raise Exception("api error")

    return resp


def extract_intent():
    async def extract_intent_inner(ctx: Context, _: Pipeline) -> Context:
        message = ctx.last_request
        text = ""
        if message is None:
            return text, None
        update = getattr(message, "update", None)
        if message.text is not None:
            text = message.text
        elif message.update.caption is not None:
            text = message.update.caption

        if not text:
            text = DEFAULT_TEXT
        ctx.misc["current_req"] = text

        if update.photo:
            photo = update.document or update.photo[-1]

            ctx.misc["img_url"] = await get_tg_img_url(photo.file_id)
            ctx.misc["llm_ctx"] = " "

        h_answ = await helper(ctx.misc["current_req"], ctx.misc["img_url"])

        ctx.misc["transit"] = h_answ["transit"]
        if h_answ.get("country"):
            ctx.misc["country"] = h_answ["country"]
        else:
            ctx.misc["country"] = None

        return ctx

    return extract_intent_inner


def generate_response():
    async def gen_inner(ctx: Context, _: Pipeline) -> Context:
        m_answ = await master(
            ctx.misc["llm_ctx"],
            ctx.misc["current_req"],
            ctx.misc["img_url"],
            ctx.misc["country"],
        )

        ctx.misc["llm_ctx"] = m_answ["llm_ctx"]
        ctx.misc["resp"] = m_answ["response"]

        return ctx

    return gen_inner


def get_node_by_request_type(ctx: Context, _: Pipeline) -> NodeLabel3Type:
    if ctx.misc["transit"] in AVAIL_INTENTS:
        res = ("chat", ctx.misc["transit"], 1.0)
    else:
        res = ("root", "fallback", 1.0)

    return res


def get_response(ctx: Context, _: Pipeline) -> NodeLabel3Type:
    return TelegramMessage(text=ctx.misc["resp"])
