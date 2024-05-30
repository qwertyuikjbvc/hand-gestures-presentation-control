import cv2
import os
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Variables
width, height = 1280, 720
folderPath = 'presentation'

# Get the list of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)

# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Variables
imgNumber = 0
camScale = 3
hs, ws = int(120*camScale), int(213*camScale)
gestureThreashold = height//4*3
buttonPressed = False
buttonCounter = 0
buttonDelay = 5
annotations = [[]]
annotationsColors = [[]]
annotationsNumber = 0
annotationsStart = False
menuDelayTime = 30
menuTimer = 0
annotationColor = (0,255,0)
changeColor = False
currentImgNumber = [[] for i in range(len(pathImages))]


# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    # Import Images
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)
    hands, img = detector.findHands(img)
    h, w, _ = imgCurrent.shape
    cv2.circle(imgCurrent, (70, 70), 30, annotationColor, cv2.FILLED)
    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx,cy = hand['center']
        lmList = hand['lmList']

        # Constrain values for easier drawing
        xValue = int(np.interp(lmList[8][0], [width // 2, width], [0, 1920*5//2]))
        yValue = int(np.interp(lmList[8][1], [150, height-150], [0, 1080*5//2]))
        indexFinger = xValue, yValue
        if not changeColor:
            #Gesture 1 - Left
            if fingers == [1,0,0,0,0] and buttonPressed == False and cy < gestureThreashold:
                buttonPressed = True
                if imgNumber >0:
                    imgNumber -=1
                annotations = [[]]
                annotationsColors = [[]]
                annotationsNumber =-1
            # Gesture 2 - Right
            if fingers == [0,0,0,0,1] and buttonPressed == False and cy < gestureThreashold:
                buttonPressed = True
                if imgNumber<len(pathImages)-1:
                    imgNumber +=1
                annotations = [[]]
                annotationsColors = [[]]
                annotationsNumber = -1

            # Gesture 3 - Show Pointer
            if fingers == [0,1,1,0,0]:
                cv2.circle(imgCurrent, indexFinger, 12, annotationColor, cv2.FILLED)

            #Gesture 4 - Draw
            if fingers == [0,1,0,0,0]:
                if annotationsStart is False:
                    annotationsStart = True
                    annotationsNumber +=1
                    annotations.append([])
                    annotationsColors.append([])
                    annotationsColors[annotationsNumber].append(annotationColor)
                cv2.circle(imgCurrent, indexFinger, 12, annotationColor, cv2.FILLED)
                annotations[annotationsNumber].append(indexFinger)
            else:
                annotationsStart = False

            #Gesture 5 - Erase
            if fingers == [0,1,1,1,0] and buttonPressed == False:
                buttonPressed = True
                if len(annotations)>0 and annotationsNumber > -1:
                    annotations.pop(-1)
                    annotationsNumber -=1
                    buttonPressed = True

            #Gesture 6 - Change color
            if fingers == [1,1,1,1,1]:
                changeColor = True



        else:
            if fingers == [0, 1, 0, 0, 0]:
                annotationColor = (255, 0, 0)
            if fingers == [0, 1, 1, 0, 0]:
                annotationColor = (0, 255, 0)
            if fingers == [0, 1, 1, 1, 0]:
                annotationColor = (0, 0, 255)
            # Gesture 7 - Cancel of changing
            if fingers == [0, 0, 0, 0, 0]:
                changeColor = False
    else:
        changeColor = False

    # Button Pressed Interations
    if buttonPressed:
        buttonCounter +=1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False


    # Drawing
    for i, annotation in enumerate(annotations):
        for j in range(len(annotation)):
            if j != 0:
                cv2.line(imgCurrent, annotation[j - 1], annotation[j], annotationsColors[i][0], 12)

    # Adding webcam image on the slide
    imgSmall = cv2.resize(img, (ws,hs))
    imgCurrent[0:hs, w-ws:w] = imgSmall

    newimg = cv2.resize(imgCurrent, (1920//4*3, 1080//4*3))

    # cv2.imshow("Image", img)
    cv2.imshow("Slides", newimg)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
