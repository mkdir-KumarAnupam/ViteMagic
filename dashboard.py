import os
import sys
import json
import shutil
import subprocess
import webbrowser
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget,
    QMessageBox, QFileDialog, QListWidgetItem, QApplication
)
from PySide6.QtGui import QIcon, QCursor
from PySide6.QtCore import Qt, QSize, Signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_FILE = os.path.join(BASE_DIR, "projects.json")


class ClickableLabel(QLabel):
    clicked = Signal()
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Dashboard")
        self.resize(800, 600)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 0)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)

        self.create_project_btn = QPushButton("➕ Create New Project")
        self.create_project_btn.setIcon(QIcon(os.path.join(BASE_DIR, "icons", "create.png")))
        self.create_project_btn.clicked.connect(self.open_project_creator)
        header_layout.addWidget(self.create_project_btn)

        self.backup_btn = QPushButton("🛡 Create Backup")
        self.backup_btn.setIcon(QIcon(os.path.join(BASE_DIR, "icons", "backup.png")))
        self.backup_btn.clicked.connect(self.backup_selected_project)
        header_layout.addWidget(self.backup_btn)

        layout.addLayout(header_layout)

        title_label = QLabel("📂 Your Projects:")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.project_list = QListWidget()
        layout.addWidget(self.project_list)

        self.load_projects()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                color: #e0e0e0;
                font-family: "Segoe UI", sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2e2e3e;
                border: none;
                color: #e0e0e0;
                min-height: 40px;
                max-height: 40px;
                border-radius: 999px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3e3e5e;
            }
            QPushButton:pressed {
                background-color: #4e4e7e;
            }
            QLabel {
                color: #e0e0e0;
            }
            QListWidget {
                background-color: #2b2b45;
                border: 1px solid #3a3a70;
                border-radius: 20px;
            }
            QListWidget::item {
                background-color: #32324f;
                border: 1px solid #3a3a70;
                border-radius: 20px;
            }
            QListWidget::item:hover {
                background-color: #3a3a70;
            }
            QListWidget::item:selected {
                background-color: #3a3a70;
            }
            QLabel#devUrlLabel {
                color: #a0c0ff;
            }
        """)

    def load_projects(self):
        self.project_list.clear()
        projects = []
        if os.path.exists(PROJECTS_FILE):
            try:
                with open(PROJECTS_FILE, "r") as f:
                    projects = json.load(f)
                if not isinstance(projects, list):
                    projects = []
            except Exception:
                projects = []
        for project in projects:
            self.add_project_item(project["name"], project["location"])

    def add_project_item(self, name, location):
        project_widget = QWidget()
        project_layout = QVBoxLayout(project_widget)
        project_layout.setContentsMargins(10, 10, 10, 10)
        project_layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        
        project_label = ClickableLabel(f"📁 {name}")
        project_label.clicked.connect(lambda: self.open_in_explorer(location))
        top_row.addWidget(project_label)

        open_editor_btn = QPushButton("📝 Open in Editor")
        open_editor_btn.setIcon(QIcon(os.path.join(BASE_DIR, "icons", "code.png")))
        open_editor_btn.setFixedSize(QSize(200, 40))
        open_editor_btn.clicked.connect(lambda: self.open_project(location))
        top_row.addWidget(open_editor_btn)

        start_dev_btn = QPushButton("🚀 Start Dev Server")
        start_dev_btn.setIcon(QIcon(os.path.join(BASE_DIR, "icons", "play.png")))
        start_dev_btn.setFixedSize(QSize(200, 40))
        start_dev_btn.clicked.connect(lambda: self.start_dev_server(location))
        top_row.addWidget(start_dev_btn)

        backup_btn = QPushButton("📦 Create Backup")
        backup_btn.setIcon(QIcon(os.path.join(BASE_DIR, "icons", "backup.png")))
        backup_btn.setFixedSize(QSize(200, 40))
        backup_btn.clicked.connect(lambda: self.create_backup(location))
        top_row.addWidget(backup_btn)

        project_layout.addLayout(top_row)

        dev_url_label = QLabel("")
        dev_url_label.setObjectName("devUrlLabel")
        dev_url_label.setAlignment(Qt.AlignCenter)
        project_layout.addWidget(dev_url_label)

        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(500, 80))
        list_item.setData(Qt.UserRole, location)
        self.project_list.addItem(list_item)
        self.project_list.setItemWidget(list_item, project_widget)

    def open_in_explorer(self, project_location):
        try:
            if os.name == "nt":
                os.startfile(project_location)
            elif os.name == "posix":
                subprocess.Popen(["xdg-open", project_location])
            else:
                webbrowser.open(project_location)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open explorer: {e}")

    def backup_selected_project(self):
        item = self.project_list.currentItem()
        if item is None:
            QMessageBox.information(self, "Info", "Please select a project to backup.")
            return
        project_location = item.data(Qt.UserRole)
        self.create_backup(project_location)

    def open_project_creator(self):
        from main_window import MainWindow
        self.project_creator = MainWindow()
        self.project_creator.show()
        self.close()

    def open_project(self, project_location):
        try:
            subprocess.run(["code", project_location], shell=True, check=True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open project: {e}")

    def create_backup(self, project_location):
        confirm = QMessageBox.question(
            self,
            "Confirm Backup",
            "Do you want to create a backup for this project?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        backup_dir = QFileDialog.getExistingDirectory(self, "Select Backup Destination")
        if not backup_dir:
            return

        try:
            base_name = os.path.join(backup_dir, os.path.basename(project_location) + "_backup")
            shutil.make_archive(base_name, 'zip', project_location)
            QMessageBox.information(self, "Success", f"Backup created: {base_name}.zip")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Backup failed: {e}")

    def start_dev_server(self, project_location):
        try:
            subprocess.Popen(["npm", "run", "dev"], cwd=project_location, shell=True)
            dev_url = "http://localhost:5173"
            webbrowser.open(dev_url)
            for i in range(self.project_list.count()):
                item = self.project_list.item(i)
                if item.data(Qt.UserRole) == project_location:
                    widget = self.project_list.itemWidget(item)
                    dev_label = widget.findChild(QLabel, "devUrlLabel")
                    if dev_label:
                        dev_label.setText(f'<a href="{dev_url}">Dev Server: {dev_url}</a>')
                        dev_label.setOpenExternalLinks(True)
                        dev_label.setCursor(QCursor(Qt.PointingHandCursor))
                    break
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to start dev server: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec())
