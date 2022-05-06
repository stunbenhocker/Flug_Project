import sys
import requests, json
import time
from threading import Timer
from pygame import mixer

mixer.init()
mixer.music.load('flug.mp3')

def alert(): 
    try:
        url = "http://172.30.1.50:8057/MapTest/BlueToothController"
        r = requests.get(url)
        print(str(r.text))
        if r.text == '"2"':
            mixer.music.play()
            return 0
        if r.text == '"1"':
            mixer.music.stop()
            return 1
        time.sleep(1)
    except:
        print("Invalid URL or some error occured while making the GET request to the specified URL")