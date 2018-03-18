from sqlalchemy import Column, Integer, String, Time, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from datetime import time, date

Base = declarative_base()


class WorkingEntry(Base):
    __tablename__ = "WORKING_ENTRY"

    id = Column(Integer, primary_key=True)
    belongs_to_day = Column(Integer, ForeignKey("WORKING_DAY.id"))
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
    tar_entry: WorkingEntry = session.query(WorkingEntry).filter(WorkingEntry.id == entry.id).first()
    tar_entry.start_time = entry.start_time
    tar_entry.end_time = entry.end_time
    tar_entry.order = entry.order
    tar_entry.comment = entry.comment
    session.commit()


def find_working_entry_by_id(id):
    session: Session = DBSession()
    return session.query(WorkingEntry).filter(WorkingEntry.id == id).first()


class WorkingDay(Base):
    __tablename__ = "WORKING_DAY"

    id = Column(Integer, primary_key=True)
    working_date = Column(Date, unique=True)
    start_of_work = Column(Time, nullable=False)
    planned_end_of_work = Column(Time, nullable=True)
    comment = Column(String, nullable=True)

    def __str__(self):
        return "id: {}, working_date: {}, start_of_work: {}, planned_end_of_work: {}, comment: {}" \
                .format(self.id, self.working_date, self.start_of_work, self.planned_end_of_work, self.comment)


def insert_working_day(working_date: date, start_of_work: time, planned_end_of_work: time,
                       comment: String) -> WorkingDay:
    session: Session = DBSession()
    new_entry = WorkingDay(working_date=working_date, start_of_work=start_of_work,
                           planned_end_of_work=planned_end_of_work, comment=comment)
    session.add(new_entry)
    session.commit()
    return new_entry


def delete_working_day(day: WorkingDay):
    session: Session = DBSession()
    tar_day = session.query(WorkingDay).filter(WorkingDay.id == day.id).first()
    session.delete(tar_day)
    session.commit()


def update_working_day(day: WorkingDay):
    session: Session = DBSession()
    old_day: WorkingDay = session.query(WorkingDay).filter(WorkingDay.id == day.id).first()
    old_day.working_date = day.working_date
    old_day.start_of_work = day.start_of_work
    old_day.planned_end_of_work = day.planned_end_of_work
    old_day.comment = day.comment
    session.commit()


def find_working_day_by_id(id):
    session: Session = DBSession()
    return session.query(WorkingDay).filter(WorkingDay.id == id).first()


# Don't move else it wouldn't create the correct schema!
engine = create_engine("sqlite:///timecapture.db", echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
