import cv2
import numpy as np
import time
from cvzone.FaceDetectionModule import FaceDetector
import serial
from twilio.rest import Client
from datetime import datetime

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
current_date = now.date()
e = serial.Serial()
e.port = "COM9"
e.baudrate = 115200
e.open()


led=0

min_YCrCb = np.array([0,133,77],np.uint8)

max_YCrCb = np.array([255,173,127],np.uint8)


################################################

account_sid = 'ACbb455e0cbc127e2400b55bcb71d6f957'
auth_token = '74e231cba3ae2510dbb92310b6d7329d'
client = Client(account_sid, auth_token)



cam = cv2.VideoCapture(0)
# time.sleep(2)
result, image = cam.read()
time.sleep(2)
if result:
	#cv2.imshow("image", image)
	cv2.imwrite("My.png", image)

#--------------------------------------------Code----------------------------------------------------
#To quit from while loop
sourceImage = cv2.imread('jaundice1.jpg')
#sourceImage = cv2.imread('My.png')
#cv2.imshow('original',sourceImage)

imageYCrCb = cv2.cvtColor(sourceImage,cv2.COLOR_BGR2YCR_CB)

#Image Converted From rgb to YCrCb

#cv2.imshow('fromRGB2YCrCb',imageYCrCb)

# Using inrange function to detect skinregion by giving max and min value of YCrCb
skinRegion = cv2.inRange(imageYCrCb,min_YCrCb,max_YCrCb)

#Morphology

# se = np.ones((1,1), dtype='uint8')
# image_close = cv2.morphologyEx(skinRegion, cv2.MORPH_CLOSE, se)
# cv2.imshow('Morphology', image_close)
#

# Do contour detection on skin region
contours, hierarchy = cv2.findContours(skinRegion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Draw the contour on the image
for i, c in enumerate(contours):
    area = cv2.contourArea(c)
    if area > 1000:
        cv2.drawContours(sourceImage, contours, i, (0, 255, 0), 3)
        cv2.drawContours(skinRegion, contours, i, (0, 255, 0), 3)

#inorder to check for jaundice (but by putting thr ycrcb value and not the extracted skin value)
#its working even without skinregion but wont be efficient in real time processing
# image = cv2.cvtColor(imageYCrCb,cv2.COLOR_RGB2YCrCb)
toRGB = cv2.cvtColor(imageYCrCb,cv2.COLOR_YCrCb2RGB)
#cv2.imshow('rgb', toRGB)
reqd_image = cv2.bitwise_and(toRGB, toRGB, mask=skinRegion)



R,G,B = cv2.split(toRGB)
#print (contours)

#for Blue Intensity

print("Blue color Intensity")
print(float(np.average(B)))
Y,Cr,Cb = cv2.split(imageYCrCb)

#for Intensity of Cb

print("for intensity of Cb")
print(float(np.average(Cb)))
#Condition to Check For Jaundice
x = 0#for jaundice not detect
y=0
if np.average(B) < 110 and np.average(Cb) < 110:
    print("jaundice detected!!!")
    x = 1
    if(x==1):
        message = client.messages.create(
            body='Your ward is tested jaundice positive on {0} dated: {1}'.format(current_time, current_date),
            from_='+17473195024',
            to='+91 74839 91895'
        )
else:
    x = 0
    print("Jaundice Not Detected!!!")
    if(x==0):
        message = client.messages.create(
            body='Your ward is tested jaundice negative on {0} dated {1}'.format(current_time,current_date),
            from_='+17473195024',
            to='+91 74839 91895'
        )



if x==1:
    cap = cv2.VideoCapture(0)
    detector = FaceDetector()
    KeyPress = -1
    while (KeyPress < 1):
        success, img = cap.read()
        if success:
            if led == 0:
                led = 1
                a = "1"
                e.write(a.encode())
                print("ON")
            img, bBoxes = detector.findFaces(img)


            # print(bBoxes)

            cv2.imshow("Video", img)
            if cv2.waitKey(20) & KeyPress == ord('q'):
                break
        if bBoxes == []:
            y=1

            if led == 1:
                led = 0
                a = "2"
                e.write(a.encode())
                print("OFF")
                cap.release()
                cv2.destroyAllWindows()
            # KeyPress+=1
            break

    now1 = datetime.now()
    end_time = now1.strftime("%H:%M:%S")
    message = client.messages.create(
        body='Your ward was tested +ve at {0} and process was completed at {1}'.format(current_time, end_time),
        from_='+17473195024',
        to='+91 74839 91895'
    )