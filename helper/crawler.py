import requests as rq
from bs4 import BeautifulSoup
import json
import traceback
import telegram
import sys

TELEGRAM_TOKEN = sys.argv[1]
AUDIENCES = sys.argv[2]
AUDIENCES = AUDIENCES.split(',')

r = rq.get('https://www.binance.com/zh-TC/support/announcement/%E6%95%B8%E5%AD%97%E8%B2%A8%E5%B9%A3%E5%8F%8A%E4%BA%A4%E6%98%93%E5%B0%8D%E4%B8%8A%E6%96%B0?c=48')

soup = BeautifulSoup(r.text, "html.parser")
res = soup.find(id="__APP_DATA")
json_object = json.loads(res.contents[0])
news = json_object['appState']['loader']['dataByRouteId']['2a3f']['catalogs'][0]['articles'][0]['title']

with open('helper/announcement.txt', 'r') as f:
    old = f.read()

if(old != news):
    with open('helper/announcement.txt', 'w') as f:
        f.write(news)
    bot = telegram.Bot(TELEGRAM_TOKEN)
    for i in AUDIENCES:
        text = '*- - - - - - - -幣安上幣- - - - - - - -*\n' + news
        text = text.replace('!', '\!')
        text = text.replace('.', '\.')
        text = text.replace('-', '\-')
        bot.sendMessage(text=text, chat_id=i, parse_mode="MARKDOWNV2")

