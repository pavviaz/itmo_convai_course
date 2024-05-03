import requests
import json
import datetime

def get_geoid(city: str) -> str:
    url_base = 'https://suggest-maps.yandex.ru/suggest-geo'
    params = {'search_type': 'tune', 'v': '9', 'results': 1, 'lang': 'ry_RU', 'callback': 'json'}
    params['part'] = city
    r = requests.get(url_base, params=params)
    if r.ok:
        r_text = r.text
        r_json = r_text[5: len(r_text)-1]
        res_json = json.loads(r_json)
        res = res_json['results'][0]['geoid']
    else:
        res = ''
    return str(res)

def get_url_booking_hotels(date_in: datetime.datetime, date_out: datetime.datetime, geoid: str) -> str:
    if date_in is None:
        date_in = datetime.datetime.now()
    if date_out is None:
        date_out = datetime.datetime.now() + datetime.timedelta(days=1)
    url = 'https://travel.yandex.ru/hotels/search/?' #adults=2&checkinDate=2024-05-20&checkoutDate=2024-05-26&childrenAges=&geoId=239&lastSearchTimeMarker=1714726809704&oneNightChecked=false'
    params = {'adults': '2', 'checkinDate': date_in.strftime('%Y-%m-%d'), 'checkoutDate': date_out.strftime('%Y-%m-%d'), 'childrenAges': '0', 'geoId': geoid}
    for item in params:
        url += '&' + item + '=' + params[item]
    return url


def get_url_booking_tikets(fromid: str, toid: str, date_in: datetime.datetime, date_out: datetime.datetime) -> str:
    if date_in is None:
        date_in = datetime.datetime.now()
    if date_out is None:
        date_out = datetime.datetime.now() + datetime.timedelta(days=1)
    url = 'https://travel.yandex.ru/avia/search/result/?' #adults=2&checkinDate=2024-05-20&checkoutDate=2024-05-26&childrenAges=&geoId=239&lastSearchTimeMarker=1714726809704&oneNightChecked=false'
    params = {'adults_seats': '2', 'fromId': 'c' + fromid, 'klass': 'economy', 'oneway': '2', 'return_date': date_out.strftime('%Y-%m-%d'), 'toId': 'c' + toid, 'when': date_in.strftime('%Y-%m-%d')}
    for item in params:
        url += '&' + item + '=' + params[item]
    return url