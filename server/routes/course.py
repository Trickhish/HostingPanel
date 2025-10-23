from datetime import date
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json

import src.api as api
import src.utils as utl

router = APIRouter()

#@router.get("/{course_id}")
#async def course_handler(
#        course_id: str,
#    ):
#
#    return JSONResponse(content={})

class signBody(BaseModel):
    qrid: str

@router.post("/sign/{course_id}")
async def sign_handler(
        course_id: str,
        body: signBody
    ):

    print(f"Signing {course_id} with {body.qrid}")

    r = api.setPresent(course_id, body.qrid)

    if r.status_code<200 or r.status_code>299:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return JSONResponse(content=json.loads(r.text))

@router.get("/list")
async def list_handler():

    r = api.getDayCourses()
    if not r:
        raise HTTPException(status_code=404, detail="No course found")
    
    out = []

    for c in r:
        start = utl.timeFromISO(c.start)
        end = utl.timeFromISO(c.end)

        if start.strftime("%d/%m/%Y")==date.today().strftime("%d/%m/%Y"):
            sstday = "Aujourdhui"
        elif (start.day == date.today().day+1):
            sstday = "Demain"
        else:
            stday = start.strftime("%d/%m/%Y")
            sstday = f"le {stday}"
        sthour = start.strftime("%H:%M")
        edhour = end.strftime("%H:%M")

        ks = c.__dict__.keys()

        if 'class_name' in ks:
            print(f"    Classe: {c.class_name if 'class_name' in ks else '❓'}")

        out.append({
            "name": c.name,
            "id": c.id,
            "classroom": c.classroom,
            "start_day": sstday,
            "start_hour": sthour,
            "end_hour": edhour,
            "present": getattr(c, 'present', False)
        })

    return JSONResponse(content=out)