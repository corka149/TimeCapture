from qtpy.QtWidgets import QDialog
from UiQt.datedialog import Ui_Dialog
from datetime import date


class DateDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__dialog = Ui_Dialog()
        self.__dialog.setupUi(self)

    def get_working_date(self) -> date:
        d = self.__dialog.dateEdit_WorkingDate.date()
        return date(d.year(), d.month(), d.day())