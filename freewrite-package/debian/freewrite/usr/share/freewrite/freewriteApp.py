import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QFontDatabase, QIcon
from PyQt5.QtCore import QSettings
from ContentView import ContentView

class FreewriteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Freewrite")
        self.setGeometry(100, 100, 1100, 600)
        self.setWindowIcon(QIcon("app_icons/1024-mac.png"))

        # Load color scheme from settings
        settings = QSettings("humansongs", "freewrite")
        self.color_scheme = settings.value("colorScheme", "light")
        
        # Set the dark property based on current scheme
        self.setProperty("dark", self.color_scheme == "dark")

        # Load fonts
        font_db = QFontDatabase()
        font_db.addApplicationFont("fonts/Lato-Regular.ttf")

        # Set central widget
        self.content_view = ContentView(self)
        self.setCentralWidget(self.content_view)

        # Center window
        self.center()

    def center(self):
        frame = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("assets/style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = FreewriteApp()
    window.show()
    sys.exit(app.exec_())
