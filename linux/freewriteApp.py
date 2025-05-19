import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
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

        # Load fonts
        font_db = QFontDatabase()
        font_db.addApplicationFont("fonts/Lato-Regular.ttf")

        # Create a full-window widget to manage background
        self.central_widget = QWidget(self)
        self.central_widget.setProperty("dark", self.color_scheme == "dark")
        self.setCentralWidget(self.central_widget)

        # Set ContentView inside the central widget
        self.content_view = ContentView(self)
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.content_view)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to cover entire window
        self.central_widget.setLayout(layout)

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
