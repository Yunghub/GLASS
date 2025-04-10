import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import requests

class facialRecognition():
    def __init__(self, username: str, password: str, classID: str):
        self.username = username
        self.password = password
        self.classID = classID
        self.cachedIDs = {}
        self.path = 'images'  # path to the directory where images are stored
        self.images = []  # list to store the images
        self.classNames = []  # list to store the names of the classes (i.e. names of the images)
        self.myList = os.listdir(self.path)  # list of all the files in the 'images' directory
        print(self.myList)
        for cl in self.myList:  # loop through all the files
            curImg = cv2.imread(f'{self.path}/{cl}')  # read the image
            self.images.append(curImg)  # add the image to the list of images
            self.classNames.append(os.path.splitext(cl)[0])  # add the name of the class (name of the image) to the list of class names
            print(self.classNames)  # print the list of class names
        
 
    def findEncodings(self, images):
        encodeList = []
        for img in self.images:
            # Convert the image to the RGB color space
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Find the encodings for the image
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    
    def markAttendance(self, id):
        lesson_id = self.classID

        # Make a GET request to the attendance mark
        url = f"https://api.yungcz.com/teacher/{self.username}/attendance/mark/{id}/{lesson_id}/Present"

        header = {"password": self.password}
        x = requests.get(url, headers = header)
        print(x.text)

    def takePicture(self, id):
        # Initialize the video capture with the default camera
        cap = cv2.VideoCapture(0)

        # Capture a frame and store it in the 'img' variable
        success, img = cap.read()
        # Save the frame as an image file with the specified 'id' as the file name
        cv2.imwrite(f"images/{id}.jpg", img)

        # Release the video capture and close all windows
        cap.release()
        cv2.destroyAllWindows()


    def run(self):
        # Encode images of known people
        encodeListKnown = self.findEncodings(self.images)
        print('Encoding Complete')
        
        # Initialize video capture from webcam
        cap = cv2.VideoCapture(0)
        
        while True:
            # Read frame from webcam
            success, img = cap.read()
            
            # Resize frame for faster processing
            imgS = cv2.resize(img,(0,0),None,0.25,0.25)
            
            # Convert frame to RGB color scheme (face_recognition library uses RGB)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            
            # Find locations and encodings of faces in current frame
            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
            
            # Iterate through each face in the current frame
            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                # Check if the face in the current frame matches one of the known faces
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                # Get the distance between the known face and the face in the current frame
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                # Get the index of the closest matching face
                matchIndex = np.argmin(faceDis)
                print ("Running")
                
                # If a match is found
                if matches[matchIndex]:
                    # Try to get the name of the person from the cached IDs
                    try:
                        nameFormatted = self.cachedIDs[self.classNames[matchIndex]]
                    # If the ID is not in the cache, make a request to the API to get the name
                    except:
                        url = f"https://api.yungcz.com/id-to-name/{self.username}/{self.classNames[matchIndex]}"
                        header = {"password": self.password}
                        response = requests.get(url, headers = header)
                        nameFormatted = response.json()
                        # Concatenate first and last name
                        nameFormatted = nameFormatted["firstname"] + " " + nameFormatted["lastname"]
                        # Add the ID and name to the cache
                        self.cachedIDs[self.classNames[matchIndex]] = nameFormatted

                    # Scale up the face location coordinates
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                    # Draw a green rectangle around the face
                    cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                    cv2.rectangle(img,(x1,y2-25),(x2,y2),(0,255,0),cv2.FILLED)
                    cv2.putText(img,nameFormatted,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),2)
                    self.markAttendance(self.classNames[matchIndex])
        
            cv2.imshow('Webcam',img)
            cv2.waitKey(1)

