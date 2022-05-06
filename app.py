import cv2
from PIL import Image
from io import BytesIO
from flask import Flask, Response, send_file, redirect
from CameraService import CameraService
from bh1750 import readIlluminance
from threading import Timer
import time
from motion import moving
import os
from fireBase import getMain
from fireBase import getMoving
from fireBase import getDistance
from fireBase import getIllum
from fireBase import fileUpload
from fireBase import sendMessage
from io import BytesIO
from blue import alert, mixer


### HTML문서 가져오기
PAGE= open('/home/cnergy/main/flug/templates/index.html').read()

global cnt
cnt = 0

save_path = 'record'

app = Flask(__name__)
cap = CameraService(0)
cap.start()

### 움직임 감지 시 푸시알림 전송
global motion_updater
motion_updater = None
def update_motion():
    global motion_updater
    motion = moving()
    print('motion: ', motion)
    if motion == 0:
        sendMessage('앱을 열어 확인해보세요.', '움직임이 감지되었습니다.')

global moving_updater
moving_updater = None
def update_moving():
    global moving_updater
    moving = alert()
    print(moving)
    if moving == 0:
        sendMessage('앱을 열어 확인해보세요.', '가방이 멀어졌습니다.')

### 조도값이 1 이상이면 푸시알림을 전송하고 사진을 찍어 파이어베이스에 업로드
global illuminance_updater
illuminance_updater = None
def update_illuminance():
    global illuminance_updater
    illumi = readIlluminance()
    print('illumi: ', illumi)
    global cnt
    try:
        if illumi > 1:
            frame = cap.read()
            if frame is not None:
                while True:
                    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    jpg = Image.fromarray(imgRGB)
                    filename = f'./image/1.jpg'
                    f = open(filename, 'wb')
                    jpg.save(f, 'JPEG')
                    # cnt += 1
                    fileUpload(filename) 
                    sendMessage('앱을 열어 확인해보세요.', '누군가가 가방을 열었습니다.')
                    break                 
    except Exception as e:
        print(e)

@app.route("/")
def hello_world():
    return PAGE

### 카메라

### 실시간 스트리밍
def cameraRead(camera):
    while True:
        frame = camera.read()
        if frame is not None:
            imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            jpg = Image.fromarray(imgRGB)
            content = BytesIO()
            jpg.save(content, 'JPEG')
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + content.getvalue() + b'\r\n')
            #cv2.putText(frame, text=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), org=(10, 460), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale=1, color=(255,255,255), thickness=2)

### HTML 파일에 영상정보 응답
@app.route('/stream.mjpg')
def stream():
    response = Response(cameraRead(cap),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    return response

### 영상 저장
@app.route('/record')
def record():
    name = time.strftime('%Y-%m-%d %H시 %M분 %S초',time.localtime(time.time()))
    cap.record(f'{name}.mp4')
    return ('', 204)

### 영상 저장 완료
@app.route('/save')
def save():
    cap.save()
    return ('', 204)

def get_last_filename(): 
    return ''

### 저장한 영상 다운로드
@app.route('/download')
def download():
    file_list = os.listdir(save_path)
    file_list.sort()
    filename =  file_list[-1]
    return send_file(f'{save_path}/{filename}', as_attachment=True)

### 실시간 스트리밍 중 캡쳐
@app.route('/snapshot')
def snapshot():
    frame = cap.read()
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    jpg = Image.fromarray(imgRGB)
    content = BytesIO()
    jpg.save(content, 'JPEG')
    return Response(content.getvalue(), mimetype='image/jpeg')

### 파이어베이스와 연동된 설정값을 불러오면서 위에서 선언된 함수 제어
def loop():
    global motion_updater
    global illuminance_updater
    global moving_updater
    if getMain() == 0:
        print('꺼짐')
    elif getMain() == 1:
        print('켜짐')
        time.sleep(1)
        if getMoving() == 0:
            if motion_updater is not None:                
                motion_updater.cancel()
            print("움직임감지 꺼짐")
            time.sleep(1)
        elif getMoving() == 1:
            motion_updater = Timer(5, update_motion)
            motion_updater.start()
            print("움직임감지 켜짐")
            time.sleep(1)
        if getDistance() == 0:
            if moving_updater is not None:
                moving_updater.cancel()
                mixer.music.stop()
            print("거리감지 꺼짐")
            time.sleep(1)
        elif getDistance() == 1:
            moving_updater = Timer(5, update_moving)
            moving_updater.start()
            print("거리감지 켜짐")
            time.sleep(1)
        if getIllum() == 0:
            if illuminance_updater is not None: 
                illuminance_updater.cancel()
            print("조도센서 꺼짐")
            time.sleep(1)
        elif getIllum() == 1:
            illuminance_updater = Timer(5, update_illuminance)
            illuminance_updater.start()    
            print("조도센서 켜짐")
            time.sleep(1)
    Timer(1, loop).start()

Timer(5, loop).start()

if __name__ == '__main__':
    app.run(threaded=True)