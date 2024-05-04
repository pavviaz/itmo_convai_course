from dff.script import (
    TRANSITIONS,
    RESPONSE,
    PRE_TRANSITIONS_PROCESSING,
    PRE_RESPONSE_PROCESSING,
)
import dff.script.conditions as cnd
from dff.messengers.telegram import (
    TelegramMessage,
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
                ("chat", "start"): lambda ctx, _: ctx.last_request.text
                in ("/start", "/restart")
            },
        },
        "fallback": {
            RESPONSE: TelegramMessage(text="Please send /restart to begin"),
            TRANSITIONS: {
                ("chat", "start"): lambda ctx, _: ctx.last_request.text
                in ("/start", "/restart")
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
        TelegramMessage(text="/start"),
        script["chat"]["start"][RESPONSE],
    ),
    (
        TelegramMessage("What height of Burj Khalifa?"),
        TelegramMessage("The Burj Khalifa is the tallest building in the world, located in Dubai, United Arab Emirates. It stands at a height of 828 meters (2,717 feet). The building was completed in 2010 and has 163 floors. The Burj Khalifa is a skyscraper, hotel, and office building, and it is part of a larger development called Downtown Dubai. The building is an iconic landmark in the city and is a popular tourist attraction."),
    ),
    (
        TelegramMessage("Can you make a trip there from Moscow from 17.06.2024 to 22.06.2024"),
        TelegramMessage("""\nHere's your links to book hotel:
https://travel.yandex.ru/hotels/search/?&adults=2&childrenAges=0&checkinDate=2024-06-17&checkoutDate=2024-06-22&geoId=11499

And flight:
https://travel.yandex.ru/avia/search/result/?&adults_seats=2&klass=economy&oneway=2&fromId=c213&toId=c11499&when=2024-06-17&return_date=2024-06-22\n"""),
    ),
    (
        TelegramMessage("What food I can taste there?"),
        TelegramMessage('The United Arab Emirates (UAE) offers a diverse range of cuisines, reflecting the country\'s multicultural population. Indian and Pakistani cuisine is the most popular in the UAE, with a wide variety of dishes available in restaurants across the country. Grilled chicken is a popular dish, accompanied by rice, bread, and other accompaniments. Traditional Emirati dishes are rare in restaurants, but Yemeni cuisine is available. Pork is not illegal in the UAE, but it can be hard to find and is generally only available in certain stores and restaurants. The UAE offers a wide range of tourist accommodations, including modern, expensive hotels, more modest housing, and low-cost options that vary in condition. Notable landmarks include the Burj al-Arab in Dubai, known as a "7-star hotel," and the Emirates Palace in Abu Dhabi, which also aspires to high standards at a lower price.'),
    ),
    (
        TelegramMessage("And what currency do they use?"),
        TelegramMessage('The currency used in the United Arab Emirates (UAE) is the United Arab Emirates dirham (AED), also referred to as the dirham (dhs). The conversion rates for the dirham are 3.67 AED for 1 USD, 4.89 AED for 1 EUR, and 5.68 AED for 1 GBP. The dirham is pegged to the USD, so rate variations with this currency are unlikely. The notes used in this currency are in denominations of 5, 10, 20, 50, 100, 200, 500, and 1,000 dirhams. There is also a one dirham coin, with sub-units of 25 and 50 fils coins (100 fils). The UAE offers a wide variety of food from different cuisines, with Indian and Pakistani restaurants being the most popular. Grilled chicken is a popular dish, accompanied by rice, bread, and other accompaniments. Traditional Emirati dishes are rare in restaurants, but Yemeni cuisine is available. Pork is not illegal in the UAE, but it can be hard to find and is generally only available in certain stores and restaurants. The UAE offers a wide range of tourist accommodations, including modern, expensive hotels, more modest housing, and low-cost options that vary in condition. Notable landmarks include the Burj al-Arab in Dubai, known as a "7-star hotel," and the Emirates Palace in Abu Dhabi, which also aspires to high standards at a lower price.'),
    ),
    (
        TelegramMessage("Cool! Thanks!"),
        TelegramMessage("You're welcome! I'm glad I could help. If you have any more questions, feel free to ask."),
    ),
)
