import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMenuBar, QAction, QFrame, QVBoxLayout, QHBoxLayout, QLineEdit, QMainWindow, \
    QSplitter, QGroupBox, QPushButton, QScrollBar, QListView, QListWidget, QListWidgetItem, QLabel, QStackedWidget, QScrollArea
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QGuiApplication, QIcon


class MainWindow(QMainWindow):
    def __init__(self):
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

        def toggle_input_options():
            if group_2_in_input_frame.isHidden():
                group_2_in_input_frame.show()
                return
            group_2_in_input_frame.hide()

        def parse_input():
            user_input = {
                "to-do": input_box.text(),
                "due-date": None,
                "reminder": False,
                "priority": None,
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


        def add_widgets():
            group_box = QGroupBox()
            label = QLabel(input_box.text(), group_box)
            hbox = QHBoxLayout(group_box)
            hbox.addWidget(label)
            group_box.setFixedHeight(100)
            group_box.setAlignment(Qt.AlignTop)
            display_frame_layout.addWidget(group_box)

        input_box = QLineEdit()
        input_box.setPlaceholderText("Add a todo ...")
        # input_box.editingFinished.connect(parse_input)
        # input_box.editingFinished.connect(add_widgets)
        add_todo_button = QPushButton("Add")
        add_todo_button.clicked.connect(parse_input)
        add_todo_button.clicked.connect(add_widgets)
        more_button = QPushButton(">")
        more_button.clicked.connect(toggle_input_options)

        group_1_in_input_frame = QGroupBox()

        horizontal_layout_1_in_input_frame = QHBoxLayout(group_1_in_input_frame)
        horizontal_layout_1_in_input_frame.addWidget(input_box)
        horizontal_layout_1_in_input_frame.addWidget(add_todo_button)
        horizontal_layout_1_in_input_frame.addWidget(more_button)
        horizontal_layout_1_in_input_frame.setStretch(0, 3)

        group_2_in_input_frame = QGroupBox()
        set_due_date_button = QPushButton("Set Due Date")
        set_reminder_button = QPushButton("Set reminder")
        set_priority_button = QPushButton("Set Priority")
        horizontal_layout_2_in_input_frame = QHBoxLayout(group_2_in_input_frame)
        horizontal_layout_2_in_input_frame.setAlignment(Qt.AlignLeft)
        horizontal_layout_2_in_input_frame.addWidget(set_priority_button)
        horizontal_layout_2_in_input_frame.addWidget(set_reminder_button)
        horizontal_layout_2_in_input_frame.addWidget(set_due_date_button)

        input_frame_layout = QVBoxLayout(self.input_frame)
        input_frame_layout.addWidget(group_1_in_input_frame)
        input_frame_layout.addWidget(group_2_in_input_frame)

        self.display_frame = QFrame()
        self.display_frame.setFrameShape(QFrame.StyledPanel)

        display_frame_layout = QVBoxLayout(self.display_frame)

        scroll_area = QScrollArea(self.splitter)
        scroll_area.setWidget(self.display_frame)
        scroll_area.setWidgetResizable(True)


        self.setCentralWidget(self.splitter)

    def parse_input(self):
        ...

    def show_info(self) -> None:
        self.isWindow()
        print("Showing info")
        ...

    def calculate_splitter_ratio(self):
        top, bottom = self.splitter.sizes()
        total = top + bottom
        new_top = total // 5
        self.splitter.setSizes([new_top, total - new_top])


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
