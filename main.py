import math
import random
from datetime import date, datetime

import os
import requests
from dateutil import tz
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage


def get_today():
    tzinfo = tz.gettz('Asina/Shanghai')
    day = datetime.now()
    day.replace(tzinfo=tzinfo)
    return day


today = get_today()

start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
    url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
    res = requests.get(url).json()
    weather = res['data']['list'][0]
    return weather['weather'], math.floor(weather['temp'])


def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days


def get_birthday():
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days


def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


def get_dna():
    weekday = today.date().weekday()
    if weekday == 5:
        return "2"
    if weekday == 6:
        return "1"
    if weekday % 2 == 0:
        return "今日需要核酸 0"
    return weekday % 2


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature = get_weather()
data = {
    "weather": {"value": wea},
    "temperature": {"value": temperature},
    "know": {"value": get_count()},
    "birthday_left": {"value": get_birthday()},
    "dna": {"value": get_dna()},
    "word": {"value": get_words(), "color": get_random_color()}
}
print(data)

for i in user_id.split(","):
    res = wm.send_template(i, template_id, data)
    print(res)
