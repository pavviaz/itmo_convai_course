HEALTHCHECK_TIMEOUT = 30
HEALTHCHECK_SLEEP = 5

AVAIL_INTENTS = ["s_info", "c_descr", "visiting", "start"]

API_URL = "neural_api"
# API_URL = "localhost"
HELPER_EP = "helper"
MASTER_EP = "master"

GEOID_URL = "https://suggest-maps.yandex.ru/suggest-geo"
GEOID_PARAMS = {
    "search_type": "tune",
    "v": "9",
    "results": 1,
    "lang": "ry_RU",
    "callback": "json",
}

HBOOKING_URL = "https://travel.yandex.ru/hotels/search/?"
HBOOKING_PARAMS = {"adults": "2", "childrenAges": "0"}

FBOOKING_URL = "https://travel.yandex.ru/avia/search/result/?"
FBOOKING_PARAMS = {"adults_seats": "2", "klass": "economy", "oneway": "2"}

DEFAULT_TEXT = "Describe the image given"

USER_GREETING = """
Greetings, traveler! I am TravelTime bot ✈️
I am the only one, who know's everything about all the countries you can think about
Moreover, I even know sightseens all over the world! Just send me a photo and ask whatever you want about it
"""

TRIP_SORRY = """
Sorry, I can't recognize departure, arrival cities or from-to dates in your request :(
Please, try to reformulate.
"""

TRIP_OK = """
Here's your links to book hotel:
HHH

And flight:
FFF
"""
