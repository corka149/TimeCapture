import persistence as p
from persistence import WorkingDay, WorkingEntry
from datetime import date


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

    def updates_working_entries(self, entries):
        p.delete_working_entry_by_working_day(self.selected_day.id)
        for row in entries:
            p.insert_working_entry(self.selected_day.working_date, row["start_time"], row["end_time"], row["order"],
                                   row["comment"])

    def add_new_working_day(self, wd: date):
        p.insert_working_day(wd)
