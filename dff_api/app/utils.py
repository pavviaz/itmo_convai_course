import os
import json

import aiohttp
from dff.script import Context, NodeLabel3Type
from dff.pipeline import Pipeline
from dff.messengers.telegram import TelegramMessage

from config import (
    HELPER_EP,
    MASTER_EP,
    API_URL,
    DEFAULT_TEXT,
    AVAIL_INTENTS,
    TRIP_SORRY,
    TRIP_OK,
    GEOID_URL,
    GEOID_PARAMS,
    HBOOKING_URL,
    HBOOKING_PARAMS,
    FBOOKING_URL,
    FBOOKING_PARAMS,
)


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

    return TG_IMAGE_URL.format(os.getenv("TG_BOT_TOKEN"), resp["result"]["file_path"])


async def helper(req: str, last_resp: str = None):
    pload = {"request": req, "last_resp": last_resp if last_resp else " "}
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


async def get_geoid(city: str) -> str:
    pload = GEOID_PARAMS.copy()
    pload["part"] = city

    async with aiohttp.ClientSession() as session:
        async with session.get(GEOID_URL, params=pload) as response:
            if response.status == 200:
                resp = await response.text()
            else:
                raise Exception("api error")

    try:
        r_json = resp[5 : len(resp) - 1]
        res_json = json.loads(r_json)
        res = str(res_json["results"][0]["geoid"])
    except:
        res = ""

    return res


def get_url_booking_hotels(date_in, date_out, geoid):
    url = HBOOKING_URL

    pload = HBOOKING_PARAMS.copy()
    pload["checkinDate"] = date_in
    pload["checkoutDate"] = date_out
    pload["geoId"] = geoid

    for item in pload:
        url += "&" + item + "=" + pload[item]
    return url


def get_url_booking_tickets(fromid, toid, date_in, date_out):
    url = FBOOKING_URL

    pload = FBOOKING_PARAMS.copy()
    pload["fromId"] = "c" + fromid
    pload["toId"] = "c" + toid
    pload["when"] = date_in
    pload["return_date"] = date_out

    for item in pload:
        url += "&" + item + "=" + pload[item]
    return url


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

        if text in ["/start", "/restart"]:
            ctx.misc["transit"] = "start"
            ctx.misc["img_url"] = None
            ctx.misc["llm_ctx"] = " "
            ctx.misc["resp"] = None
            ctx.misc["trip"] = None
            return ctx

        ctx.misc["current_req"] = text
        if update.photo:
            photo = update.document or update.photo[-1]

            ctx.misc["img_url"] = await get_tg_img_url(photo.file_id)
            ctx.misc["llm_ctx"] = " "
            ctx.misc["resp"] = None

        ctx.misc["resp"] = ctx.misc["resp"] if ctx.misc.get("resp") else None
        h_answ = await helper(ctx.misc["current_req"], ctx.misc["resp"])
        ctx.misc["transit"] = h_answ["transit"]
        print(f"HELPER: {h_answ}", flush=True)

        if ctx.misc["transit"] == "visiting":
            c_from, c_to = h_answ.get("c_from"), h_answ.get("c_to")
            date_from, date_to = h_answ.get("date_from"), h_answ.get("date_to")

            if any(not el for el in [c_from, c_to, date_from, date_to]):
                ctx.misc["trip"] = TRIP_SORRY
            else:
                from_geoid, to_geoid = await get_geoid(c_from), await get_geoid(c_to)
                h_url = get_url_booking_hotels(date_from, date_to, to_geoid)
                f_url = get_url_booking_tickets(
                    from_geoid, to_geoid, date_from, date_to
                )

                ctx.misc["trip"] = TRIP_OK.replace("HHH", h_url).replace("FFF", f_url)
                return ctx

        if h_answ.get("country"):
            ctx.misc["country"] = h_answ["country"]
        else:
            ctx.misc["country"] = None

        return ctx

    return extract_intent_inner


def generate_response():
    async def gen_inner(ctx: Context, _: Pipeline) -> Context:
        if ctx.misc.get("trip"):
            ctx.misc["resp"] = ctx.misc["trip"]
            ctx.misc["trip"] = None
            return ctx

        if not ctx.misc.get("llm_ctx"):
            ctx.misc["llm_ctx"] = " "
        if not ctx.misc.get("img_url"):
            ctx.misc["img_url"] = None
        if not ctx.misc.get("country"):
            ctx.misc["country"] = None
            
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
