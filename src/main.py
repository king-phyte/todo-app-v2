import sys
import os
from PyQt5.QtWidgets import QApplication, QMenuBar, QAction, QFrame, QVBoxLayout, QHBoxLayout, QLineEdit, QMainWindow, \
    QSplitter, QGroupBox, QPushButton, QLabel, QScrollArea, QComboBox, QCheckBox, \
    QGraphicsOpacityEffect, QGridLayout, QDialog, QDateTimeEdit, QRadioButton
from PyQt5.QtCore import QCoreApplication, Qt, QDateTime
from PyQt5.QtGui import QGuiApplication, QIcon, QFont
from typing import List, Tuple
import sqlite3


# Currently being used as a temporary memory to hold the values of returned by the "Set Date" feature
# Think of a better way to implement this
temp: dict


def get_selected_date(data: dict) -> None:
    global temp
    temp = data


def access_database() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    try:
        if not os.path.isfile("./journal.db"):
            print("No database found. Creating a new one")
            connection = sqlite3.connect("./journal.db")
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE todo(text, priority, due_date, reminder)")
        else:
            connection = sqlite3.connect("./journal.db")
            cursor = connection.cursor()

        return connection, cursor

    except sqlite3.Error as e:
        print(e)


def save_to_database(todo: dict) -> bool:
    try:
        connection, cursor = access_database()
        cursor.execute("INSERT INTO todo VALUES (?, ?, ?, ?)", tuple(todo.values()))
        connection.commit()
        connection.close()
        return True
    except sqlite3.Error as e:
        print(e)
    return False


def load_existing_todos() -> List[dict]:
    try:
        connection, cursor = access_database()
        connection.commit()
        cursor.close()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        database_rows = cursor.execute("SELECT * FROM todo")
        database_rows = [dict(row) for row in database_rows]
        connection.close()
        return database_rows

    except sqlite3.Error as e:
        print(e)


