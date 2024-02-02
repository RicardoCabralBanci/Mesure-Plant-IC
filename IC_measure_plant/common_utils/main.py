#!/usr/bin/python3

import rtsp

import cv2

import time

from common_utils.web_video_stream_multiple import mjpg_stream

import numpy

from threading import Thread

import os

 

image_path = r'C:\Users\20.95005-5\Desktop\WebRTC-diferente\Imagens'

class ThreadedRTSPtoMJPG():

    def __init__(self, mjpeg_server, rtsp_cameras_transforms):

        self.mjpeg_server = mjpeg_server

        self.rtsp_cameras_transforms = rtsp_cameras_transforms

        self.loops = [True for x in rtsp_cameras_transforms]

        self.threads = []

        self.rtsp_server_uri = [x['rtsp_url'] for x in self.rtsp_cameras_transforms]

 

        for x in range(len(rtsp_cameras_transforms)):

            self.threads.append(Thread(target = self._run, args = [x]))



    def start_threads(self):

        for x in self.threads:

            x.start()

 

    def _run(self,index):

        try:

            print("Starting Camera#" + str(index+1))

            _image = cv2.VideoCapture(self.rtsp_server_uri[index])
            success, img = _image.read()
            cv2.imshow("Result", img)
            time.sleep(5)
            cv2.imwrite('Imagens/Horta09.jpg', img)
            while self.loops[index]:

                #print('Atualizada Camera#' + str(index+1))

                ret, frame = _image.read()

                if(frame is not None):

                    self.mjpeg_server.update_frame(frame.copy(), index)

                    if cv2.waitKey(1)&0xFF == ord('q'):

                        break

 

        except Exception as e:

            print("Error on "+str("Thread#"+str(index+1)))

            print(e)

            ##raise

            print('Ending Camera#' + str(index+1))

 

    def kill_all(self):

        self.loops = [False for x in rtsp_cameras_transforms]



 

rtsp_cameras_transforms = [

     {'rtsp_url':'rtsp://admin:SmartCamera@10.33.133.146:554/cam/realmonitor?channel=1&subtype=0',

     'mjpeg_url_ext':'agro_cam'}

     

]

 

streams = [x['mjpeg_url_ext'] for x in rtsp_cameras_transforms]

mjpg_server = mjpg_stream(ip = '127.0.0.1', streams = streams, port = 8090)

time.sleep(0.8)

rtsp_transform = ThreadedRTSPtoMJPG(mjpg_server, rtsp_cameras_transforms)

rtsp_transform.start_threads()

while True:

    try:

        time.sleep(0.8)

    except KeyboardInterrupt:

        rtsp_transform.kill_all()

 

mjpg_server.disconnect()