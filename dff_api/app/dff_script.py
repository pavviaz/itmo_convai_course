from dff.script import (
    TRANSITIONS,
    RESPONSE,
    Message,
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
        "visiting": {
            PRE_RESPONSE_PROCESSING: {"1": generate_response()},
            RESPONSE: get_response,
            PRE_TRANSITIONS_PROCESSING: {"1": extract_intent()},
            TRANSITIONS: {get_node_by_request_type: cnd.true()},
        }
    },
}

start_label = ("root", "start")
fallback_label = ("root", "fallback")


happy_path = (
    (
        Message("What do you think about UAE?"),
        Message("""The United Arab Emirates (UAE) is a diverse and modern country that offers a familiar environment for Western tourists. The country is known for its modern malls filled with Western products, but also has remote desert dunes and craggy wadis that are less well-known. Alcohol is widely available in Dubai and tourist hotels, but not in Sharjah. The roads and public facilities are modern but can be crowded. Supermarkets offer a variety of products from Europe and the US, along with local and regional items. Major international chains operate widely, but there are still traditional souks filled with products from around the world.

The UAE has a diverse population and is home to people from different cultures and religions. The country is known for its tolerance and respect for different beliefs and practices. The UAE is also a hub for business and trade, and is home to many international companies and organizations.

The UAE is a popular tourist destination, with a wide variety of tourist attractions, including beaches, desert safaris, ski slopes, and traditional souks. The country is also known for its modern and luxurious hotels, such as the Burj al-Arab in Dubai and the Emirates Palace in Abu Dhabi.

The UAE is a popular destination for people from all over the world, and it is easy for tourists to obtain a visa to enter the country. Citizens of GCC nations do not require a visa and may stay, work, and travel in the UAE indefinitely. Citizens of the European Union (except Ireland), Andorra, Iceland, Liechtenstein, Monaco, Norway, San Marino, Seychelles, Switzerland, and Vatican City do not require a visa for stays of up to 90 days within a 180 day period. Citizens of Australia, Brunei, Canada, China, Hong Kong, Ireland, Japan, Macau, Malaysia, New Zealand, Singapore, South Korea, United Kingdom, and the United States, as well as persons holding British National (Overseas) passports, may obtain a free visa on arrival valid for 30 days, with the possibility of extension for a fee. Citizens of India holding a valid US visa or Green Card do not require an advance visa for visit purposes and can get a visa on arrival, valid for 14 days, from any port of entry. Citizens of any country except Afghanistan, Iraq, Nigeria, Somalia, and Yemen may enter the UAE for up to 96 hours (4 days) after obtaining a transit visa at the airport, provided they continue to a third destination and have a hotel booking. Several other countries are eligible for free hotel/tour-sponsored tourism visas. All other nationalities will be required to apply for a visa in advance, which will require a sponsor from inside the UAE. Israeli passport holders previously needed to make advance arrangements for an entry permit, but following an Israel-UAE peace agreement in August 2020, Israeli and Emirati citizens can now go to each other's countries visa-free. However, some discrimination and distrust may still exist due to cultural, religious, and political differences. Travelers from India may need to obtain a stamp of 'OK to Board' before traveling to the UAE.
"""),
    ),
)
    