import json
import re
from fastapi import FastAPI, Depends, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List 
from . import models, database, engine

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def list_events(request: Request, db: Session = Depends(database.get_db)):
    events = db.query(models.Event).all()
    return templates.TemplateResponse("index.html", {"request": request, "events": events})

@app.post("/events")
async def create_event(name: str = Form(...), db: Session = Depends(database.get_db)):
    new_event = models.Event(name=name)
    db.add(new_event)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/event/{event_id}", response_class=HTMLResponse)
async def view_event(event_id: int, request: Request, db: Session = Depends(database.get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    dances = db.query(models.Dance).filter(models.Dance.event_id == event_id).all()
    dancers = db.query(models.Dancer).filter(models.Dancer.event_id == event_id).all()
    sessions = db.query(models.Session).filter(models.Session.event_id == event_id).all()
    daily_constraints = db.query(models.DailyConstraint).filter(models.DailyConstraint.event_id == event_id).all()
    
    full_schedule = engine.calculate_full_schedule(sessions, dancers, daily_constraints)
    
    return templates.TemplateResponse("event.html", {
        "request": request, "event": event, "dances": dances,
        "dancers": dancers, "schedule": full_schedule,
        "daily_constraints": daily_constraints
    })

@app.post("/event/{event_id}/add_session")
async def add_session(
    event_id: int, 
    dance_id: int = Form(...), 
    duration: int = Form(0), 
    custom_time: str = Form(None),
    db: Session = Depends(database.get_db)
):
    new_session = models.Session(
        dance_id=dance_id, 
        duration=duration, 
        custom_time=custom_time,
        event_id=event_id
    )
    db.add(new_session)
    db.commit()
    return RedirectResponse(url=f"/event/{event_id}", status_code=303)

@app.post("/event/{event_id}/delete_session/{session_id}")
async def delete_session(event_id: int, session_id: int, db: Session = Depends(database.get_db)):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()
    return RedirectResponse(url=f"/event/{event_id}", status_code=303)

@app.post("/event/{event_id}/reorder_sessions")
async def reorder_sessions(event_id: int, payload: dict = Body(...), db: Session = Depends(database.get_db)):
    new_order = payload.get("order", [])
    for index, s_id in enumerate(new_order):
        session = db.query(models.Session).filter(models.Session.id == int(s_id)).first()
        if session:
            session.sort_order = index
    db.commit()
    return {"status": "success"}

@app.post("/event/{event_id}/add_dancer")
async def add_dancer(event_id: int, name: str = Form(...), db: Session = Depends(database.get_db)):
    new_dancer = models.Dancer(name=name, busy_times=[], event_id=event_id)
    db.add(new_dancer)
    db.commit()
    return RedirectResponse(url=f"/event/{event_id}#library", status_code=303)

@app.post("/event/{event_id}/add_dance")
async def add_dance(event_id: int, name: str = Form(...), dancer_ids: List[int] = Form([]), db: Session = Depends(database.get_db)):
    new_dance = models.Dance(name=name, member_ids=dancer_ids, event_id=event_id)
    db.add(new_dance)
    db.commit()
    return RedirectResponse(url=f"/event/{event_id}#library", status_code=303)

@app.post("/event/{event_id}/edit_dance/{dance_id}")
async def edit_dance(event_id: int, dance_id: int, name: str = Form(...), dancer_ids: List[int] = Form([]), db: Session = Depends(database.get_db)):
    db_dance = db.query(models.Dance).filter(models.Dance.id == dance_id).first()
    if db_dance:
        db_dance.name = name
        db_dance.member_ids = dancer_ids
        db.commit()
    return RedirectResponse(url=f"/event/{event_id}#library", status_code=303)

@app.post("/event/{event_id}/delete_dance/{dance_id}")
async def delete_dance(event_id: int, dance_id: int, db: Session = Depends(database.get_db)):
    # 1. Remove all sessions that were using this dance
    db.query(models.Session).filter(models.Session.dance_id == dance_id).delete()
    
    # 2. Remove the dance itself
    db_dance = db.query(models.Dance).filter(models.Dance.id == dance_id).first()
    if db_dance:
        db.delete(db_dance)
        db.commit()
    return RedirectResponse(url=f"/event/{event_id}#library", status_code=303)

@app.post("/event/{event_id}/add_daily_constraint")
async def add_daily_constraint(event_id: int, dancer_id: int = Form(...), time_range: str = Form(...), db: Session = Depends(database.get_db)):
    new_constraint = models.DailyConstraint(dancer_id=dancer_id, time_range=time_range, event_id=event_id)
    db.add(new_constraint)
    db.commit()
    return RedirectResponse(url=f"/event/{event_id}", status_code=303)

@app.post("/event/{event_id}/delete_constraint/{constraint_id}")
async def delete_constraint(event_id: int, constraint_id: int, db: Session = Depends(database.get_db)):
    constraint = db.query(models.DailyConstraint).filter(models.DailyConstraint.id == constraint_id).first()
    if constraint:
        db.delete(constraint)
        db.commit()
    return RedirectResponse(url=f"/event/{event_id}", status_code=303)

@app.post("/event/{event_id}/edit_busy/{dancer_id}")
async def edit_busy(event_id: int, dancer_id: int, times_str: str = Form(""), db: Session = Depends(database.get_db)):
    dancer = db.query(models.Dancer).filter(models.Dancer.id == dancer_id).first()
    if dancer:
        matches = re.findall(r"(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})", times_str)
        dancer.busy_times = matches
        db.commit()
    return RedirectResponse(url=f"/event/{event_id}#library", status_code=303)

@app.post("/event/{event_id}/rename_dancer/{dancer_id}")
async def rename_dancer(event_id: int, dancer_id: int, new_name: str = Form(...), db: Session = Depends(database.get_db)):
    dancer = db.query(models.Dancer).filter(models.Dancer.id == dancer_id).first()
    if dancer:
        dancer.name = new_name
        db.commit()
    return RedirectResponse(url=f"/event/{event_id}#library", status_code=303)

@app.post("/event/{event_id}/clear_day")
async def clear_day(event_id: int, db: Session = Depends(database.get_db)):
    # 1. Delete all sessions for this specific event
    db.query(models.Session).filter(models.Session.event_id == event_id).delete()
    
    # 2. Delete all daily constraints (the yellow box conflicts)
    db.query(models.DailyConstraint).filter(models.DailyConstraint.event_id == event_id).delete()
    
    db.commit()
    return RedirectResponse(url=f"/event/{event_id}", status_code=303)