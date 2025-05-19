import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QLocale# Add QLocale import
from freewriteApp import FreewriteApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Force LTR locale (English, US)
    locale = QLocale(QLocale.English, QLocale.UnitedStates)
    QLocale.setDefault(locale)
    with open("assets/style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = FreewriteApp()
    window.show()
    sys.exit(app.exec_())
