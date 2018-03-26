import persistence as p
from persistence import WorkingDay, WorkingEntry
from datetime import date
from bindings import WorkingEntryKey


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
            p.insert_working_entry(self.selected_day.id, row[WorkingEntryKey.START_TIME], row[WorkingEntryKey.END_TIME],
                                   row[WorkingEntryKey.ORDER], row[WorkingEntryKey.COMMENT])

    def add_new_working_day(self, wd: date):
        p.insert_working_day(wd)

    def load_working_entries(self, working_date: str) -> list:
        val = working_date.split("-")
        d = date(int(val[0]), int(val[1]), int(val[2]))
        wd: WorkingDay = p.find_working_day_by_date(d)
        we_list = list()
        for we in p.find_all_working_entries():
            if wd.id == we.belongs_to_day:
                we_list.append(tranform_entry_dict(we))
        return we_list


def tranform_entry_dict(entry: WorkingEntry) -> dict:
    d = dict()
    d[WorkingEntryKey.START_TIME] = entry.start_time
    d[WorkingEntryKey.END_TIME] = entry.end_time
    d[WorkingEntryKey.ORDER] = entry.order
    d[WorkingEntryKey.COMMENT] = entry.comment
    return d
