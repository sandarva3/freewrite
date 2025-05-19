import os
import uuid
import re
import random  # Added for random placeholder selection
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton,
    QScrollArea, QLabel, QMenu, QFileDialog
)
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QPainter, QTextDocument, QTextOption  # Added QTextOption
from PyQt5.QtCore import Qt, QTimer, QSettings, QUrl, QSize
from PyQt5.Qt import QDesktopServices
from PyQt5.QtWidgets import QApplication
import markdown
import PyPDF2
from PyPDF2 import PdfWriter

class HumanEntry:
    def __init__(self, id, date, filename, preview_text):
        self.id = id
        self.date = date
        self.filename = filename
        self.preview_text = preview_text

    @staticmethod
    def create_new():
        id = uuid.uuid4()
        now = datetime.now()
        date_formatter = "%Y-%m-%d-%H-%M-%S"
        date_string = now.strftime(date_formatter)
        display_formatter = "%b %d"
        display_date = now.strftime(display_formatter)
        return HumanEntry(
            id=id,
            date=display_date,
            filename=f"[{id}]-[{date_string}].md",
            preview_text=""
        )

class ContentView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries = []
        self.text = "\n\n"
        self.is_fullscreen = False
        self.selected_font = "Lato-Regular"
        self.current_random_font = ""
        self.time_remaining = 900
        self.timer_is_running = False
        self.is_hovering_timer = False
        self.is_hovering_fullscreen = False
        self.hovered_font = None
        self.is_hovering_size = False
        self.font_size = 18
        self.bottom_nav_opacity = 1.0
        self.is_hovering_bottom_nav = False
        self.selected_entry_id = None
        self.hovered_entry_id = None
        self.is_hovering_chat = False
        self.showing_chat_menu = False
        self.is_hovering_new_entry = False
        self.is_hovering_clock = False
        self.showing_sidebar = False
        self.hovered_trash_id = None
        self.hovered_export_id = None
        self.color_scheme = QSettings("humansongs", "freewrite").value("colorScheme", "light")
        self.is_hovering_theme_toggle = False
        self.did_copy_prompt = False
        self.placeholder_text = ""
        self.available_fonts = ["Lato-Regular", "Arial", "Times New Roman"]  # Simplified
        self.font_sizes = [16, 18, 20, 22, 24, 26]
        self.placeholder_options = [
            "\n\nBegin writing", "\n\nPick a thought and go", "\n\nStart typing",
            "\n\nWhat's on your mind", "\n\nJust start", "\n\nType your first thought",
            "\n\nStart with one sentence", "\n\nJust say it"
        ]
        self.documents_directory = os.path.join(os.path.expanduser("~"), "information", "freewrite_notes")
        self.ai_chat_prompt = """
below is my journal entry. wyt? talk through it with me like a friend. don't therpaize me and give me a whole breakdown, don't repeat my thoughts with headings. really take all of this, and tell me back stuff truly as if you're an old homie.

Keep it casual, dont say yo, help me make new connections i don't see, comfort, validate, challenge, all of it. dont be afraid to say a lot. format with markdown headings if needed.

do not just go through every single thing i say, and say it back to me. you need to proccess everythikng is say, make connections i don't see it, and deliver it all back to me as a story that makes me feel what you think i wanna feel. thats what the best therapists do.

ideally, you're style/tone should sound like the user themselves. it's as if the user is hearing their own tone but it should still feel different, because you have different things to say and don't just repeat back they say.

else, start by saying, "hey, thanks for showing me this. my thoughts:"

my entry:
"""
        self.claude_prompt = """
Take a look at my journal entry below. I'd like you to analyze it and respond with deep insight that feels personal, not clinical.
Imagine you're not just a friend, but a mentor who truly gets both my tech background and my psychological patterns. I want you to uncover the deeper meaning and emotional undercurrents behind my scattered thoughts.
Keep it casual, dont say yo, help me make new connections i don't see, comfort, validate, challenge, all of it. dont be afraid to say a lot. format with markdown headings if needed.
Use vivid metaphors and powerful imagery to help me see what I'm really building. Organize your thoughts with meaningful headings that create a narrative journey through my ideas.
Don't just validate my thoughts - reframe them in a way that shows me what I'm really seeking beneath the surface. Go beyond the product concepts to the emotional core of what I'm trying to solve.
Be willing to be profound and philosophical without sounding like you're giving therapy. I want someone who can see the patterns I can't see myself and articulate them in a way that feels like an epiphany.
Start with 'hey, thanks for showing me this. my thoughts:' and then use markdown headings to structure your response.

Here's my journal entry:
"""
        self.init_ui()
        self.load_existing_entries()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_widget = QWidget()
        self.main_layout.addWidget(self.main_widget)
        self.main_v_layout = QVBoxLayout(self.main_widget)
        # Text Editor with proper alignment configuration
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(self.text)
        self.text_edit.setFont(QFont(self.selected_font, self.font_size))
        # Critical fixes for text direction
        document = self.text_edit.document()
        option = QTextOption()
        option.setAlignment(Qt.AlignLeft)
        option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        option.setTextDirection(Qt.LeftToRight)
        document.setDefaultTextOption(option)
        # Set property for theme
        is_dark = self.color_scheme == "dark"
        if hasattr(self, 'parent') and self.parent() is not None:
            self.parent().setProperty("dark", is_dark)
        self.text_edit.setProperty("dark", is_dark)
        self.text_edit.textChanged.connect(self.on_text_changed)
        self.fix_text_direction()
        self.main_v_layout.addWidget(self.text_edit)

        # Bottom Navigation
        self.bottom_nav = QWidget()
        self.bottom_nav.setObjectName("bottomNav")
        self.bottom_nav.setProperty("dark", is_dark)
        self.bottom_nav_layout = QHBoxLayout(self.bottom_nav)
        self.font_buttons = QWidget()
        self.font_buttons_layout = QHBoxLayout(self.font_buttons)
        
        # Font Size Button
        self.font_size_btn = QPushButton(f"{int(self.font_size)}px")
        self.font_size_btn.setProperty("dark", is_dark)
        self.font_size_btn.clicked.connect(self.change_font_size)
        self.font_buttons_layout.addWidget(self.font_size_btn)
        
        # Font Buttons
        for font in ["Lato", "Arial", "System", "Serif", "Random"]:
            btn = QPushButton(font)
            btn.setProperty("dark", is_dark)
            btn.clicked.connect(lambda checked, f=font: self.change_font(f))
            self.font_buttons_layout.addWidget(btn)
        self.bottom_nav_layout.addWidget(self.font_buttons)
        self.bottom_nav_layout.addStretch()
        
        #ensure that cursor doesn't move above third ine
        self.text_edit.cursorPositionChanged.connect(self.enforce_minimum_cursor_position)

        # Utility Buttons
        self.utility_buttons = QWidget()
        self.utility_buttons_layout = QHBoxLayout(self.utility_buttons)
        self.timer_btn = QPushButton("15:00")
        self.timer_btn.setProperty("dark", is_dark)
        self.timer_btn.clicked.connect(self.toggle_timer)
        self.utility_buttons_layout.addWidget(self.timer_btn)
        
        self.chat_btn = QPushButton("Chat")
        self.chat_btn.setProperty("dark", is_dark)
        self.chat_btn.clicked.connect(self.show_chat_menu)
        self.utility_buttons_layout.addWidget(self.chat_btn)
        
        self.fullscreen_btn = QPushButton("Fullscreen")
        self.fullscreen_btn.setProperty("dark", is_dark)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.utility_buttons_layout.addWidget(self.fullscreen_btn)
        
        self.new_entry_btn = QPushButton("New Entry")
        self.new_entry_btn.setProperty("dark", is_dark)
        self.new_entry_btn.clicked.connect(self.create_new_entry)
        self.utility_buttons_layout.addWidget(self.new_entry_btn)
        
        self.theme_toggle_btn = QPushButton("Toggle Theme")
        self.theme_toggle_btn.setProperty("dark", is_dark)
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        self.utility_buttons_layout.addWidget(self.theme_toggle_btn)
        
        self.history_btn = QPushButton("History")
        self.history_btn.setProperty("dark", is_dark)
        self.history_btn.clicked.connect(self.toggle_sidebar)
        self.utility_buttons_layout.addWidget(self.history_btn)
        
        self.bottom_nav_layout.addWidget(self.utility_buttons)
        self.main_v_layout.addWidget(self.bottom_nav)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setProperty("dark", is_dark)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.history_btn = QPushButton("History")
        self.history_btn.setProperty("dark", is_dark)
        self.history_btn.clicked.connect(self.open_documents_directory)
        self.sidebar_layout.addWidget(self.history_btn)
        
        self.entries_scroll = QScrollArea()
        self.entries_widget = QWidget()
        self.entries_layout = QVBoxLayout(self.entries_widget)
        self.entries_scroll.setWidget(self.entries_widget)
        self.entries_scroll.setWidgetResizable(True)
        self.sidebar_layout.addWidget(self.entries_scroll)
        self.main_layout.addWidget(self.sidebar)
        self.sidebar.setVisible(False)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        # Save Timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_current_entry)
        self.save_timer.start(1000)


    def enforce_minimum_cursor_position(self):
        """Ensure cursor never goes above the third line (after the two newlines)"""
        cursor = self.text_edit.textCursor()
        current_position = cursor.position()
    
        # Minimum position is after the initial "\n\n" (position 2)
        if current_position < 2:
            cursor.setPosition(2)
            self.text_edit.setTextCursor(cursor)

    def keyPressEvent(self, event):
        """Override keyPressEvent to prevent deleting the initial \\n\\n"""
        cursor = self.text_edit.textCursor()
        current_position = cursor.position()
        
        # Prevent backspace from deleting the initial \n\n
        if event.key() == Qt.Key_Backspace and current_position <= 2:
            return  # Do nothing, prevent the backspace
        
        # Let the parent handle other key events
        super().keyPressEvent(event)

    def change_font_size(self):
        current_index = self.font_sizes.index(self.font_size)
        self.font_size = self.font_sizes[(current_index + 1) % len(self.font_sizes)]
        self.font_size_btn.setText(f"{int(self.font_size)}px")
        self.text_edit.setFont(QFont(self.selected_font, self.font_size))

    def change_font(self, font):
        if font == "Random":
            self.selected_font = self.available_fonts[random.randint(0, len(self.available_fonts) - 1)]
            self.current_random_font = self.selected_font
        else:
            self.selected_font = {"Lato": "Lato-Regular", "Arial": "Arial", "System": "Arial", "Serif": "Times New Roman"}[font]
            self.current_random_font = ""
        self.text_edit.setFont(QFont(self.selected_font, self.font_size))

    def toggle_timer(self):
        self.timer_is_running = not self.timer_is_running
        if not self.timer_is_running:
            self.time_remaining = 900
        self.update_timer_button()

    def update_timer(self):
        if self.timer_is_running and self.time_remaining > 0:
            self.time_remaining -= 1
            self.update_timer_button()
        elif self.time_remaining == 0:
            self.timer_is_running = False
            self.bottom_nav_opacity = 1.0

    def update_timer_button(self):
        if not self.timer_is_running and self.time_remaining == 900:
            self.timer_btn.setText("15:00")
        else:
            minutes = self.time_remaining // 60
            seconds = self.time_remaining % 60
            self.timer_btn.setText(f"{minutes}:{seconds:02d}")

    def select_entry(self, entry):
        if self.selected_entry_id:
            self.save_current_entry()
        self.selected_entry_id = entry.id
        self.load_entry(entry)


    def update_entries_display(self):
        # Clear existing widgets
        while self.entries_layout.count():
            child = self.entries_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Check current theme
        is_dark = self.color_scheme == "dark"
        
        # Remove spacing between entries
        self.entries_layout.setSpacing(0)
        self.entries_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add entries to the sidebar
        for entry in self.entries:
            entry_widget = QWidget()
            entry_widget.setProperty("dark", is_dark)
            entry_widget.setObjectName("entryItem")  # Add an object name for styling
            
            entry_layout = QHBoxLayout(entry_widget)
            entry_layout.setContentsMargins(8, 2, 8, 2)  # Reduce internal margins
            
            # Entry title/preview
            label = QLabel(f"{entry.date}: {entry.preview_text}")
            label.setProperty("dark", is_dark)
            label.setWordWrap(True)
            entry_layout.addWidget(label, 1)
            
            # Delete button
            delete_btn = QPushButton("🗑️")
            delete_btn.setProperty("dark", is_dark)
            delete_btn.setMaximumWidth(30)
            delete_btn.clicked.connect(lambda checked, e=entry: self.delete_entry(e))
            entry_layout.addWidget(delete_btn)
            
            # Export button
            export_btn = QPushButton("📤")
            export_btn.setProperty("dark", is_dark)
            export_btn.setMaximumWidth(30)
            export_btn.clicked.connect(lambda checked, e=entry: self.export_entry_as_pdf(e))
            entry_layout.addWidget(export_btn)
            
            self.entries_layout.addWidget(entry_widget)
            
            # Make entry clickable to load
            entry_widget.mousePressEvent = lambda event, e=entry: self.select_entry(e)
        
        # Set background for entries widget to match theme
        self.entries_widget.setProperty("dark", is_dark)
        self.entries_widget.setObjectName("entriesContainer")
        self.entries_widget.setContentsMargins(0, 0, 0, 0)
        
        # Also set properties for the scroll area
        self.entries_scroll.setProperty("dark", is_dark)
        self.entries_scroll.setObjectName("entriesScroll")
        self.entries_scroll.setContentsMargins(0, 0, 0, 0)
        
        # Update the sidebar entries widget size
        self.entries_widget.adjustSize()

    def show_chat_menu(self):
        menu = QMenu(self.chat_btn)
        trimmed_text = self.text_edit.toPlainText().strip()
        print(f"Trimmed text length: {len(trimmed_text)}")
        gpt_full_text = self.ai_chat_prompt + "\n\n" + trimmed_text
        claude_full_text = self.claude_prompt + "\n\n" + trimmed_text
        gpt_url_length = len("https://chat.openai.com/?m=" + gpt_full_text)
        claude_url_length = len("https://claude.ai/new?q=" + claude_full_text)
        print(f"GPT URL length: {gpt_url_length}, Claude URL length: {claude_url_length}")
        
        if gpt_url_length > 6000 or claude_url_length > 6000:
            print("Adding 'Copy Prompt' action due to long URL")
            menu.addAction("Copy Prompt", self.copy_prompt_to_clipboard)
        elif len(trimmed_text) < 350:
            print("Adding 'Write more first' action due to short text")
            menu.addAction("Write more first")
        else:
            print("Adding ChatGPT, Claude, and Copy Prompt actions")
            menu.addAction("ChatGPT", self.open_chat_gpt)
            menu.addAction("Claude", self.open_claude)
            menu.addAction("Copy Prompt", self.copy_prompt_to_clipboard)
        menu.exec_(self.chat_btn.mapToGlobal(self.chat_btn.rect().bottomLeft()))

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        # Call showFullScreen/showNormal on the parent QMainWindow
        if self.is_fullscreen:
            self.parent().showFullScreen()
        else:
            self.parent().showNormal()
        self.fullscreen_btn.setText("Minimize" if self.is_fullscreen else "Fullscreen")

    


    def restore_font_size_on_toggle(self, font_size_before_toggle):
        current_index = self.font_sizes.index(self.font_size)
        self.font_size = self.font_sizes[(current_index + 1) % len(self.font_sizes)]
        self.font_size_btn.setText(f"{int(self.font_size)}px")
        self.text_edit.setFont(QFont(self.selected_font, self.font_size))


    def toggle_theme(self):
        # Store current font size before theme change
        current_font_size = self.font_size
        
        self.color_scheme = "dark" if self.color_scheme == "light" else "light"
        QSettings("humansongs", "freewrite").setValue("colorScheme", self.color_scheme)
        
        # Apply theme to all widgets
        is_dark = self.color_scheme == "dark"
        
        # Apply property to parent main window
        if hasattr(self, 'parent') and self.parent() is not None:
            self.parent().setProperty("dark", is_dark)
            self.parent().style().unpolish(self.parent())
            self.parent().style().polish(self.parent())
        
        # Set property for all widgets
        for widget in [self.text_edit, self.bottom_nav, self.sidebar, self.font_size_btn, 
                      self.timer_btn, self.chat_btn, self.fullscreen_btn, 
                      self.new_entry_btn, self.theme_toggle_btn, self.history_btn]:
            if widget:
                widget.setProperty("dark", is_dark)
                widget.style().unpolish(widget)
                widget.style().polish(widget)
        
        # Apply to all buttons in font_buttons
        for i in range(self.font_buttons_layout.count()):
            widget = self.font_buttons_layout.itemAt(i).widget()
            if widget:
                widget.setProperty("dark", is_dark)
                widget.style().unpolish(widget)
                widget.style().polish(widget)
        
        # Apply to all buttons in utility_buttons
        for i in range(self.utility_buttons_layout.count()):
            widget = self.utility_buttons_layout.itemAt(i).widget()
            if widget:
                widget.setProperty("dark", is_dark)
                widget.style().unpolish(widget)
                widget.style().polish(widget)
        
        # Apply to all widgets in entries_layout
        for i in range(self.entries_layout.count()):
            entry_widget = self.entries_layout.itemAt(i).widget()
            if entry_widget:
                entry_widget.setProperty("dark", is_dark)
                entry_widget.style().unpolish(entry_widget)
                entry_widget.style().polish(entry_widget)
                
                # Apply to child widgets in the entry
                entry_layout = entry_widget.layout()
                for j in range(entry_layout.count()):
                    child_widget = entry_layout.itemAt(j).widget()
                    if child_widget:
                        child_widget.setProperty("dark", is_dark)
                        child_widget.style().unpolish(child_widget)
                        child_widget.style().polish(child_widget)
        
        # Restore font size
        self.restore_font_size_on_toggle(current_font_size)
        self.font_size_btn.setText(f"{int(self.font_size)}px")
        self.text_edit.setFont(QFont(self.selected_font, self.font_size))
        
        # Refresh the styles
        self.update_styles()
        
        # Update entries display to ensure new widgets have the theme
        self.update_entries_display()

