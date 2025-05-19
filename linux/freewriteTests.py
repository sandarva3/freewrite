import unittest
import os
import sys
from PyQt5.QtWidgets import QApplication  # ✅ Use PyQt5
from ContentView import HumanEntry, ContentView

class FreewriteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)  # ✅ Needed before any QWidget

    def setUp(self):
        self.view = ContentView()
        self.entry = HumanEntry.create_new()

    def test_save_entry(self):
        self.view.text = "\n\nTest entry"
        self.view.save_entry(self.entry)
        file_path = os.path.join(self.view.documents_directory, self.entry.filename)
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "\n\nTest entry")

    def tearDown(self):
        file_path = os.path.join(self.view.documents_directory, self.entry.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    unittest.main()
