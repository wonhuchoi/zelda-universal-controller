import pyaudio
import sys
import numpy as np
import aubio
from pynput.keyboard import Key, Controller
import pyautogui

import imutils
import cv2


class webcamController:

    # initialise pyaudio# define a video capture object
    def __init__(self):
        pass


    keyboard = Controller()
    slidingWindow = [None, None, None]

    keyboardMap = {
        'right': Key.right,
        'left': Key.left,
        'up': Key.up,
        'down': Key.down,
        'A': 'a',
        '': '',
        'R': 'r',
        'B': 'b'
    }


    def moveSlidingWindow(self, key):
        self.slidingWindow[0] = self.slidingWindow[1]
        self.slidingWindow[1] = self.slidingWindow[2]
        self.slidingWindow[2] = key
        # print(slidingWindow)

    def pressKey(self, input, releaseKey = None):
        # print("pressing key", input)
        if input == None:
            return
        keyToPress = self.keyboardMap[input]
        if releaseKey != input and releaseKey != None:
            keyToRelease = self.keyboardMap[releaseKey]
            self.keyboard.release(keyToRelease)
        if keyToPress == '' and releaseKey != None:
            keyToRelease = self.keyboardMap[releaseKey]
            self.keyboard.release(keyToRelease)
        elif keyToPress == '' and releaseKey == None:
            return
        else:  
            self.keyboard.press(keyToPress)
            return input

    def getClosest(self, val1, val2, target): 
        
        if (target - val1 >= val2 - target): 
            return val2 
        else: 
            return val1 

    def findClosest(self, arr, n, target): 
        
        # Corner cases 
        if (target <= arr[0]): 
            return arr[0] 
        if (target >= arr[n - 1]): 
            return arr[n - 1] 
        
        # Doing binary search 
        i = 0; j = n; mid = 0
        while (i < j):  
            mid = int((i + j) / 2)
        
            if (arr[mid] == target): 
                return arr[mid] 
        
            # If target is less than array  
            # element, then search in left 
            if (target < arr[mid]) : 
        
                # If target is greater than previous 
                # to mid, return closest of two 
                if (mid > 0 and target > arr[mid - 1]): 
                    return getClosest(arr[mid - 1], arr[mid], target) 
        
                # Repeat for left half  
                j = mid 
                
            # If target is greater than mid 
            else : 
                if (mid < n - 1 and target < arr[mid + 1]): 
                    return getClosest(arr[mid], arr[mid + 1], target) 
                        
                # update i 
                i = mid + 1
                
        # Only single element left after search 
        return arr[mid]
    # open stream
    def run(self):
        vid = cv2.VideoCapture(0)
        currentKey = None
        while(True):
            
            # Capture the video frame
            # by frame
            ret, frame = vid.read()
        
            # Display the resulting frame
            
            # cv2.imshow('frame', frame)
            

            # load the image and resize it to a smaller factor so that
            # the shapes can be approximated better
            image = frame
            resized = imutils.resize(image, width=300)
            ratio = image.shape[0] / float(resized.shape[0])
            # convert the resized image to grayscale, blur it slightly,
            # and threshold it
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
            # find contours in the thresholded image and initialize the
            # shape detector
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            sd = ShapeDetector()
            shapes = []
            for c in cnts:
                if cv2.arcLength(c,True) < 100:
                    continue
                # compute the center of the contour, then detect the name of the
                # shape using only the contour
                M = cv2.moments(c)
                try:
                    cX = int((M["m10"] / M["m00"]) * ratio)
                    cY = int((M["m01"] / M["m00"]) * ratio)
                    # print("this is c", c)
                except:
                    continue
                shape = sd.detect(c)
                shapes.append(shape)
                # print(shape)
                # multiply the contour (x, y)-coordinates by the resize ratio,
                # then draw the contours and the name of the shape on the image
                c = c.astype("float")
                c *= ratio
                c = c.astype("int")
                cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 2)
                # show the output image
                # cv2.imshow("Image", image)
                # cv2.waitKey(0)
            keyPressed = None
            if 'rectangle' in shapes or 'square' in shapes:
                keyPressed = 'R'
            elif 'triangle' in shapes:
                keyPressed = 'B'

            self.moveSlidingWindow(keyPressed)

            # cv2.imshow("Image", thresh)
            if self.slidingWindow[0] == self.slidingWindow[1] and self.slidingWindow[1] == self.slidingWindow[2] and self.slidingWindow[0] != None:
                # print(slidingWindow)
                # print("pressing ", keyPressed)
                pressedKey = self.pressKey(keyPressed, currentKey)
                currentKey = pressedKey
                # pass


            cv2.imshow("Image", image)
            # the 'q' button is set as the
            # quitting button you may use any
            # desired button of your choice
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # After the loop release the cap object
        vid.release()
        # Destroy all the windows
        cv2.destroyAllWindows()




class ShapeDetector:
    def __init__(self):
	    pass

    def detect(self, c):
        # initialize the shape name and approximate the contour
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        if len(approx) == 3:
            shape = "triangle"
        # if the shape has 4 vertices, it is either a square or
        # a rectangle
        elif len(approx) == 4:
            # compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)
            # a square will have an aspect ratio that is approximately
            # equal to one, otherwise, the shape is a rectangle
            shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
        # if the shape is a pentagon, it will have 5 vertices
        elif len(approx) == 5:
            shape = "pentagon"
        # otherwise, we assume the shape is a circle
        else:
            shape = "circle"
        # return the name of the shape
        return shape

  # import numpy as np

  # pitches=[69]
  # dur=0.5
  # Fs=4000
  # amp=1

  # N = int(dur * Fs)
  # t = np.arange(N) / Fs
  # x = []

  # for p in pitches:
  #     freq = 2 ** ((p - 69) / 12) * 440
  #     x = np.append(x, np.sin(2 * np.pi * freq * t))

  # print(x)