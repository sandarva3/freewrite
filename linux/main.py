import sys
from PyQt5.QtWidgets import QApplication
from freewriteApp import FreewriteApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("assets/style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = FreewriteApp()
    window.show()
    sys.exit(app.exec_())