def delete_todo_from_database(todo: dict) -> bool:
    try:
        connection, cursor = access_database()
        cursor.execute("DELETE FROM todo WHERE text=?", (todo["text"], ))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except sqlite3.Error as e:
        print(e)
    return False


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.menu_bar = QMenuBar()
        self.window_title = "To-Do"
        self.init_ui()
        self.maintain_splitter_ratio()

    def init_ui(self) -> None:
        QCoreApplication.setApplicationName("To-Do")
        QCoreApplication.setApplicationVersion("0.0.4")
        QCoreApplication.setOrganizationName("King Inc.")
        QGuiApplication.setFallbackSessionManagementEnabled(False)

        width, height = 800, 600
        self.setWindowTitle(self.window_title)
        self.setMinimumSize(width, height)
        self.create_menu_bar()
        self.create_main_area()
        self.show()

    def create_menu_bar(self) -> None:
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("File")
        exit_action = QAction(QIcon("../svgs/times.svg"), "Exit", file_menu)
        exit_action.setShortcut("Ctrl+F4")
        exit_action.triggered.connect(sys.exit)
        file_menu.addAction(exit_action)

        help_menu = self.menu_bar.addMenu("Help")
        info = QAction(QIcon("../svgs/info.svg"), "Info", help_menu)
        info.setShortcut("F1")
        info.triggered.connect(self.show_info)
        help_menu.addAction(info)

    def create_main_area(self) -> None:
        self.splitter = QSplitter(Qt.Vertical, self)
        self.splitter.splitterMoved.connect(self.maintain_splitter_ratio)

        input_frame = QFrame(self.splitter)
        input_frame.setFrameShape(QFrame.StyledPanel)

        def toggle_input_options() -> None:
            group_2_in_input_frame.show() if group_2_in_input_frame.isHidden() else group_2_in_input_frame.hide()

        def toggle_todo_checked(check_box: QCheckBox, group_box: QGroupBox) -> None:
            opacity = QGraphicsOpacityEffect()
            if check_box.isChecked():
                opacity.setOpacity(0.5)
            else:
                opacity.setOpacity(1)
            group_box.setGraphicsEffect(opacity)

        def delete_todo(group_box: QGroupBox, _todo: dict) -> None:
            if not delete_todo_from_database(_todo):
                print("Unable to delete todo from database.")

            group_box.deleteLater()
            input_box.setFocus()

        def add_todo(_todo: dict) -> bool:
            group_box = QGroupBox()
            group_box.setStyleSheet("background: white")
            vertical_box_layout = QVBoxLayout(group_box)
            label = QLabel(_todo["text"].capitalize(), group_box)
            font = QFont("cursive", 16)
            label.setFont(font)
            check_box = QCheckBox(group_box)
            check_box.stateChanged.connect(lambda: toggle_todo_checked(check_box, group_box))
            todo_display_layout = QHBoxLayout()
            todo_display_layout.addWidget(check_box)
            todo_display_layout.addWidget(label)
            vertical_box_layout.addLayout(todo_display_layout)
            todo_display_layout.setAlignment(Qt.AlignLeft)
            horizontal_box_layout = QHBoxLayout()
            grid = QGridLayout()
            vertical_box_layout.addLayout(grid)
            vertical_box_layout.addLayout(horizontal_box_layout)

            delete = QPushButton(QIcon("../svgs/trash-alt.svg"), "")
            delete.clicked.connect(lambda: delete_todo(group_box, _todo))
            priority = QLabel(f"Priority: {priority_options[_todo['priority']]}")
            due_date = QLabel(f"Due Date: {_todo['due_date']}")
            reminder_value = "On" if _todo['reminder'] else "Off"
            reminder = QLabel(f"Reminder: {reminder_value}")
            reminder.setAlignment(Qt.AlignRight)
            horizontal_box_layout.setAlignment(Qt.AlignLeft)

            grid.addWidget(priority, 0, 0)
            grid.addWidget(due_date, 0, 1)
            grid.addWidget(reminder, 0, 2)
            grid.addWidget(delete, 0, 3)
            grid.setAlignment(delete, Qt.AlignRight)

            group_box.setFixedHeight(100)
            group_box.setAlignment(Qt.AlignTop)
            display_frame_layout.insertWidget(0, group_box)
            return True

        def process_input() -> None:
            user_input = input_box.text()
            is_empty_user_input = len(user_input) < 1
            if is_empty_user_input:
                input_box.setFocus()
                return
            input_box.clear()
            priorities_dict = {"None": 0, "Low": 1, "Medium": 2, "High": 3}
            priority = priorities_dict[priorities_combobox.currentText()]
            try:
                due_date = temp["due_date"]
                reminder = temp["reminder"]
            except NameError:
                due_date = None
                reminder = False
            to_do_data = {"text": user_input, "priority": priority, "due_date": due_date, "reminder": reminder}
            # todo = ToDo(**to_do_data)

            if not add_todo(to_do_data):
                print("Unable to add to-do!")
                ...
                return

            if not save_to_database(to_do_data):
                print("Unable to save todo to database")
                ...

        input_box = QLineEdit(input_frame)
        input_box.setPlaceholderText("Add a todo ...")
        input_box.returnPressed.connect(process_input)
        add_todo_button = QPushButton("Add", input_frame)
        add_todo_button.clicked.connect(process_input)
        more_button = QPushButton("...", input_frame)
        more_button.clicked.connect(toggle_input_options)

        group_1_in_input_frame = QGroupBox(input_frame)

        horizontal_layout_1_in_input_frame = QHBoxLayout(group_1_in_input_frame)
        horizontal_layout_1_in_input_frame.addWidget(input_box)
        horizontal_layout_1_in_input_frame.addWidget(add_todo_button)
        horizontal_layout_1_in_input_frame.addWidget(more_button)
        horizontal_layout_1_in_input_frame.setStretch(0, 3)

        def set_due_date() -> None:
            due_date_window = QDialog()
            due_date_window.setModal(True)
            due_date_window.setFixedSize(300, 300)
            date_and_time = QDateTimeEdit(due_date_window)
            date_and_time.setCalendarPopup(True)
            date_and_time.setMinimumDateTime(QDateTime().currentDateTime())
            date_and_time.setDisplayFormat("dd MMMM yyyy HH:MM")
            reminder_label = QLabel("Reminder: ")
            reminder_radio_on = QRadioButton("On", due_date_window)
            reminder_radio_off = QRadioButton("Off", due_date_window)
            reminder_radio_off.setChecked(True)

            set_date = QPushButton("OK")
            set_date.clicked.connect(due_date_window.accept)
            cancel = QPushButton("Cancel")
            cancel.clicked.connect(due_date_window.close)

            horizontal_layout = QHBoxLayout()
            horizontal_layout.addWidget(reminder_label, stretch=3)
            horizontal_layout.addWidget(reminder_radio_on, stretch=1)
            horizontal_layout.addWidget(reminder_radio_off, stretch=1)

            horizontal_layout_2 = QHBoxLayout()
            horizontal_layout_2.addWidget(set_date)
            horizontal_layout_2.addWidget(cancel)

            due_date_window_layout = QVBoxLayout(due_date_window)
            due_date_window_layout.addWidget(date_and_time)
            due_date_window_layout.addLayout(horizontal_layout)
            due_date_window_layout.addLayout(horizontal_layout_2)

            due_date_window.accepted.connect(lambda: get_selected_date(
                {"due_date": date_and_time.dateTime().toString("dd/MMM/yy | HH:MM"),
                 "reminder": reminder_radio_on.isChecked()
                 }))
            due_date_window.exec()

        priority_options = ("None", "Low", "Medium", "High")

        group_2_in_input_frame = QGroupBox(input_frame)
        set_due_date_button = QPushButton("Set Due Date")
        set_due_date_button.clicked.connect(set_due_date)
        priorities_combobox = QComboBox(group_2_in_input_frame)
        set_priority_label = QLabel("Priority:", priorities_combobox)
        priorities_combobox.insertItems(0, priority_options)
        horizontal_layout_2_in_input_frame = QHBoxLayout(group_2_in_input_frame)
        horizontal_layout_2_in_input_frame.setAlignment(Qt.AlignLeft)
        horizontal_layout_2_in_input_frame.addWidget(set_priority_label)
        horizontal_layout_2_in_input_frame.addWidget(priorities_combobox)
        horizontal_layout_2_in_input_frame.addWidget(set_due_date_button)

        input_frame_layout = QVBoxLayout(input_frame)
        input_frame_layout.addWidget(group_1_in_input_frame)
        input_frame_layout.addWidget(group_2_in_input_frame)

        display_frame = QFrame()
        display_frame.setStyleSheet("background: #fff")
        display_frame.setFrameShape(QFrame.StyledPanel)

        display_frame_layout = QVBoxLayout(display_frame)
        display_frame_layout.setAlignment(Qt.AlignTop)

        scroll_area = QScrollArea(self.splitter)
        scroll_area.setWidget(display_frame)
        scroll_area.setWidgetResizable(True)

        previous_todos = load_existing_todos()
        for todo in previous_todos:
            add_todo(todo)

        self.setCentralWidget(self.splitter)

    def show_info(self) -> None:
        self.isWindow()
        print("Showing info")
        ...

    def maintain_splitter_ratio(self) -> None:
        top, bottom = self.splitter.sizes()
        total = top + bottom
        new_top = total // 5
        self.splitter.setSizes([new_top, total - new_top])


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
