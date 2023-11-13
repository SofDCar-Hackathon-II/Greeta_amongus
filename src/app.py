import numpy as np
import cv2
import cv2.aruco as aruco
import os
import time
from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import Datapoint
from deepface import DeepFace
import cv2.aruco as aruco
import pygame
pygame.init()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
time.sleep(5)
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_color = (255, 255, 255)  # White color in BGR
font_thickness = 2
frame_rate = 30
prev = time.time()


aruco_dict = aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
arucoParams =  aruco.DetectorParameters()

def set_vss_value(vss, value):
    with VSSClient('192.168.1.99', 55556) as client:
    
        client.set_current_values({
            vss: Datapoint(value)
        })

def get_vss_value():
      with VSSClient('192.168.1.99', 55556) as client:
        for updates in client.subscribe_current_values([
        'Vehicle.Window.Row1.DriverSide.Sensor.Position',
        'Vehicle.Window.Row2.DriverSide.Sensor.Position'
    ]):
            return updates['Vehicle.Window.Row1.DriverSide.Sensor.Position'].value
        

def main():
    global verified, drunk, playing_aud
    verified = 0
    drunk = 0
    playing_aud = 0

    def setDrunk():
        global drunk
        drunk = 1

    def setVerified():
        global verified
        verified = 1

    def setAudio():
        global playing_aud
        playing_aud = 1

    
    def isVerified():
        return verified == 1
    
    def isDrunk():
        return drunk == 1
    
    def isAudioPlaying():
        return playing_aud == 1
    
    def car_action_verified():
        # set_vss_value("Vehicle.Window.Row2.DriverSide.Action", "open")
        # set_vss_value("Vehicle.Window.Row1.DriverSide.Action", "open")
        # set_vss_value("Vehicle.Door.Row1.DriverSide.Action", "open")
        print('verified action')

    def car_action_drunk():
        # set_vss_value("Vehicle.Window.Row2.DriverSide.Action", "open")
        # set_vss_value("Vehicle.Door.Row2.DriverSide.Action", "open")
        print('drunk action')

    def car_action():
        # set_vss_value("Vehicle.Window.Row2.DriverSide.Action", "close")
        # set_vss_value("Vehicle.Window.Row1.DriverSide.Action", "close")
        # set_vss_value("Vehicle.Door.Row1.DriverSide.Action", "close")
        # set_vss_value("Vehicle.Door.Row2.DriverSide.Action", "close")
        print('secure action')

    def playAudio():
        my_sound2 = pygame.mixer.Sound(os.path.abspath('src'+os.sep+'alexa2.wav'))
        my_sound2.set_volume(1.0)
        my_sound2.play()
        my_sound = pygame.mixer.Sound(os.path.abspath('src'+os.sep+'welcome.wav'))
        my_sound.set_volume(0.5)
        my_sound.play()

    def authenticate_face(data, frame):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(frame, scaleFactor=1.3, minNeighbors=5)
        cv2.putText(frame, str(len(faces)), (50, 50), font, font_scale, font_color, font_thickness)
        corners, ids, rejected = aruco.detectMarkers(
            frame, aruco_dict, parameters=arucoParams
        )
  
        if ids is not None:
            if ids[0][0] == 0:
                setDrunk()

        if len(faces) > 0 and verified == 0:
            cv2.putText(frame, 'Verifying', (100, 50), font, 2, font_color, font_thickness)

            if DeepFace.verify(img1_path=os.path.abspath('src'+os.sep+'test.jpg'), img2_path=frame, enforce_detection=False)['verified'] == True:
                print(isVerified())
                setVerified()
                print(isVerified())
                return frame
        return frame

    while(True):
        ret, frame = cap.read()
        if (time.time() - prev) > 1 / frame_rate:
            data = cv2.resize(frame, (299, 299))
            frame = authenticate_face(frame, frame)

            if isVerified():
                cv2.putText(frame, 'Verified', (100, 50), font, 2, font_color, font_thickness)
                car_action_verified()
                if isAudioPlaying() != 1:
                    playAudio()
                    setAudio()
              
            elif isDrunk():
                car_action_drunk()

            else:
                car_action()

            cv2.imshow("Display", frame)        

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()