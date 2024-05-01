import os
from io import BytesIO

import aiohttp
from PIL import Image

import app.config as cfg
from app.conversation import default_conversation, SeparatorStyle
# import config as cfg
# from conversation import default_conversation, SeparatorStyle


CREFR_URL = (
    f"http://{cfg.WORKER_URL}:{os.getenv('CONTROLLER_PORT')}/{cfg.CONTROLLER_REFRESH}"
)
CWLIST_URL = (
    f"http://{cfg.WORKER_URL}:{os.getenv('CONTROLLER_PORT')}/{cfg.CONTROLLER_WLIST}"
)


async def get_model_list():
    async with aiohttp.ClientSession() as session:
        async with session.post(CREFR_URL) as response:
            if response.status != 200:
                return
                # raise HTTPException(status_code=500, detail="LLAVA refresh error")

        async with session.post(CWLIST_URL) as response:
            if response.status != 200:
                return
                # raise HTTPException(status_code=500, detail="LLAVA models error")

            models = (await response.json())["models"]
            if not models:
                return
                # raise HTTPException(status_code=500, detail="No models available")

    return models


async def download_image_pil(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                buf = BytesIO(await response.read())
                return Image.open(buf)

            return


def get_pload(text, img=None):
    text = text[: cfg.TOKEN_CUTOFF]  # Hard cut-off for images
    if img is not None:
        text = text[:cfg.TOKEN_CUTOFF - 336]  # Hard cut-off for images
        if '<image>' not in text:
            text = text + '\n<image>'
        text = (text, img, "Default")
        state = default_conversation.copy()

    state.append_message(state.roles[0], text)
    state.append_message(state.roles[1], None)

    prompt = state.get_prompt()
    imgs = state.get_images()

    pload = {
        "prompt": prompt,
        "temperature": cfg.TEMPERATURE,
        "top_p": cfg.TOP_P,
        "max_new_tokens": cfg.MAX_NEW_TOKENS,
        "stop": (
            state.sep
            if state.sep_style in [SeparatorStyle.SINGLE, SeparatorStyle.MPT]
            else state.sep2
        ),
        "images": imgs,
    }

    return pload


def func_1(text, img=None):
    resp = {"transit": "s_info" | "c_descr" | "ticket_ord", "country": str}

    return resp


def func_2(text, img=None, **kwargs):
    kwargs["country"]

    resp = "hello"

    return resp