import requests as rq


from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")

f = open('testing.txt', "a")
f.write(current_time+"\r")


#test1