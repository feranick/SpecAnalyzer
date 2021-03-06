'''
cameraFeed.py
-------------
Class for providing a hardware support for 
for the cameraFeed

Copyright (C) 2017-2018 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017-2018 Michel Nasilowski <micheln@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import cv2
import time, sys
import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from datetime import datetime

class CameraFeed():
    # Setup connection to OpenCV
    def __init__(self):
        self.camera_port = 0
        self.ramp_frames = 2
        self.camera = cv2.VideoCapture(self.camera_port)
        #time.sleep(2)
        self.camera.set(10, -200)
        self.camera.set(15, -8.0)

    # Grab frame into variable from live
    def grab_image_live(self):
        self.closeLiveFeed = False
        windowTitle = 'Live Feed: push \"q\" to stop and grab frame'
        while True:
            ret, frame = self.camera.read()

            cv2.namedWindow(windowTitle)
            # Our operations on the frame come here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            def mouse_callback(event, x, y, flags, param):
                if event == cv2.EVENT_LBUTTONDOWN:
                    intensity = gray[y,x]
                    print(" Intensity pixel at ["+str(x)+", "+str(y)+"]: "+str(intensity))
        
            cv2.setMouseCallback(windowTitle, mouse_callback)
            cv2.imshow(windowTitle,gray)
        
            if (cv2.waitKey(1) & 0xFF == ord('q')) or self.closeLiveFeed == True:
                cv2.destroyAllWindows()
                break
        for i in range(self.ramp_frames):
            temp = self.camera.read()
        _, self.img = self.camera.read()
        return self.img
        
    def grab_image(self):
        #ret, frame = self.camera.read()
        for i in range(self.ramp_frames):
            temp = self.camera.read()
        _, self.img = self.camera.read()
        return self.img
        
    # Process image
    def get_image(self, crop, x1, x2, y1, y2):
        if crop == True:
            self.img1 = self.img[min(y1,y2):max(y1,y2), min(x1,x2):max(x1,x2)]
        else:
            self.img1 = self.img
        self.img_raw = Image.fromarray(self.img1).convert('L')
        self.imgg = ImageQt(self.img_raw)
        self.img_data = np.asarray(self.img1)
        self.imgg_orig = ImageQt(Image.fromarray(self.img).convert('L'))
        return self.imgg, self.img_data, self.imgg_orig

    # Save image
    def save_image(self, filename):
        img_bw = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
        cv2.imwrite(filename,img_bw)

    # Logic for checking alignment
    def check_alignment(self, img_data, thresholdPerc):
        count = 0
        self.iMax = np.amax(img_data)
        threshold = thresholdPerc*self.iMax
        for i in np.nditer(img_data):
            if i > threshold:
                count = count + 1
        contrast = 100*count/img_data.size
        print(" Check alignment [%]: {0:0.3f}".format(contrast))
        return "{0:0.3f}".format(contrast), self.iMax

    '''
    def check_alignment_old(self, threshold):
        sumint=np.sum(self.img_data)
        #print(sumint)
        if sumint>10000000:
            print ('Attention: devices and mask might be misaligned')
        else :
            print ('Devices and mask are properly aligned')
    '''

    # Close connection to camera
    def close_cam(self):
        self.closeLiveFeed = True
        cv2.destroyAllWindows()
        del(self.camera)
