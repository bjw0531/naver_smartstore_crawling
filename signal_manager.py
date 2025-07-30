from PyQt5.QtCore import pyqtSignal, QObject

class SignalManager(QObject):
    image_done_signal = pyqtSignal()
    text_done_signal = pyqtSignal()
    log_message_signal = pyqtSignal(str)
    user_stop_signal = pyqtSignal()
    image_data_signal = pyqtSignal(list)
