import requests as rq


from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")

f = open('test.txt', "a")
f.write(current_time+"\r")