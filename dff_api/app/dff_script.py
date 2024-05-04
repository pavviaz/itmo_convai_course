from dff.script import (
    TRANSITIONS,
    RESPONSE,
    PRE_TRANSITIONS_PROCESSING,
    PRE_RESPONSE_PROCESSING,
)
import dff.script.conditions as cnd
from dff.messengers.telegram import (
    TelegramMessage,
    telegram_condition,
)

from utils import (
    extract_intent,
    get_node_by_request_type,
    generate_response,
    get_response,
)
from config import USER_GREETING


script = {
    "root": {
        "start": {
            TRANSITIONS: {
                ("chat", "start"): telegram_condition(commands=["start", "restart"])
            },
        },
        "fallback": {
            RESPONSE: TelegramMessage(text="Please send /restart to begin"),
            TRANSITIONS: {
                ("chat", "start"): telegram_condition(commands=["start", "restart"])
            },
        },
    },
    "chat": {
        "start": {
            RESPONSE: TelegramMessage(text=USER_GREETING),
            PRE_TRANSITIONS_PROCESSING: {"1": extract_intent()},
            TRANSITIONS: {get_node_by_request_type: cnd.true()},
        },
        "s_info": {
            PRE_RESPONSE_PROCESSING: {"1": generate_response()},
            RESPONSE: get_response,
            PRE_TRANSITIONS_PROCESSING: {"1": extract_intent()},
            TRANSITIONS: {get_node_by_request_type: cnd.true()},
        },
        "c_descr": {
            PRE_RESPONSE_PROCESSING: {"1": generate_response()},
            RESPONSE: get_response,
            PRE_TRANSITIONS_PROCESSING: {"1": extract_intent()},
            TRANSITIONS: {get_node_by_request_type: cnd.true()},
        },
        # "ticket_ord": {
        #     PRE_RESPONSE_PROCESSING: {"1": generate_response()},
        #     RESPONSE: get_response,
        #     PRE_TRANSITIONS_PROCESSING: {"1": extract_intent()},
        #     TRANSITIONS: {get_node_by_request_type: cnd.true()},
        # }
    },
}

start_label = ("root", "start")
fallback_label = ("root", "fallback")