# Replace the update_styles method
    def update_styles(self):
        try:
            with open("assets/style.qss", "r") as f:
                style_content = f.read()
                QApplication.instance().setStyleSheet(style_content)
        except Exception as e:
            print(f"Error loading styles: {e}")

    def toggle_sidebar(self):
        self.showing_sidebar = not self.showing_sidebar
        self.sidebar.setVisible(self.showing_sidebar)

    def open_documents_directory(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.documents_directory))


    def fix_text_direction(self):
        """Fix text direction to ensure horizontal writing"""
        cursor = self.text_edit.textCursor()
        # Set text direction explicitly
        format = cursor.charFormat()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(format)
        # Ensure document options are correct
        document = self.text_edit.document()
        option = QTextOption()
        option.setAlignment(Qt.AlignLeft)
        option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        option.setTextDirection(Qt.LeftToRight)
        document.setDefaultTextOption(option)
    # Force layout direction
        self.text_edit.setLayoutDirection(Qt.LeftToRight)

    def on_text_changed(self):
        """Handle text changes and ensure proper formatting"""
        text = self.text_edit.toPlainText()
        cursor_position = self.text_edit.textCursor().position()
        # Only prepend \n\n if the text doesn't already start with it
        if not text.startswith("\n\n") and text.strip():
            text = "\n\n" + text.lstrip("\n")
            self.text_edit.blockSignals(True)  # Prevent recursive signals
            self.text_edit.setPlainText(text)
            # Restore cursor position (adjust for added characters)
            cursor = self.text_edit.textCursor()
            new_position = max(2, cursor_position + 2)
            cursor.setPosition(min(new_position, len(text)))
            self.text_edit.setTextCursor(cursor)
            # Fix text direction after text change
            self.fix_text_direction()
            self.text_edit.blockSignals(False)
        self.text = text
        self.save_current_entry()

    def save_current_entry(self):
        if self.selected_entry_id:
            entry = next((e for e in self.entries if e.id == self.selected_entry_id), None)
            if entry:
                self.save_entry(entry)

    def save_entry(self, entry):
        os.makedirs(self.documents_directory, exist_ok=True)
        file_path = os.path.join(self.documents_directory, entry.filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.text)
            self.update_preview_text(entry)
        except Exception as e:
            print(f"Error saving entry: {e}")

    def load_entry(self, entry):
        file_path = os.path.join(self.documents_directory, entry.filename)
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    self.text = f.read()
                    self.text_edit.setPlainText(self.text)
                    cursor = self.text_edit.textCursor()
                    cursor.movePosition(QTextCursor.End)
                    self.text_edit.setTextCursor(cursor)
        except Exception as e:
            print(f"Error loading entry: {e}")

    def create_new_entry(self):
        new_entry = HumanEntry.create_new()
        self.entries.insert(0, new_entry)
        self.selected_entry_id = new_entry.id
        if len(self.entries) == 1:
            try:
                with open("assets/default.md", "r", encoding="utf-8") as f:
                    self.text = "\n\n" + f.read()
            except:
                self.text = "\n\n"
            self.save_entry(new_entry)
            self.update_preview_text(new_entry)
        else:
            self.text = "\n\n"
            self.placeholder_text = random.choice(self.placeholder_options)
            self.save_entry(new_entry)
        self.text_edit.setPlainText(self.text)
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_edit.setTextCursor(cursor)
        self.update_entries_display()

    def update_preview_text(self, entry):
        file_path = os.path.join(self.documents_directory, entry.filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().replace("\n", " ").strip()
                entry.preview_text = content[:30] + "..." if len(content) > 30 else content
        except Exception as e:
            print(f"Error updating preview: {e}")

    def open_chat_gpt(self):
        trimmed_text = self.text.strip()
        full_text = self.ai_chat_prompt + "\n\n" + trimmed_text
        encoded_text = QUrl.toPercentEncoding(full_text)
        url = QUrl(f"https://chat.openai.com/?m={encoded_text}")
        QDesktopServices.openUrl(url)

    def open_claude(self):
        trimmed_text = self.text.strip()
        full_text = self.claude_prompt + "\n\n" + trimmed_text
        encoded_text = QUrl.toPercentEncoding(full_text)
        url = QUrl(f"https://claude.ai/new?q={encoded_text}")
        QDesktopServices.openUrl(url)

    def copy_prompt_to_clipboard(self):
        trimmed_text = self.text.strip()
        full_text = self.ai_chat_prompt + "\n\n" + trimmed_text
        QCoreApplication.instance().clipboard().setText(full_text)
        self.did_copy_prompt = True

    def delete_entry(self, entry):
        file_path = os.path.join(self.documents_directory, entry.filename)
        try:
            os.remove(file_path)
            self.entries = [e for e in self.entries if e.id != entry.id]
            if self.selected_entry_id == entry.id:
                if self.entries:
                    self.selected_entry_id = self.entries[0].id
                    self.load_entry(self.entries[0])
                else:
                    self.create_new_entry()
            self.update_entries_display()
        except Exception as e:
            print(f"Error deleting entry: {e}")

    def export_entry_as_pdf(self, entry):
        if self.selected_entry_id == entry.id:
            self.save_entry(entry)
        file_path = os.path.join(self.documents_directory, entry.filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            suggested_filename = self.extract_title_from_content(content, entry.date) + ".pdf"
            file_dialog = QFileDialog()
            file_dialog.setDefaultSuffix("pdf")
            file_dialog.selectFile(suggested_filename)
            if file_dialog.exec_():
                pdf_path = file_dialog.selectedFiles()[0]
                self.create_pdf_from_text(content, pdf_path)
        except Exception as e:
            print(f"Error exporting PDF: {e}")

    def extract_title_from_content(self, content, date):
        trimmed = content.strip()
        if not trimmed:
            return f"Entry {date}"
        words = [w.strip(".,!?;:\"'()[]{}<>").lower() for w in trimmed.replace("\n", " ").split() if w.strip(".,!?;:\"'()[]{}<>")]
        if len(words) >= 4:
            return "-".join(words[:4])
        return "-".join(words) if words else f"Entry {date}"

    def create_pdf_from_text(self, text, output_path):
        writer = PdfWriter()
        page = writer.add_page()
        page.mediabox = [0, 0, 612, 792]
        page.trimbox = [72, 72, 612 - 72, 792 - 72]
        text_doc = QTextDocument()
        text_doc.setDefaultFont(QFont(self.selected_font, self.font_size))
        text_doc.setPlainText(text.strip())
        painter = QPainter()
        painter.begin(page)
        text_doc.drawContents(painter)
        painter.end()
        with open(output_path, "wb") as f:
            writer.write(f)

    def load_existing_entries(self):
        os.makedirs(self.documents_directory, exist_ok=True)
        try:
            files = [f for f in os.listdir(self.documents_directory) if f.endswith(".md")]
            entries_with_dates = []
            for file in files:
                match_uuid = re.search(r"\[(.*?)\]", file)
                match_date = re.search(r"\[(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})\]", file)
                if match_uuid and match_date:
                    uuid_str = match_uuid.group(1)
                    date_str = match_date.group(1)
                    try:
                        file_date = datetime.strptime(date_str, "%Y-%m-%d-%H-%M-%S")
                        with open(os.path.join(self.documents_directory, file), "r", encoding="utf-8") as f:
                            content = f.read().replace("\n", " ").strip()
                            preview = content[:30] + "..." if len(content) > 30 else content
                            display_date = file_date.strftime("%b %d")
                            entries_with_dates.append((
                                HumanEntry(uuid.UUID(uuid_str), display_date, file, preview),
                                file_date
                            ))
                    except:
                        continue
            self.entries = [e[0] for e in sorted(entries_with_dates, key=lambda x: x[1], reverse=True)]
            today = date.today()
            has_empty_entry_today = any(
                e.date == today.strftime("%b %d") and not e.preview_text for e in self.entries
            )
            has_only_welcome = len(self.entries) == 1 and "Welcome to Freewrite" in (open(os.path.join(self.documents_directory, self.entries[0].filename), "r", encoding="utf-8").read() if self.entries else "")
            if not self.entries:
                self.create_new_entry()
            elif not has_empty_entry_today and not has_only_welcome:
                self.create_new_entry()
            else:
                for entry in self.entries:
                    if entry.date == today.strftime("%b %d") and not entry.preview_text:
                        self.selected_entry_id = entry.id
                        self.load_entry(entry)
                        break
                    elif has_only_welcome:
                        self.selected_entry_id = self.entries[0].id
                        self.load_entry(self.entries[0])
                        break
            self.update_entries_display()
        except Exception as e:
            print(f"Error loading entries: {e}")
            self.create_new_entry()
