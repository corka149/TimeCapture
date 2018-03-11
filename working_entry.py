from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from datetime import time


Base = declarative_base()
engine = create_engine("sqlite:///timecapture.db")
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)


class WorkingEntry(Base):
    __tablename__ = "WORKING_ENTRY"

    id = Column(Integer, primary_key=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    order = Column(String(250), nullable=False)
    comment = Column(String(1000), nullable=True)


def insert_working_entry(start_time: time, end_time: time, order: String, comment: String):
    session: Session = DBSession()
    new_entry = WorkingEntry(start_time=start_time, end_time=end_time, order=order, comment=comment)
    session.add(new_entry)
    session.commit()


def delete_working_entry(entry: WorkingEntry):
    session: Session = DBSession()
    entry = session.query(WorkingEntry).filter(WorkingEntry.id == entry.id).first()
    session.delete(entry)
    session.commit()


def update_working_entry(entry: WorkingEntry):
    session: Session = DBSession()
    tar_entry: WorkingEntry = session.query(WorkingEntry).filter(WorkingEntry.id == entry.id).first();
    tar_entry.start_time = entry.start_time
    tar_entry.end_time = entry.end_time
    tar_entry.order = entry.order
    tar_entry.comment = entry.comment
    session.commit()


def find_working_entry_by_id(id):
    session: Session = DBSession()
    return session.query(WorkingEntry).filter(WorkingEntry.id == id).first()

