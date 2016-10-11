# sheltercare_local
2016-10-08〜09に熊本市で開催された「Race for Resilience 2016 熊本」のチームひなんじょが作成したソフトウェアです。ローカル側で動作させるプログラムを格納しています。

#Links
イベントページ, http://connpass.com/event/40111/  
本チームのサービス公開ページ, https://halsk.github.io/sheltercare/  
Webシステム側のソースコード, https://github.com/halsk/sheltercare  

#動作環境
*OS: Windows 10, Mac 10.11.6  
*other: Python3, OpenCV3, Arduino FTDI driver（Mac, Win10なら問題ないはず）  

#プログラムの説明
##Pythonのスクリプト　capture_final.py
このスクリプトは、カメラ画像から年齢と性別を推定し、DBサーバに通報するプログラムです。シリアルでArduinoからセンサーの値を受信しつつ、その値をトリガーとしてWebカメラから静止画を取得し、静止画をMicrosoftのComputer Vision APIに送信して性別と年齢の推定値を取得し、DBサーバーに性別と年齢の情報を送信します。ちなみに、送られたデータは性別ごとに統計が取られ、Webサーバ上でグラフ化されます（https://halsk.github.io/sheltercare/）。なお、画像をキャプチャするためのトリガーを画像から判断する場合はシリアル通信関係を利用しなくてOKです。
##Arduinoのプログラム
オムロンのSensorShield-EVK-001というシールドに照度センサを取り付けた上で、照度の時間変化率を求めています。求めた結果はシリアル（有線通信）でPC側に送られます。capture_final.pyでは受信した変化率をカメラ画像の保存のトリガーにしています。なお、オムロンが配布しているライブラリはArduino IDE 1.7.10ではビルドできなかったので少々改造しました。

#実行環境の構築
##PythonのセットアップとOpenCVのインストール
###Windowsの場合
Windowsの場合は、Anacondaをインストール後にOpenCVをpipでインストールするのが簡単です（文献1,2）。Anacondaのビット幅とOpenCVのビット幅は合わせて下さい。
###Macの場合
一番簡単なのは恐らく、homebrewでPythonとOpenCVを導入する方法です。文献3を参考に導入して下さい。2016-10時点では自前のビルドは不要です。
 
#ご利用上の注意
　DBサーバーに負荷をかけないようにして下さい。

#参考文献
[1] Anaconda, https://www.continuum.io/downloads, 2016-10.  
[2] OpenCV 3（core + contrib）をPython 3の環境にインストール＆OpenCV 2とOpenCV 3の違い＆簡単な動作チェック, http://qiita.com/olympic2020/items/d5d475a446ec9c73261e, 2016-10.  
[3] 【Mac】brewだけでOpenCV3+Python3(venv)の環境を構築する, https://www.blog.umentu.work/%E3%80%90mac%E3%80%91brew%E3%81%A0%E3%81%91%E3%81%A7opencv3python3venv%E3%81%AE%E7%92%B0%E5%A2%83%E3%82%92%E6%A7%8B%E7%AF%89%E3%81%99%E3%82%8B/, 2016-10.  
