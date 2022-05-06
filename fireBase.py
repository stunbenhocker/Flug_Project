import firebase_admin
from firebase_admin import credentials, db, storage
from uuid import uuid4
import os
from pyfcm import FCMNotification

### 파이어베이스 정보

PROJECT_ID = "flug-543ad"
cred = credentials.Certificate('/home/cnergy/main/flug/flug-543ad-firebase-adminsdk-i7hyj-1c88429022.json')
firebase_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://flug-543ad-default-rtdb.firebaseio.com/',
    'storageBucket':f"{PROJECT_ID}.appspot.com"
})
bucket = storage.bucket()

### 이미지 업로드 함수

def fileUpload(file):
    blob = bucket.blob('image_store/'+ os.path.basename(file))
    new_token = uuid4()
    metadata = {"firebaseStorageDownloadTokens": new_token}
    blob.metadata = metadata
    blob.upload_from_filename(filename=file, content_type='image/jpg')         

### 설정값 가져오기

def getMain():
    dbRef = db.reference('status')
    return dbRef.get()
def getIllum():
    Illum = db.reference('switchCheck1')
    return Illum.get()
def getDistance():
    dist = db.reference('switchCheck2')
    return dist.get()
def getMoving():
    move = db.reference('switchCheck3')
    return move.get()

### 푸시알림

APIKEY = "AAAAMQiY0g4:APA91bFRfeCVYqoNrMFPliE4ZHyBgFQVIQ7AavSGI-zLTXkxwvE612rWmV5ZXAHDMHJVkC-2Hhhql39IAi5Onx27rcnXjqsyCx3OALl6bh60qxSsq5n948Ce6kwlhpbjGDouBFmkOjnX"
TOKEN = "fY7P9A47TSmepTt5Uv39t6:APA91bHTJlJlrC8AD80FqH3KrhQxnqp-raUl9J_0oFCz91yN2-iA7WfkzwqO1_8WVNNtC9R6cRQaUyt9BCvVKTtzLQbnuguCkr1X6uhuBkX5DtT9p0Djf6UBu2VtoGrh1SevNgAM6RQi"

# 파이어베이스 콘솔에서 얻어 온 서버 키를 넣어 줌
push_service = FCMNotification(APIKEY)

def sendMessage(body, title):
    # 메시지 (data 타입)
    data_message = {
        "body": body,
        "title": title
    }
    # 토큰값을 이용해 푸시알림을 전송함
    result = push_service.notify_single_device(registration_id=TOKEN, message_title=title, 
    message_body=body, data_message=data_message)
    # 전송 결과 출력
    print(result)