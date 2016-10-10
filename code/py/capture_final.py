# -*- coding: utf-8 -*-
# purpose: 出入り口に設置したカメラにより出入りする者の年齢別の人口と性別を調べる。
# description: シリアルでArduinoからセンサーの値を受信しつつ、
#              その値をトリガーとしてWebカメラから静止画を取得し、
#              静止画をMicrosoftのComputer Vision APIに送信して性別と年齢の推定値を取得し、
#              別に立てたサーバーに性別と年齢の情報を送信する。
#              ちなみに、送られたデータは性別ごとに統計が取られ、グラフ化されWebに公開される予定。
#              なお、画像をキャプチャするためのトリガーを画像から判断する場合はシリアル通信関係を利用しなくてOKです。
# author: Katsuhiro Morishita
# created: 2016-10-09
# lisence: MIT
# other: Mac Python 3.4.2 + OpenCV、Windows Anaconda 4.1.1(Python 3.5) + OpenCVで動作確認済み
import numpy as np
import cv2
import time
from PIL import Image
import matplotlib.pyplot as plt
import copy
import http.client
import urllib.parse
import json
import pprint
import datetime
import requests
import serial


def sent_req(age, gender, time, direction_in="True", ID="001"):
    """ 引数からjsonを作って、サーバーにPOSTする
    """
    #POSTパラメータは二つ目の引数に辞書で指定する
    response = requests.post(
        'https://shelterassist-56940.firebaseio.com/items.json',
        json.dumps({'time':str(time), "age":int(age), "gender":gender}),
        headers={'Content-Type': 'application/json'})
    pprint.pprint(response.json())
    return
#sent_req(13, "female", "2016-10-08 23:07:29.056724+09:00") # sample for test


def get_photo_data(file_name, api_key):
    """ 画像から人の情報を取得する
    """
    headers = {
        # Request headers
        #'Content-Type': 'application/json', # image from Web version
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': api_key,
    }
    params = urllib.parse.urlencode({
        # Request parameters
        #'visualFeatures': 'Description,Faces',
        'visualFeatures': 'Faces,Color', # jender, age
        # 'visualFeatures': 'Categories,Tags, Description, Faces, ImageType, Color, Adult',
        # 'details': 'Celebrities'
    })
    conn = http.client.HTTPSConnection('api.projectoxford.ai')

    # image from Web version
    #image_url = 'http://www.python.jp/images/22027340636_8d2e74b3ce_z.jpg'
    #image_url = "http://www.sojo-u.ac.jp/faculty/department/architecture/news/images/IMG_9366low.jpg"
    #body = """{'url': '%s'}""" % (image_url)
    #conn.request("POST", "/vision/v1.0/analyze?%s" % params, body, headers)

    # file version
    img = open(file_name, 'rb').read()
    conn.request("POST", "/vision/v1.0/analyze?%s" % params, img, headers)

    response = conn.getresponse()
    caption_data = response.read().decode('ascii')
    #print(caption_data)
    #print(type(caption_data))
    conn.close()
    return caption_data


# カメラ読み込みイベントのトリガー処理用（クラスにすべきだろうが、面倒）
obj = None
def detect_with_img(image, hist):
    """ 画像を用いて、動体検知して、検出結果を返す
    輝度のヒストグラムを作成して、前回の輝度分布との差から動体検知を行います。
    """
    w,h = image.size    # 画像の幅・高さを取得
    _hist = [0,]*256
    for j in range(h):
        for i in range(w):
            pixval = image.getpixel((i, j))
            _hist[pixval] += 1
    _hist = np.array(_hist)
    _hist = _hist / _hist.max() # 正規化
    if isinstance(hist, list) or isinstance(hist, np.ndarray):
        _sum = sum([(x - y) ** 2 for x,y in zip(_hist, hist)]) # 差分の計算
        result = _sum > 0.2
        print(_sum, result)
        return copy.copy(_hist), result
    else:
        return copy.copy(_hist), False


def detect_with_hardsensor(ser):
    """ Arduinoを用いて、動体検知して、検出結果を返す
    基本的には、Arduino側で一次処理をしておく。
    argv:
        ser シリアル通信オブジェクト（既にオープンしていること）
    """
    try:
        buff = ser.readline()                        # reading data valure from PORT, return bytes
        buff = buff.decode("ascii", errors="ignore") # bytes to str
        buff = buff.rstrip()
        #print(buff)
        if buff != "" and buff != "-":
            val = float(buff)
            result = val > 0.1
            print("sensor ", val, result)
            if result:
                return True
    except Exception as e:
        print("Something Went Wrong on Serial", str(e))

    return False



# カメラ読み込みの準備
cap = cv2.VideoCapture(0)    # if you have some camera, choice it by index.

# シリアル通信のための準備
#ser = serial.Serial('/dev/tty.usbmodem1411', 38400, timeout=0) # This is for Linux/Mac
#ser = serial.Serial('COM3',38400, timeout=0) # for Windows

# setup for Computer Vision API
api_key = ""
with open("ignore/Computer Vision API key.txt", "r") as fr:
    api_key = fr.readline().rstrip()

# main loop
while(True):
    # カメラの画像をキャプチャする
    ret, frame = cap.read()
    im = Image.fromarray(frame)   # ndarrayをImageのオブジェクトに変換
    w,h = im.size
    im_send = np.asarray(im)                              # 送信用
    im_view = np.asarray(im.resize((int(w/3), int(h/3)))) # 表示用
    
    obj, detection = detect_with_img(im.resize((int(w/20), int(h/20))).convert("L"), obj) # ヒストグラム計算用として、縮小＆グレースケール化したものを渡す
    #detection = detect_with_hardsensor(ser)

    # 画面に表示する
    if detection:
        _now = datetime.datetime.now()
        #_now = int(time.mktime(_now.timetuple()))
        path = "photo/photo_" + _now.strftime('%Y%m%d%H%M%S') + ".jpg" # photoというディレクトリがなかったら作って下さい。
        cv2.imshow('camera capture', im_view)   # 画像の表示
        if cv2.waitKey(100) >= 0:               # X msだけキー入力を待つ（これを入れないと画像が表示されない）
            break                               # if any key is pressed, break.　（うまく行っていない on Mac Python3.4.2）
        cv2.imwrite(path, im_send)              # 画像として保存
        data = get_photo_data(path, api_key)
        res = json.loads(data)
        if "faces" in res:
            faces = res["faces"]                # list<dict>
            for human in faces:
                age = human["age"]
                gender = human["gender"]
                txt = "detection result,{0},{1},{2}\n".format(age, gender, _now)
                with open("log.txt", "a") as fw:
                    fw.write(txt)
                print(txt)
                sent_req(age, gender, str(_now)) # サーバーに結果を通報（不要ならコメントアウト）
    #time.sleep(0.5)

# キャプチャの後始末と，ウィンドウをすべて消す
cap.release()
cv2.destroyAllWindows()



