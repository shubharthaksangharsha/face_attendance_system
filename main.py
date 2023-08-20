#Import required libraries
import cv2 
import cvzone
import os 
import face_recognition
import pickle
import numpy as np 
import firebase_admin
from datetime import datetime
from firebase_admin import storage, credentials, db

#Initialize the firebase app
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-attendance-system-be24c-default-rtdb.firebaseio.com/",
    'storageBucket': 'face-attendance-system-be24c.appspot.com'
})
bucket = storage.bucket()
#Create a VideoCapture object
cap = cv2.VideoCapture(-1)
#Set the width and height
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

#Import the modes images into a list 
folderModePath = 'Resources/Modes'
modePath = os.listdir(folderModePath)
imgModeList = []
for path in sorted(modePath):
    # print(path)
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

#print(len(imgModeList)) #Check if all the images are imported

#Load the encoding file
with open('encodings.p', 'rb') as f:
    encodeListKnownWithIds = pickle.load(f)

#Get the encodings and ids from the file
encodeListKnown, studentIds  = encodeListKnownWithIds

# print(studentIds) #Check all the student ids are imported
print('Encoding Loaded...')
modeType = 0
counter = 0
id = -1
imgStudent = []
while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    #Change the color of the image from BGR to RGB
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    #Find the face locations in the image
    facesCurFrame = face_recognition.face_locations(imgS)
    #Find the encodings of the faces in the image
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    #Put the image in the background
    imgBackground[162:162+480, 55:55+640] = img
    imgBackground[44:44 + 633, 808: 808 + 414] = imgModeList[modeType]

    if facesCurFrame:
        #Loop through all the encodings in the frame
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print(matches, faceDis)

            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                # print('Known Face Detected')
                # print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1 , 162 + y1, x2 - x1, y2 - y1
                # print(bbox)
                # imgBackground = cv2.rectangle(imgBackground, (x1, y1), (x2, y2), (0, 255, 0), 2)
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                
                if counter == 0:
                    counter = 1
                    modeType = 1
        if counter != 0:

            if counter == 1:
                #Get the student info from the database
                studentInfo = db.reference(f"Students/{id}").get()
                print(studentInfo)
                # print(studentInfo)
                #Get the image from the firebase storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                #Update the data of attendance
                date_time = datetime.strptime(studentInfo['last_attendance_time'], 
                                            "%Y-%m-%d %H:%M:%S")
                
                secondsElapsed = (datetime.now() - date_time).total_seconds() #seconds passed
                print(secondsElapsed)
                day = 24 * 3600
                if secondsElapsed > 10:
                    ref = db.reference(f"Students/{id}")
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    # modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808: 808 + 414] = imgModeList[modeType]        
            if modeType != 3:
                if 50 < counter < 100:
                    modeType = 2
                imgBackground[44:44 + 633, 808: 808 + 414] = imgModeList[modeType]
                # cv2.imwrite(f'./Output/img{counter}.png', imgBackground)


                if counter <= 50:   
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    
                    
                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    
                    imgBackground[175: 175 + 216, 909: 909 + 216] = imgStudent
                    
                
                counter += 1

                if counter >= 111:
                    counter = 0
                    modeType = 0
                    studentInfo = []

                    imgStudent = []
                    imgBackground[44:44 + 633, 808: 808 + 414] = imgModeList[modeType]
    else:
        counter = 0
        modeType = 0
        # imgBackground[44:44 + 633, 808: 808 + 414] = imgModeList[modeType]

    # cv2.imshow("Webcam", img) #To check the webcam
    cv2.imshow('Face Attendance ', imgBackground)
    cv2.waitKey(1)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
