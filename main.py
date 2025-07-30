from ui import CrawlerApp
from PyQt5.QtWidgets import QApplication
import sys
from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()
    app = QApplication(sys.argv)
    print("Starting CrawlerApp...")
    window = CrawlerApp()
    window.start_thread()
    window.show()
    sys.exit(app.exec_())
