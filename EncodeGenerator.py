#Generate the encodings of the faces in the dataset

#Import the necessary packages
import cv2 
import os 
import face_recognition
import pickle 
import firebase_admin
from firebase_admin import storage, credentials, db

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-attendance-system-be24c-default-rtdb.firebaseio.com/",
    'storageBucket': 'face-attendance-system-be24c.appspot.com'
})

ref = db.reference('Students')

def upload_image(fileName):
    #Upload the images to the firebase storage
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

#Importing the student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
# print(pathList) #Check if all the images are imported
imgList = []
studentIds = []
for path in pathList:
    #Import the images into a list
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])
    # Upload the images to the firebase storage
    upload_image(os.path.join(folderPath, path))
    
print(studentIds) #Check all the student ids are imported

#Encode the images
def findEncodings(imagesList):
    encodeList = []
    # print(imagesList)
    for img in imagesList:
        #Change the color of the image from BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        except:
            print('No face found in the image')
        
    
    return encodeList

if __name__ == '__main__':
    print('Encoding Started...')
    encodeListKnown = findEncodings(imgList)
    encodeListKnownWithIds = [encodeListKnown, studentIds]
    print('Encoding Completed...')
    #Save the encodings in a file
    with open('encodings.p', 'wb') as f:
        pickle.dump(encodeListKnownWithIds, f)
    print('File Saved...')




