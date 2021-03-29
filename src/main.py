import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMenuBar, QAction, QFrame, QVBoxLayout, QHBoxLayout, QLineEdit, QMainWindow, \
    QSplitter, QGroupBox, QPushButton, QLabel, QStackedWidget, QScrollArea, QComboBox, QCheckBox, \
    QGraphicsOpacityEffect, QGridLayout
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QGuiApplication, QIcon, QFont


def save_user_input(**kwargs) -> bool:
    if "user_input" in kwargs:
        todo = kwargs["user_input"]
    if "priority" in kwargs:
        priority = kwargs["priority"]
    if "status" in kwargs:
        status = kwargs["status"]

    user_input = {
        "to-do": todo,
        "due-date": None,
        "reminder": False,
        "priority": priority,
        "status": status
    }

    if not os.path.isfile("./list.json"):
        user_input = [user_input]
        with open("./list.json", "w") as f:
            json.dump(user_input, f, indent=4)

    else:
        with open("./list.json") as f:
            feed = json.load(f)
            feed.append(user_input)

        with open("./list.json", "w") as f:
            json.dump(feed, f, indent=4)
    return True


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.menu_bar = QMenuBar()
        self.window_title = "To-Do"
        self.init_ui()
        self.calculate_splitter_ratio()

    def init_ui(self) -> None:
        QCoreApplication.setApplicationName("To-Do")
        QCoreApplication.setApplicationVersion("0.0.1")
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
        self.splitter.splitterMoved.connect(self.calculate_splitter_ratio)

        self.input_frame = QFrame(self.splitter)
        self.input_frame.setFrameShape(QFrame.StyledPanel)

        def toggle_input_options() -> None:
            group_2_in_input_frame.show() if group_2_in_input_frame.isHidden() else group_2_in_input_frame.hide()

        def add_widgets(label_text: str) -> bool:

            def toggle_todo_checked() -> None:
                opacity = QGraphicsOpacityEffect()
                if check_box.isChecked():
                    opacity.setOpacity(0.5)
                else:
                    opacity.setOpacity(1)
                group_box.setGraphicsEffect(opacity)

            group_box = QGroupBox()
            group_box.setStyleSheet("background: white")
            vertical_box_layout = QVBoxLayout(group_box)
            label = QLabel(label_text.capitalize(), group_box)
            font = QFont("cursive", 16)
            label.setFont(font)
            check_box = QCheckBox(group_box)
            check_box.stateChanged.connect(toggle_todo_checked)
            todo_display_layout = QHBoxLayout()
            todo_display_layout.addWidget(check_box)
            todo_display_layout.addWidget(label)
            vertical_box_layout.addLayout(todo_display_layout)
            todo_display_layout.setAlignment(Qt.AlignLeft)
            horizontal_box_layout = QHBoxLayout()
            grid = QGridLayout()
            vertical_box_layout.addLayout(grid)
            vertical_box_layout.addLayout(horizontal_box_layout)

            def delete_todo() -> None:
                with open("./list.json") as f:
                    feed = json.load(f)
                print(feed)

                for todo in feed:
                    som = todo["to-do"]
                    if som == label_text:
                        feed.pop(feed.index(todo))

                if not feed:
                    os.remove("./list.json")

                group_box.deleteLater()
                input_box.setFocus()

            delete = QPushButton(QIcon("../svgs/trash-alt.svg"), "")
            delete.clicked.connect(delete_todo)
            priority = QLabel(f"Priority: {priorities_list.currentText()}")
            due_date = QLabel(f"Due Date: {None}")
            reminder = QLabel(f"Reminder: Off")
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
                return
            input_box.clear()
            priority = priorities_list.currentText()
            priority = None if (priority == "None") else priority.lower()

            if not add_widgets(user_input):
                print("Unable to add to-do!")
                ...
                return

            todo_data = {"user_input": user_input, "priority": priority, "status": 0}

            if not save_user_input(**todo_data):
                print("Unable to save to-do")
                ...

        input_box = QLineEdit(self.input_frame)
        input_box.setPlaceholderText("Add a todo ...")
        input_box.returnPressed.connect(process_input)
        add_todo_button = QPushButton("Add", self.input_frame)
        add_todo_button.clicked.connect(process_input)
        more_button = QPushButton(">", self.input_frame)
        more_button.clicked.connect(toggle_input_options)

        group_1_in_input_frame = QGroupBox(self.input_frame)

        horizontal_layout_1_in_input_frame = QHBoxLayout(group_1_in_input_frame)
        horizontal_layout_1_in_input_frame.addWidget(input_box)
        horizontal_layout_1_in_input_frame.addWidget(add_todo_button)
        horizontal_layout_1_in_input_frame.addWidget(more_button)
        horizontal_layout_1_in_input_frame.setStretch(0, 3)

        group_2_in_input_frame = QGroupBox(self.input_frame)
        set_due_date_button = QPushButton("Set Due Date")
        set_reminder_button = QPushButton("Set reminder")
        priorities = ("None", "Low", "Medium", "High")
        priorities_list = QComboBox(group_2_in_input_frame)
        set_priority_label = QLabel("Priority:", priorities_list)
        priorities_list.insertItems(0, priorities)
        horizontal_layout_2_in_input_frame = QHBoxLayout(group_2_in_input_frame)
        horizontal_layout_2_in_input_frame.setAlignment(Qt.AlignLeft)
        horizontal_layout_2_in_input_frame.addWidget(set_priority_label)
        horizontal_layout_2_in_input_frame.addWidget(priorities_list)
        horizontal_layout_2_in_input_frame.addWidget(set_reminder_button)
        horizontal_layout_2_in_input_frame.addWidget(set_due_date_button)

        input_frame_layout = QVBoxLayout(self.input_frame)
        input_frame_layout.addWidget(group_1_in_input_frame)
        input_frame_layout.addWidget(group_2_in_input_frame)

        self.display_frame = QFrame()
        self.display_frame.setStyleSheet("background: #fff")
        self.display_frame.setFrameShape(QFrame.StyledPanel)

        display_frame_layout = QVBoxLayout(self.display_frame)
        display_frame_layout.setAlignment(Qt.AlignTop)

        scroll_area = QScrollArea(self.splitter)
        scroll_area.setWidget(self.display_frame)
        scroll_area.setWidgetResizable(True)

        self.setCentralWidget(self.splitter)

        def load_todo():
            ...

    def parse_input(self):
        ...

    def show_info(self) -> None:
        self.isWindow()
        print("Showing info")
        ...

    def calculate_splitter_ratio(self) -> None:
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
