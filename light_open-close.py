import cv2 # OpenesCV ktphani.
import mediapipe as mp # MediaPipe ellerin izlenmesi için kullanılır.
import numpy as np #  Bilimsel hesaplamalar için kullanılan kütüphane.
import math # Matematik fonksiyonları için kullanılan kütüphane.
import time
from ctypes import cast, POINTER # Ses kontrolü için kullanılan kütüphaneler.
from comtypes import CLSCTX_ALL
from pycaw.pycaw import * # Ses kontrolü için kullanılır. 
# Ses aygıtlarının listesi alınır ve bir ses arayüzüne erişim sağlanır.
import keyboard
import pyautogui

devices = AudioUtilities.GetSpeakers()

# Bu satır, ses aygıtlarından birini seçmek ve onunla etkileşimde bulunmak için kullanılır. 
interface = devices.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None)

# Bu satır, seçilen ses aygıtı üzerinde işlem yapmak için bir arayüz (interface) oluşturur. 
vc = cast(interface,POINTER(IAudioEndpointVolume)) # vc -> volume control

# Bu satır, seçilen ses aygıtının desteklediği ses seviyesi aralığını alır
Range = vc.GetVolumeRange()

# Bu satır, ses seviyesi aralığını iki değişkene atar.
minR, maxR = Range[0], Range[1]

# MediaPipe kütüphanesindeki elleri izleme yöntemini temsil eden bir nesne oluşturur
mpHands = mp.solutions.hands

# mpHands nesnesi üzerinden Hands adlı bir alt nesne oluşturulur. 
# Hands alt nesnesi, gerçek zamanlı el izleme işlemlerini gerçekleştirmek için kullanılır.
Hands = mpHands.Hands()

# mpDraw nesnesi, el izleme sonuçlarını görselleştirmek ve çizimler yapmak için kullanılır.
mpDraw = mp.solutions.drawing_utils

# Bu satır, bir önceki frame'in işlenme zamanını temsil eden bir değişkeni başlatır. 
PTime = 0 # previous time

# Ses seviyesini temsil eden bir değişkeni başlatır
vol = 0

# Bu değer, görsel arayüzdeki çubuğun yüksekliğini temsil eder.
volBar = 300

# Bu satır, ses seviyesini yüzde cinsinden temsil eden bir değişkeni başlatır. 
# El izleme sonuçlarına bağlı olarak bu değer güncellenir ve bilgisayarın ses seviyesi kontrol edilir
volPer = 0 # volume percent

cap = cv2.VideoCapture(0) # Bilgisayarın kamerasına erişim sağlanır.

while (cap.isOpened()): 
    lmList = [] # (landmark listesi) 
    # bool : boolean -> True / False
    success, img = cap.read() # Kamera görüntüsü alınır  
    converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # renk formatı MediaPipe için uygun hale getirilir.
    results = Hands.process(converted_image) # Hands modeli ile el izleme işlemi gerçekleştirilir.

    # El tespit edildiyse, elin landmark'ları çizilir ve elin uç noktaları arasındaki mesafe hesaplanır.
    if results.multi_hand_landmarks:
        for hand_in_frame in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, hand_in_frame, mpHands.HAND_CONNECTIONS) # çizim yapılır    

        for id, lm in enumerate(results.multi_hand_landmarks[0].landmark):
            h, w, c = img.shape
            cx,cy = int(lm.x*w),int(lm.y*h)
            lmList.append([cx,cy])

        if len(lmList) != 0: # Bu mesafe, ses seviyesini kontrol etmek için kullanılır.
            x1,y1 = lmList[4][0], lmList[4][1] # baş parmak ucu konumu
            x2,y2 = lmList[8][0], lmList[8][1] # işaret parmak ucu konumu


            if y1 > y2:
                pyautogui.moveTo(1333, 747)
                pyautogui.dragTo(1333, 747, button='left')     # drag mouse to X of 100, Y of 200 while holding down left mouse button  
                pyautogui.PAUSE = 1
                
                if y1 > y2:
                    pyautogui.moveTo(1054, 672)
                    pyautogui.dragTo(1054, 672, button='left') 
                    pyautogui.PAUSE = 1

            elif y1 < y2:
                pyautogui.moveTo(1333, 747)
                pyautogui.dragTo(1333, 747, button='left')     # drag mouse to X of 100, Y of 200 while holding down left mouse button  
                pyautogui.PAUSE = 1
                
                if y1 < y2:
                    pyautogui.moveTo(1298, 672)
                    pyautogui.dragTo(1298, 672, button='left')
                    pyautogui.PAUSE = 1


              
            cv2.circle(img, (x1,y1), 15, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2,y2), 15, (255,0,0), cv2.FILLED)
            cv2.line(img,(x1,y1),(x2,y2),(255,0,0), 3, cv2.FILLED)
            length = math.hypot(x2-x1-30, y2-y1-30)

            vol = np.interp(length, [50,300], [minR,maxR])
            
            volBar = np.interp(length, [50,300], [400,150])
            volPer = np.interp(length, [50,300], [0,100])

            cv2.rectangle(img,(50,150),(85,400),(255,0,0))
            cv2.rectangle(img,(50,int(volBar)),(85,400),(255,0,0),cv2.FILLED)
            cv2.putText(img, f'{int(volPer)} %', (85,450),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),3)
            
            # Hesaplanan ses seviyesi, bilgisayarın ses kontrol kütüphanesi olan pycaw aracılığıyla bilgisayarın ses aygıtlarına uygulanır.
        

    CTime = time.time() # current time -> şimdiki zaman
    fps = 1 / (CTime-PTime)
    PTime = CTime

    # Frame rate (fps) hesaplanır ve ekrana yazdırılır.
    cv2.putText(img, str(int(fps)), (40,50), cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),3)
    
    # El izleme ekranı görüntülenir.
    cv2.imshow("Hand Tracking", img) 

    # Klavyeden 'Q' tuşuna basılırsa, program sonlandırılır.
    if cv2.waitKey(1) == 113: # 113 - Q
        break