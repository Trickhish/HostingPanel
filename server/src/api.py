import requests as rq
import json
from datetime import datetime, timezone, timedelta

from src.objects import *
import src.utils as utl
from src.config import *

def getCourse(cid):
    r = rq.get(f"https://api.edusign.fr/student/courses/{cid}", headers={
        "Authorization": f"Bearer {TOKEN}"
    })
    if (not(200 <= r.status_code < 300)):
        raise Exception(f"Error {r.status_code}")
    
    r = json.loads(r.text)
    return(r["result"])

def fetchCourseDetails(c: Course):
    dt = getCourse(c.id)
    c.completeData(dt)


def getCourses(start, end):
    #print(f"{start} - {end}")
    
    r = rq.get(f"https://api.edusign.fr/student/planning?start={start}&end={end}", headers={
        "Authorization": f"Bearer {TOKEN}"
    })
    if (not(200 <= r.status_code < 300)):
        print(r.text)
        raise Exception(f"Error {r.status_code}")
    
    r = json.loads(r.text)["result"]
    return(list(map(lambda c: Course.fromDt(c), r)))


def getAllCourse():
    std = "2025-09-01T07:38:39.000Z"
    edd = "2026-09-01T07:38:39.000Z"

    r = getCourses(std, edd)
    return(r)

    for c in r:
        # 'ID', 'NAME', 'START', 'END', 'LOCKED', 'CLASSROOM', 'SCHOOL_GROUP', 'DESCRIPTION', 'TRAINING_ID', 'NEED_STUDENTS_SIGNATURE', 'SURVEY_ID', 'SURVEY_ID_2', 'API_ID', 'PROFESSOR', 'PROFESSOR_SIGNATURE', 'idx', 'STUDENTS', 'surveyCount', 'STUDENT_IS_JUSTIFICATED', 'STUDENT_ABSENCE_ID', 'JUSTIFIED', 'STUDENT_PRESENCE', 'STUDENT_SIGNATURE', 'SIGNATURE_DATE', 'DELAY', 'COMMENT', 'EARLY_DEPARTURE', 'WAITING', 'EXCLUDED', 'REQUEST_STATUS', 'data_type', 'type'
        # cdt = getCourse(c["ID"]) #TRAINING_NAME
        print(f"{c['NAME']}: {c['ID']} | {cdt['TRAINING_NAME']} | starts {c['START']} in {c['CLASSROOM']}")

def getDayCourses():
    now = datetime.now()
    start = now.replace(hour=STARTOFDAYHOUR, minute=0, second=0, microsecond=0)
    end = now.replace(hour=ENDOFDAYHOUR, minute=0, second=0, microsecond=0)

    return(getCourses(utl.timeToISO(start), utl.timeToISO(end)))

def getNextCourse():
    now = datetime.now()
    start = now - timedelta(hours=5)
    #end = now.replace(hour=ENDOFDAYHOUR, minute=0, second=0, microsecond=0)
    end = now + timedelta(days=5)

    c = getCourses(utl.timeToISO(now), utl.timeToISO(end))
    if len(c)==0:
        return(None)

    return(c[0])

def getUser():
    r = rq.get("https://api.edusign.fr/student/account/getByToken", headers={
        "Authorization": f"Bearer {TOKEN}"
    })

    if (not(200 <= r.status_code < 300)):
        return(None)
    
    r = json.loads(r.text)
    if r["status"]=="success":
        return(r["result"]["FIRSTNAME"]+" "+r["result"]["LASTNAME"])
    
    return(None)

def checkTk():
    r = rq.get("https://api.edusign.fr/student/grades", headers={
    })

    if (not(200 <= r.status_code < 300)):
        return(False)
    
    r = json.loads(r.text)

    return(r["status"]=="success")

def setPresent(cid, qrid):

    body = {
        "courseId": cid,
        "phoneModel": "Web - opera - Opera 120",
        "tagInfo": {
            "lat": 48.815027,
            "lon": 2.3628162,
            "QRCodeId": qrid # Axdwbe7lBKZDhi1
        },
        "base64Signature": B64SIGN
    }

    r = rq.post("https://api.edusign.fr/student/courses/nfc-qrcode/setStudentPresent", json=body, headers={
        "content-type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    })

    return(r)

