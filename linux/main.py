import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QLocale

# Add BASE_DIR for absolute paths
BASE_DIR = "/usr/share/freewrite"

from freewriteApp import FreewriteApp
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Force LTR locale (English, US)
    locale = QLocale(QLocale.English, QLocale.UnitedStates)
    QLocale.setDefault(locale)
    # Use absolute path here
    with open(os.path.join(BASE_DIR, "assets/style.qss"), "r") as f:
        app.setStyleSheet(f.read())
    window = FreewriteApp()
    window.show()
    sys.exit(app.exec_())
