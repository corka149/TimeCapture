import persistence as p
from persistence import WorkingDay, WorkingEntry
from datetime import date
from bindings import WorkingEntryKey as wee, BookingKey as bk


class TimeCaptureService:

    def __init__(self):
        self.working_days: list = p.find_all_working_days()
        self._selected_day: WorkingDay = None

    @property
    def working_dates(self):
        return [i.working_date for i in self.working_days]

    @property
    def selected_day(self):
        return self._selected_day

    @selected_day.setter
    def selected_day(self, value):
        if isinstance(value, str):
            val = value.split("-")
            if len(val) == 3:
                self._selected_day = p.find_working_day_by_date(date(int(val[0]), int(val[1]), int(val[2])))
        else:
            self._selected_day = value

    def update_working_entries(self, entries):
        p.delete_working_entry_by_working_day(self.selected_day.id)
        for row in entries:
            p.insert_working_entry(self.selected_day.id, row[wee.START_TIME], row[wee.END_TIME],
                                   row[wee.ORDER], row[wee.COMMENT])

    def add_new_working_day(self, wd: date):
        p.insert_working_day(wd)

    def load_working_entries(self, working_date: str) -> list:
        d = transform_str_to_date(working_date)
        we_list = list()
        if d is not None:
            wd: WorkingDay = p.find_working_day_by_date(d)
            for we in p.find_all_working_entries():
                if wd.id == we.belongs_to_day:
                    we_list.append(transform_entry_dict(we))
        return we_list

    def update_bookings(self, bookings):
        p.delete_booking_by_day(self.selected_day)
        for r in bookings:
            p.insert_booking(self.selected_day.id, r[bk.ORDER], r[bk.HOURS], r[bk.BOOKED], r[bk.LOGGED], r[bk.COMMENT])

    def load_bookings(self, working_date: str):
        d = transform_str_to_date(working_date)
        bookings = list()
        if d is not None:
            wd: WorkingDay = p.find_working_day_by_date(d)
            bookings = p.find_booking_by_day(wd)
        return bookings


def transform_entry_dict(entry: WorkingEntry) -> dict:
    d = dict()
    d[wee.START_TIME] = entry.start_time
    d[wee.END_TIME] = entry.end_time
    d[wee.ORDER] = entry.order
    d[wee.COMMENT] = entry.comment
    return d


def transform_str_to_date(wd: str) -> date:
    val = wd.split("-")
    if len(val) == 3:
        return date(int(val[0]), int(val[1]), int(val[2]))
    else:
        return None