from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5 import QtTest
import datetime
class GetDateTimeThreaded(QObject):
    def __init__(self, signal_to_emit, parent=None):
        super().__init__(parent)
        self.signal_to_emit = signal_to_emit
        self.running = True

    @pyqtSlot()
    def executeThread( self ):
        while self.running:
            # GET DATE AND SET LABEL
            now = datetime.datetime.now()
            # dd/mm/YY H:M:S
            date = now.strftime("%m/%d/%Y")
            self.signal_to_emit.emit('dateLabel', str(date))

            # GET TIME AND SET LABEL
            now = datetime.datetime.now()
            date = now.strftime("%I:%M:%S %p")
            self.signal_to_emit.emit('timeLabel', str(date))

            QtTest.QTest.qWait(1000)