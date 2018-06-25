
import face_recognition
import cv2
import numpy as np 
import pandas as pd 
from flask_table import Table, Col
from flask import Markup
from flask import Flask
from flask import render_template, Flask, request
import time 
import argparse
import datetime


parser = argparse.ArgumentParser()
parser.add_argument('--refresh-time', type=int, default="15", help='time to take new picture, default 15 second')
parser.add_argument('--pit-time', type=int, default="1", help='time to take new picture, default 1 min')
parser.add_argument('--last-x', type=int, default="10", help='last x activity')
args = parser.parse_args()


app = Flask(__name__)

# Declare your table
class ItemTable(Table):
    name = Col('Name')
    times = Col('Times')

# Get some objects
class Item(object):
    def __init__(self, name, times):
        self.name = name
        self.times = times

font = cv2.FONT_HERSHEY_DUPLEX

# Load a sample picture and learn how to recognize it.
hamza_image = face_recognition.load_image_file("hamza.jpg")
hamza_face_encoding = face_recognition.face_encodings(hamza_image)[0]
known_names = ['HAMZA']
known_encods = [hamza_face_encoding]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
items = []

now = datetime.datetime.now()
data = [["Start",now.strftime("%Y-%m-%d %H:%M")]]

shown_data = [["Start",now.strftime("%Y-%m-%d %H:%M")]]

def get_data():
    # Grab a single frame of video
    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()

    
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    name = "Unknown"
    face_names = []
    for face_encoding in face_encodings:
        for ii in range(len(known_encods)):
            # See if the face is a match for the known face(s)
            match = face_recognition.compare_faces([known_encods[ii]], face_encoding)
            if match[0]:
                name = known_names[ii]
        face_names.append(name)
    if face_names != []:
        for name in face_names:
            now = datetime.datetime.now()
            data.append([name, now.strftime("%Y-%m-%d %H:%M")])
            if shown_data[-1][0] !=name:
                now = datetime.datetime.now()
                shown_data.append([name, now.strftime("%Y-%m-%d %H:%M")])
    else:
        now = datetime.datetime.now()
        data.append(['EMPTY', now.strftime("%Y-%m-%d %H:%M")])
        if shown_data[-1][0] !='EMPTY':
            now = datetime.datetime.now()
            shown_data.append(["EMPTY", now.strftime("%Y-%m-%d %H:%M")])

    
    table = ItemTable(items)


    video_capture.release()
    cv2.destroyAllWindows()

    datac = np.array(data)
    df = pd.DataFrame(datac, columns=['name', 'time'])
    df.to_csv("data.csv", index = False)
    
    return table, shown_data, data 

# Pass cart data 
def get_empty_chart(data):
    emp = []
    labels = []
    pit_size = args.pit_time * 60 // args.refresh_time 
    data = data[-1200:]

    if len(data) > pit_size:
        for i in range(0,len(data[:( len(data) - len(data)%pit_size)  ]),pit_size):
            if_emp = False
            for j in range(pit_size):
                if data[i+j][0] != "EMPTY":
                    if_emp=True
            if not if_emp:
                emp.append(10)
            else:
                emp.append(0)
            labels.append(str(data[i][1]))

    return emp, labels


@app.route("/")
def index():
    _, shown_data, data = get_data()
    emp, labels = get_empty_chart(data)

    if len(shown_data) >= args.last_x:
        return render_template("index.html",  data = shown_data[-10:] , emp = emp, labels = labels, refresh = args.refresh_time , num_activity = args.last_x)
    else:
        return render_template("index.html",  data = shown_data, emp = emp, labels = labels, refresh = args.refresh_time , num_activity = args.last_x )


if __name__ == '__main__':

    app.run(use_reloader=True, debug=True)



