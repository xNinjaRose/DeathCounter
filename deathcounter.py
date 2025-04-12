import os
import sys
import sqlite3
import hashlib
import pygame
import re
from datetime import datetime  # For timestamps
from pynput import keyboard as pynput_keyboard
from pynput import mouse as pynput_mouse
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QInputDialog, QMessageBox, QDialog, QFormLayout, QLineEdit,
    QTextEdit, QScrollArea  # For history window
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class DeathCounter:
    def __init__(self, count=0):
        self._deaths = count

    @property
    def deaths(self):
        return self._deaths

    def increment(self):
        self._deaths += 1
        return self._deaths

    def decrement(self):
        self._deaths = max(0, self._deaths - 1)
        return self._deaths

    def reset(self):
        self._deaths = 0
        return self._deaths

class HotkeyDialog(QDialog):
    def __init__(self, parent=None, current_hotkeys=None):
        super().__init__(parent)
        self.setWindowTitle("Set Hotkeys")
        self.hotkeys = current_hotkeys or {"increment": "+", "decrement": "-"}
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.setLayout(layout)

        self.inc_input = QLineEdit(self.hotkeys["increment"])
        self.dec_input = QLineEdit(self.hotkeys["decrement"])

        layout.addRow("Increment Hotkey or Mouse Button:", self.inc_input)
        layout.addRow("Decrement Hotkey or Mouse Button:", self.dec_input)
        layout.addRow(QLabel("Examples: i, ctrl+i, mouse4, left, right. For MMO mice, try mouse4, mouse5, or button4."))

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)

    def get_hotkeys(self):
        return {
            "increment": self.inc_input.text().strip(),
            "decrement": self.dec_input.text().strip()
        }

class HistoryWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Counter History")
        self.setFixedSize(400, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Scrollable text area for history
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setStyleSheet("font-size: 14px; padding: 5px; background-color: #f0f0f0; color: #333;")
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.history_text)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("font-size: 14px; padding: 8px;")
        layout.addWidget(close_button)

    def set_history(self, history):
        # Format the history entries
        formatted_history = ""
        for event in history:
            timestamp, event_type, details = event
            formatted_history += f"[{timestamp}] {event_type}: {details}\n"
        self.history_text.setText(formatted_history)

class DeathCounterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.death_name = ""
        self.death_counter = None
        self.hotkeys = {"increment": "+", "decrement": "-"}
        self.name_color = "#000000"
        self.count_color = "#ffc743"
        self.theme = "light"  # Default theme
        self.keyboard_listener = None
        self.mouse_listener = None
        self.paused = False
        self.green_screen_active = False
        pygame.mixer.init()
        self.name_label = QLabel("Death Counter:")
        self.count_label = QLabel("0")
        self.init_ui()
        self.load_data()
        self.update_display()
        self.setup_hotkeys()

    def init_ui(self):
        self.setWindowTitle("Death Counter")
        self.setFixedSize(400, 600)
        self.setGeometry(100, 100, 400, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.counter_widget = QWidget()
        self.counter_widget.setStyleSheet("background-color: #00FF00;")
        self.counter_widget.setMinimumHeight(150)
        counter_layout = QVBoxLayout()
        self.counter_widget.setLayout(counter_layout)

        self.name_label.setStyleSheet(f"""
            font-family: 'Segoe UI Black';
            font-size: 48px;
            color: {self.name_color};
            background-color: transparent;
        """)
        self.name_label.setAlignment(Qt.AlignCenter)
        counter_layout.addWidget(self.name_label)

        counter_layout.addSpacing(10)

        self.count_label.setStyleSheet(f"""
            font-family: 'Segoe UI Black';
            font-size: 48px;
            color: {self.count_color};
            background-color: transparent;
        """)
        self.count_label.setAlignment(Qt.AlignCenter)
        counter_layout.addWidget(self.count_label)

        self.counter_widget.show()
        self.layout.addWidget(self.counter_widget)

        self.layout.addSpacing(-15)

        self.button_layout = QHBoxLayout()
        self.inc_button = QPushButton("+")
        self.inc_button.clicked.connect(self.increment_count)
        self.button_layout.addWidget(self.inc_button)

        self.dec_button = QPushButton("-")
        self.dec_button.clicked.connect(self.decrement_count)
        self.button_layout.addWidget(self.dec_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_count)
        self.button_layout.addWidget(self.reset_button)

        self.button_layout_widget = QWidget()
        self.button_layout_widget.setLayout(self.button_layout)
        self.layout.addWidget(self.button_layout_widget)

        self.layout.addSpacing(10)

        self.name_button = QPushButton("Change Counter Name")
        self.name_button.clicked.connect(self.change_name)
        self.layout.addWidget(self.name_button)

        self.hotkey_button = QPushButton("Set Hotkeys")
        self.hotkey_button.clicked.connect(self.set_hotkeys)
        self.layout.addWidget(self.hotkey_button)

        self.pause_button = QPushButton("Pause Counter")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.layout.addWidget(self.pause_button)

        self.color_button = QPushButton("Set Text Color")
        self.color_button.clicked.connect(self.set_text_color)
        self.layout.addWidget(self.color_button)

        # New button for viewing history
        self.history_button = QPushButton("View History")
        self.history_button.clicked.connect(self.view_history)
        self.layout.addWidget(self.history_button)

        # New button for toggling dark mode
        self.theme_button = QPushButton("Toggle Dark Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.layout.addWidget(self.theme_button)

        self.green_screen_button = QPushButton("Green Screen Mode")
        self.green_screen_button.clicked.connect(self.toggle_green_screen)
        self.layout.addWidget(self.green_screen_button)

        self.layout.addStretch()

        # Apply the initial theme
        self.apply_theme()

    def apply_theme(self):
        if self.theme == "dark":
            # Dark theme
            self.central_widget.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
            button_style = "font-size: 14px; padding: 8px; background-color: #444444; color: #ffffff; border: 1px solid #555555;"
            self.inc_button.setStyleSheet("font-size: 20px; padding: 10px; background-color: #444444; color: #ffffff; border: 1px solid #555555;")
            self.dec_button.setStyleSheet("font-size: 20px; padding: 10px; background-color: #444444; color: #ffffff; border: 1px solid #555555;")
            self.reset_button.setStyleSheet("font-size: 20px; padding: 10px; background-color: #444444; color: #ffffff; border: 1px solid #555555;")
        else:
            # Light theme
            self.central_widget.setStyleSheet("background-color: #f0f0f0; color: #000000;")
            button_style = "font-size: 14px; padding: 8px;"
            self.inc_button.setStyleSheet("font-size: 20px; padding: 10px;")
            self.dec_button.setStyleSheet("font-size: 20px; padding: 10px;")
            self.reset_button.setStyleSheet("font-size: 20px; padding: 10px;")

        # Apply button styles
        self.name_button.setStyleSheet(button_style)
        self.hotkey_button.setStyleSheet(button_style)
        self.pause_button.setStyleSheet(button_style if not self.paused else "background-color: red; color: white; font-size: 14px; padding: 8px;")
        self.color_button.setStyleSheet(button_style)
        self.history_button.setStyleSheet(button_style)
        self.theme_button.setStyleSheet(button_style)
        self.green_screen_button.setStyleSheet(button_style if not self.green_screen_active else "font-size: 14px; padding: 8px; background-color: #ff4444; color: white;")

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()
        self.save_data()

    def log_event(self, event_type, details):
        try:
            conn = sqlite3.connect("death_counter.db")
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO history (timestamp, event_type, details) VALUES (?, ?, ?)",
                (timestamp, event_type, details)
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error while logging event: {e}")

    def view_history(self):
        try:
            conn = sqlite3.connect("death_counter.db")
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, event_type, details FROM history ORDER BY timestamp DESC")
            history = cursor.fetchall()
            conn.close()

            history_window = HistoryWindow(self)
            history_window.set_history(history)
            history_window.exec_()
        except sqlite3.Error as e:
            print(f"Database error while fetching history: {e}")
            QMessageBox.warning(self, "Error", "Failed to load history.")

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            self.pause_button.setText("Pause Counter")
            self.setup_hotkeys()
            print("Counter resumed")
        else:
            self.paused = True
            self.pause_button.setText("Resume Counter")
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            print("Counter paused")
        self.apply_theme()  # Update button style
        self.save_data()

    def toggle_green_screen(self):
        self.green_screen_active = not self.green_screen_active
        if self.green_screen_active:
            self.green_screen_button.setText("Disable Green Screen")
            self.button_layout_widget.hide()
            self.name_button.hide()
            self.hotkey_button.hide()
            self.pause_button.hide()
            self.color_button.hide()
            self.history_button.hide()
            self.theme_button.hide()
            self.counter_widget.show()
            self.green_screen_button.show()
            self.setFixedSize(400, 600)
        else:
            self.green_screen_button.setText("Green Screen Mode")
            self.button_layout_widget.show()
            self.name_button.show()
            self.hotkey_button.show()
            self.pause_button.show()
            self.color_button.show()
            self.history_button.show()
            self.theme_button.show()
            self.green_screen_button.show()
            self.counter_widget.show()
            self.setFixedSize(400, 600)
        self.apply_theme()  # Update button style

    def compute_hash(self, name, count, inc_hotkey, dec_hotkey, name_color, count_color, theme):
        data = f"{name}:{count}:{inc_hotkey}:{dec_hotkey}:{name_color}:{count_color}:{theme}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    def load_data(self):
        try:
            conn = sqlite3.connect("death_counter.db")
            cursor = conn.cursor()
            # Create counter table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS counter (
                    name TEXT,
                    count INTEGER,
                    increment_hotkey TEXT,
                    decrement_hotkey TEXT,
                    name_color TEXT,
                    count_color TEXT,
                    theme TEXT,  -- New column for theme
                    hash TEXT,
                    paused INTEGER
                )
            """)
            # Create history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    timestamp TEXT,
                    event_type TEXT,
                    details TEXT
                )
            """)
            cursor.execute("SELECT name, count, increment_hotkey, decrement_hotkey, name_color, count_color, theme, hash, paused FROM counter")
            result = cursor.fetchone()
            if result:
                name, count, inc_hotkey, dec_hotkey, name_color, count_color, theme, stored_hash, paused = result
                if not inc_hotkey or not dec_hotkey:
                    print("Invalid hotkeys in database, resetting to defaults")
                    self.setup_new_counter()
                else:
                    computed_hash = self.compute_hash(name, count, inc_hotkey, dec_hotkey, name_color, count_color, theme)
                    if computed_hash == stored_hash:
                        self.death_name = name
                        self.death_counter = DeathCounter(count)
                        self.hotkeys["increment"] = inc_hotkey
                        self.hotkeys["decrement"] = dec_hotkey
                        self.name_color = name_color
                        self.count_color = count_color
                        self.theme = theme or "light"  # Default to light if None
                        self.paused = bool(paused)
                        if self.paused:
                            self.pause_button.setText("Resume Counter")
                        else:
                            self.pause_button.setText("Pause Counter")
                        print(f"Loaded hotkeys from DB: {self.hotkeys}, paused: {self.paused}, theme: {self.theme}")
                    else:
                        print("Data tampered, resetting to defaults")
                        self.setup_new_counter()
            else:
                print("No data in DB, setting up new counter")
                self.setup_new_counter()
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.setup_new_counter()

    def setup_new_counter(self):
        self.death_name = "Deaths"
        self.death_counter = DeathCounter(0)
        self.hotkeys = {"increment": "+", "decrement": "-"}
        self.name_color = "#000000"
        self.count_color = "#ffc743"
        self.theme = "light"
        self.paused = False
        self.save_data()
        self.update_display()

    def save_data(self):
        try:
            conn = sqlite3.connect("death_counter.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM counter")
            computed_hash = self.compute_hash(
                self.death_name,
                self.death_counter.deaths,
                self.hotkeys["increment"],
                self.hotkeys["decrement"],
                self.name_color,
                self.count_color,
                self.theme
            )
            cursor.execute(
                "INSERT INTO counter (name, count, increment_hotkey, decrement_hotkey, name_color, count_color, theme, hash, paused) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    self.death_name,
                    self.death_counter.deaths,
                    self.hotkeys["increment"],
                    self.hotkeys["decrement"],
                    self.name_color,
                    self.count_color,
                    self.theme,
                    computed_hash,
                    int(self.paused)
                )
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def update_display(self):
        self.name_label.setText(f"{self.death_name}:")
        self.name_label.setStyleSheet(f"""
            font-family: 'Segoe UI Black';
            font-size: 48px;
            color: {self.name_color};
            background-color: transparent;
        """)
        self.count_label.setText(str(self.death_counter.deaths))
        self.count_label.setStyleSheet(f"""
            font-family: 'Segoe UI Black';
            font-size: 48px;
            color: {self.count_color};
            background-color: transparent;
        """)
        self.save_data()

    def increment_count(self):
        new_count = self.death_counter.increment()
        self.log_event("Increment", f"Counter increased to {new_count}")
        self.update_display()
        try:
            pygame.mixer.music.load("ding.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Sound error: {e}")

    def decrement_count(self):
        new_count = self.death_counter.decrement()
        self.log_event("Decrement", f"Counter decreased to {new_count}")
        self.update_display()

    def reset_count(self):
        if QMessageBox.question(self, "Confirm Reset", "Are you sure you want to reset the counter?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.death_counter.reset()
            self.log_event("Reset", "Counter reset to 0")
            self.update_display()

    def set_text_color(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

        name_color, ok1 = QInputDialog.getText(
            self,
            "Set Name Color",
            "Enter hex color code for name (e.g., #000000):",
            text=self.name_color
        )
        if ok1 and name_color:
            if re.match(r'^#[0-9A-Fa-f]{6}$', name_color):
                self.name_color = name_color
            else:
                QMessageBox.warning(self, "Invalid Color", "Please enter a valid hex color code (e.g., #000000).")
                self.setup_hotkeys()
                return

        count_color, ok2 = QInputDialog.getText(
            self,
            "Set Counter Color",
            "Enter hex color code for counter (e.g., #ffc743):",
            text=self.count_color
        )
        if ok2 and count_color:
            if re.match(r'^#[0-9A-Fa-f]{6}$', count_color):
                self.count_color = count_color
            else:
                QMessageBox.warning(self, "Invalid Color", "Please enter a valid hex color code (e.g., #ffc743).")
                self.setup_hotkeys()
                return

        self.update_display()
        self.setup_hotkeys()

    def change_name(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

        new_name, ok = QInputDialog.getText(
            self,
            "Change Counter Name",
            "Enter new counter name:",
            text=self.death_name
        )
        if ok and new_name.strip():
            old_name = self.death_name
            self.death_name = new_name.strip()
            self.log_event("Name Change", f"Counter name changed from '{old_name}' to '{self.death_name}'")
            self.update_display()

        self.setup_hotkeys()

    def parse_hotkey(self, hotkey_str):
        mouse_buttons = {
            "left": pynput_mouse.Button.left,
            "right": pynput_mouse.Button.right,
            "middle": pynput_mouse.Button.middle,
            "mouse4": pynput_mouse.Button.x1,
            "mouse5": pynput_mouse.Button.x2,
            "button4": pynput_mouse.Button.x1,
            "button5": pynput_mouse.Button.x2,
        }
        if hotkey_str.lower() in mouse_buttons:
            return ("mouse", mouse_buttons[hotkey_str.lower()])
        key_code_map = {
            ']': 221,
            '[': 219,
            '+': 187,  # VK_OEM_PLUS
            '-': 189,
            'i': 73,
            'm': 77,
            'h': 72,
            'ctrl': 17,
            'shift': 16,
            'alt': 18,
        }
        # Initialize modifiers and main_key
        modifiers = []
        main_key = hotkey_str.lower()
        # Only split if it's a combination (e.g., "ctrl+i", but not "+")
        parts = main_key.split("+")
        if len(parts) > 1 and all(part.strip() for part in parts):
            # It's a combination like "ctrl+i"
            modifiers = [p.strip() for p in parts[:-1]]
            main_key = parts[-1].strip()
        if not main_key:
            raise ValueError("Hotkey cannot be empty")
        main_key_code = key_code_map.get(main_key, None)
        if main_key_code is None:
            raise ValueError(f"Unsupported key: {main_key}")
        modifier_codes = [key_code_map.get(mod, None) for mod in modifiers]
        if None in modifier_codes:
            raise ValueError(f"Unsupported modifier in hotkey: {hotkey_str}")
        return ("keyboard", (hotkey_str.lower(), tuple(modifiers), main_key, main_key_code, tuple(modifier_codes)))
    
    def setup_hotkeys(self):
        if self.paused:
            print("Skipping hotkey setup while paused")
            return

        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None

        DEBUG = False

        try:
            keyboard_hotkeys = {}
            mouse_hotkeys = {}

            for action, hotkey_str in self.hotkeys.items():
                if not hotkey_str:
                    raise ValueError(f"Hotkey for {action} cannot be empty")
                hotkey_type, hotkey_value = self.parse_hotkey(hotkey_str)
                if hotkey_type == "keyboard":
                    keyboard_hotkeys[hotkey_value] = action
                else:
                    mouse_hotkeys[hotkey_value] = action

            if DEBUG:
                print(f"Binding keyboard hotkeys: {keyboard_hotkeys}")
                print(f"Binding mouse hotkeys: {mouse_hotkeys}")

            if keyboard_hotkeys:
                pressed_key_codes = set()
                last_triggered_time = {}

                def on_press(key):
                    try:
                        if hasattr(key, '_value') and hasattr(key._value, 'vk'):
                            key_code = key._value.vk
                        elif hasattr(key, 'vk'):
                            key_code = key.vk
                        else:
                            key_code = None

                        if DEBUG:
                            if hasattr(key, 'char') and key.char:
                                key_str = key.char
                            else:
                                key_str = str(key).replace("Key.", "")

                        if key_code is None:
                            if DEBUG:
                                print(f"Key code not found for {key_str}")
                            return

                        pressed_key_codes.add(key_code)
                        if DEBUG:
                            print(f"Key pressed: {key_str}, key_code: {key_code}, pressed_key_codes: {pressed_key_codes}")

                        for (hotkey_str, modifiers, main_key, main_key_code, modifier_codes), action in keyboard_hotkeys.items():
                            all_modifiers_pressed = all(mod_code in pressed_key_codes for mod_code in modifier_codes)
                            main_key_pressed = main_key_code == key_code

                            import time
                            current_time = time.time()
                            last_time = last_triggered_time.get(hotkey_str, 0)
                            if current_time - last_time < 0.2:
                                continue

                            if not modifier_codes:
                                if main_key_pressed:
                                    if DEBUG:
                                        print(f"Hotkey triggered: {hotkey_str} -> {action}")
                                    last_triggered_time[hotkey_str] = current_time
                                    if action == "increment":
                                        self.increment_count()
                                    elif action == "decrement":
                                        self.decrement_count()
                            else:
                                if all_modifiers_pressed and main_key_pressed:
                                    if DEBUG:
                                        print(f"Hotkey triggered: {hotkey_str} -> {action}")
                                    last_triggered_time[hotkey_str] = current_time
                                    if action == "increment":
                                        self.increment_count()
                                    elif action == "decrement":
                                        self.decrement_count()

                    except Exception as e:
                        if DEBUG:
                            print(f"Keyboard event error: {e}")

                def on_release(key):
                    try:
                        if hasattr(key, '_value') and hasattr(key._value, 'vk'):
                            key_code = key._value.vk
                        elif hasattr(key, 'vk'):
                            key_code = key.vk
                        else:
                            key_code = None

                        if DEBUG:
                            if hasattr(key, 'char') and key.char:
                                key_str = key.char
                            else:
                                key_str = str(key).replace("Key.", "")

                        if key_code is not None:
                            pressed_key_codes.discard(key_code)

                        if DEBUG:
                            print(f"Key released: {key_str}, key_code: {key_code}, pressed_key_codes: {pressed_key_codes}")
                    except Exception as e:
                        if DEBUG:
                            print(f"Keyboard release error: {e}")

                self.keyboard_listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
                self.keyboard_listener.start()

            if mouse_hotkeys:
                def on_click(x, y, button, pressed):
                    if pressed:
                        for btn, action in mouse_hotkeys.items():
                            if button == btn:
                                if DEBUG:
                                    print(f"Mouse hotkey triggered: {button} -> {action}")
                                if action == "increment":
                                    self.increment_count()
                                elif action == "decrement":
                                    self.decrement_count()

                self.mouse_listener = pynput_mouse.Listener(on_click=on_click)
                self.mouse_listener.start()

            if DEBUG:
                print(f"Hotkeys set: increment={self.hotkeys['increment']}, decrement={self.hotkeys['decrement']}")
        except Exception as e:
            QMessageBox.warning(
                self,
                "Hotkey Error",
                f"Failed to set hotkeys: {str(e)}\nTry running as administrator or choosing different keys (e.g., i, mouse4)."
            )
            if DEBUG:
                print(f"Hotkey error: {e}")

    def set_hotkeys(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

        dialog = HotkeyDialog(self, self.hotkeys)
        if dialog.exec_():
            new_hotkeys = dialog.get_hotkeys()
            invalid_keys = [k for k, v in new_hotkeys.items() if not v]
            if invalid_keys:
                QMessageBox.warning(self, "Invalid Hotkeys", "All hotkeys must be specified.")
                self.setup_hotkeys()
                return
            try:
                for hotkey in new_hotkeys.values():
                    self.parse_hotkey(hotkey)
                self.hotkeys = new_hotkeys
                print(f"Hotkeys updated in memory: {self.hotkeys}")
                self.setup_hotkeys()
                self.save_data()
                print(f"Hotkeys saved to DB: {self.hotkeys}")
                QMessageBox.information(
                    self,
                    "Hotkeys Updated",
                    f"Hotkeys updated: increment={self.hotkeys['increment']}, decrement={self.hotkeys['decrement']}"
                )
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Hotkeys", str(e))
                self.setup_hotkeys()
        else:
            self.setup_hotkeys()

    def closeEvent(self, event):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        pygame.mixer.quit()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeathCounterGUI()
    window.show()
    sys.exit(app.exec_())
