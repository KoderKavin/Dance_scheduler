from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    date = Column(String)
    dances = relationship("Dance", back_populates="event")
    dancers = relationship("Dancer", back_populates="event")

class Dancer(Base):
    __tablename__ = "dancers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    busy_times = Column(JSON) 
    event_id = Column(Integer, ForeignKey("events.id"))
    event = relationship("Event", back_populates="dancers")

class Dance(Base):
    __tablename__ = "dances"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    member_ids = Column(JSON, default=[]) 
    event_id = Column(Integer, ForeignKey("events.id"))
    event = relationship("Event", back_populates="dances")
    sessions = relationship("Session", back_populates="dance", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    dance_id = Column(Integer, ForeignKey("dances.id"))
    duration = Column(Integer)
    is_runthrough = Column(Boolean, default=False)
    event_id = Column(Integer, ForeignKey("events.id"))
    # NEW COLUMNS FOR DRAG & DROP AND CUSTOM TIMES
    sort_order = Column(Integer, default=0)
    custom_time = Column(String, nullable=True)
    
    dance = relationship("Dance",back_populates="sessions")

class DailyConstraint(Base):
    __tablename__ = "daily_constraints"
    id = Column(Integer, primary_key=True, index=True)
    dancer_id = Column(Integer, ForeignKey("dancers.id"))
    time_range = Column(String)
    event_id = Column(Integer, ForeignKey("events.id"))
    dancer = relationship("Dancer")