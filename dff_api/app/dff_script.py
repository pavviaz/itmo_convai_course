from dff.script import conditions as cnd
from dff.script import labels as lbl
from dff.script import RESPONSE, TRANSITIONS, MISC
from dff.script.core.message import Button
from dff.messengers.telegram import (
    TelegramUI,
    TelegramMessage,
    RemoveKeyboard,
)

from app.config import USER_GREETING


script = {
    "root": {
        "start": {
            TRANSITIONS: {
                ("general", "native_keyboard"): (
                    lambda ctx, _: ctx.last_request.text in ("/start", "/restart")
                ),
            },
        },
        "fallback": {
            RESPONSE: TelegramMessage(
                text="Please, send `/start` or `/restart` to begin"
            ),
            TRANSITIONS: {
                ("general", "native_keyboard"): (
                    lambda ctx, _: ctx.last_request.text in ("/start", "/restart")
                ),
            },
        },
    },
    "general": {
        "native_keyboard": {
            RESPONSE: TelegramMessage(
                text=USER_GREETING,
                ui=TelegramUI(
                    buttons=[
                        Button(text="5"),
                        Button(text="4"),
                    ],
                    is_inline=False,
                    row_width=4,
                ),
            ),
            TRANSITIONS: {
                ("general", "s_info"): func_1(text, img) == "s_info",
                ("general", "c_descr"): func_1(text, img) == "c_descr",
                ("general", "ticket_ord"): func_1(text, img) == "ticket_ord",
                ("general", "fail"): cnd.true(),
            },
        },
        "s_info": {
            RESPONSE: TelegramMessage(**{"text": func_2(text, img), "ui": RemoveKeyboard()}),
            TRANSITIONS: {
                ("general", "s_info"): cnd.exact_match(TelegramMessage(text="4")),
                ("general", "c_descr"): cnd.true(),
                ("general", "ticket_ord"): cnd.true(),
            },
        },
        "c_descr": {
            RESPONSE: TelegramMessage(**{"text": func_3(text, img, country=...), "ui": RemoveKeyboard()}),
            TRANSITIONS: {
                ("general", "s_info"): cnd.exact_match(TelegramMessage(text="4")),
                ("general", "c_descr"): cnd.true(),
                ("general", "ticket_ord"): cnd.true(),
            },
        },
        "ticket_ord": {
            RESPONSE: TelegramMessage(**{"text": func_4(text, img, currency=...), "ui": RemoveKeyboard()}),
            TRANSITIONS: {
                ("general", "s_info"): cnd.exact_match(TelegramMessage(text="4")),
                ("general", "c_descr"): cnd.true(),
                ("general", "ticket_ord"): cnd.true(),
            },
        },
        "fail": {
            RESPONSE: TelegramMessage(
                **{
                    "text": "Incorrect answer, type anything to try again",
                    "ui": RemoveKeyboard(),
                }
            ),
            TRANSITIONS: {("general", "native_keyboard"): cnd.true()},
        },
    },
}

start_label=("root", "start")
fallback_label=("root", "fallback")
