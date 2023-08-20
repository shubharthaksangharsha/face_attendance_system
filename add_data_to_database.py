import firebase_admin
from firebase_admin import credentials
from firebase_admin import db 

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-attendance-system-be24c-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "20bcs6872" : 
        {
            "name": "Shubharthak",
            "major": "AIML",
            "starting_year": 2020,
            "total_attendance": 6,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2023-08-20 05:28:34"
        },
    "852741" : 
        {
            "name": "Emly Blunt",
            "major": "Economics",
            "starting_year": 2018,
            "total_attendance": 12,
            "standing": "B",
            "year": 2,
            "last_attendance_time": "2023-08-20 05:28:34"
        },
    "963852" : 
        {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2020,
            "total_attendance": 6,
            "standing": "G",
            "year": 2,
            "last_attendance_time": "2023-08-20 05:28:34"
        }
}

for key, value in data.items():
    ref.child(key).set(value)