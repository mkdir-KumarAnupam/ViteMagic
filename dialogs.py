import json
import shutil
import os
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QDialogButtonBox, QFileDialog, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QIcon

class SettingsDialog(QDialog):
    def __init__(self, current_base_dir, current_placements, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(400, 200)
        layout = QFormLayout(self)
        self.base_dir_edit = QLineEdit(current_base_dir)
        self.base_dir_edit.setToolTip("Set the base directory where projects will be created.")
        browse_button = QPushButton(QIcon("icons/browse.png"), "Browse")
        browse_button.setToolTip("Browse for base directory")
        browse_button.clicked.connect(self.browse_directory)
        base_dir_layout = QHBoxLayout()
        base_dir_layout.addWidget(self.base_dir_edit)
        base_dir_layout.addWidget(browse_button)
        layout.addRow("Base Directory:", base_dir_layout)
        self.placements_edit = QLineEdit(", ".join(current_placements))
        self.placements_edit.setToolTip("Comma-separated list of project placements")
        layout.addRow("Project Placements:", self.placements_edit)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.base_dir_edit.setText(directory)

    def get_values(self):
        base_dir = self.base_dir_edit.text().strip()
        placements = [p.strip() for p in self.placements_edit.text().split(",") if p.strip()]
        return base_dir, placements

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Guide")
        self.resize(500, 400)
        layout = QVBoxLayout(self)
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setPlainText(
"Vite Magic User Guide:\n\n1. Fill in the required fields for project placement, type, name, and choose additional options.\n2. Use the extra options to select a template, additional dependencies, and set environment variables.\n3. Toggle between dark/light themes via the View menu.\n4. Use the Templates menu to save/load project templates for reuse.\n5. GitHub integration requires GitHub CLI (gh) to be installed and authenticated.\n6. Detailed logs are available in the log area and vite_magic.log file."
        )
        layout.addWidget(help_text)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

class DependencyManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Dependencies")
        self.resize(400, 300)
        layout = QFormLayout(self)
        self.project_path_edit = QLineEdit()
        self.project_path_edit.setToolTip("Path to your project folder")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_project)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.project_path_edit)
        path_layout.addWidget(browse_button)
        layout.addRow("Project Path:", path_layout)
        self.dependency_edit = QLineEdit()
        self.dependency_edit.setToolTip("Name of dependency (e.g., lodash)")
        layout.addRow("Dependency:", self.dependency_edit)
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_dependency)
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_dependency)
        self.update_btn = QPushButton("Update")
        self.update_btn.clicked.connect(self.update_dependency)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.update_btn)
        layout.addRow(btn_layout)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addRow("Output:", self.log_text)

    def browse_project(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if directory:
            self.project_path_edit.setText(directory)

    def add_dependency(self):
        self.run_dependency_command("install", "")

    def remove_dependency(self):
        self.run_dependency_command("uninstall", "")

    def update_dependency(self):
        self.run_dependency_command("install", "@latest")

    def run_dependency_command(self, action, suffix):
        project_path = self.project_path_edit.text().strip()
        dependency = self.dependency_edit.text().strip()
        if not project_path or not os.path.exists(project_path):
            self.log_text.append("Invalid project path.")
            return
        if not dependency:
            self.log_text.append("Please enter a dependency name.")
            return
        cmd = f"npm {action} {dependency}{suffix}"
        try:
            run_command(cmd, project_path, f"npm {action}")
            self.log_text.append(f"Command succeeded: {cmd}")
        except Exception as e:
            self.log_text.append(f"Command failed: {e}")

class ProjectDashboardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Dashboard")
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        path_layout = QHBoxLayout()
        self.project_path_edit = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_project)
        path_layout.addWidget(self.project_path_edit)
        path_layout.addWidget(browse_button)
        layout.addLayout(path_layout)
        self.refresh_btn = QPushButton("Load Dashboard")
        self.refresh_btn.clicked.connect(self.load_dashboard)
        layout.addWidget(self.refresh_btn)
        self.stats_label = QLabel("")
        layout.addWidget(self.stats_label)

    def browse_project(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if directory:
            self.project_path_edit.setText(directory)

    def load_dashboard(self):
        project_path = self.project_path_edit.text().strip()
        if not project_path or not os.path.exists(project_path):
            QMessageBox.warning(self, "Error", "Invalid project path.")
            return
        file_count = sum(len(files) for _, _, files in os.walk(project_path))
        pkg_path = os.path.join(project_path, "package.json")
        dep_count = 0
        if os.path.exists(pkg_path):
            try:
                with open(pkg_path, "r") as f:
                    pkg = json.load(f)
                    dep_count = len(pkg.get("dependencies", {})) + len(pkg.get("devDependencies", {}))
            except Exception:
                pass
        try:
            with open("vite_magic.log", "r") as f:
                log_lines = f.readlines()[-5:]
            recent_activity = "".join(log_lines)
        except Exception:
            recent_activity = "No recent activity."
        stats = f"Total Files: {file_count}\nTotal Dependencies: {dep_count}\nRecent Activity:\n{recent_activity}"
        self.stats_label.setText(stats)

class BackupRestoreDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backup / Restore Project")
        self.resize(400, 200)
        layout = QFormLayout(self)
        path_layout = QHBoxLayout()
        self.project_path_edit = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_project)
        path_layout.addWidget(self.project_path_edit)
        path_layout.addWidget(browse_button)
        layout.addRow("Project Path:", path_layout)
        btn_layout = QHBoxLayout()
        self.backup_btn = QPushButton("Create Backup")
        self.backup_btn.clicked.connect(self.create_backup)
        self.restore_btn = QPushButton("Restore Backup")
        self.restore_btn.clicked.connect(self.restore_backup)
        btn_layout.addWidget(self.backup_btn)
        btn_layout.addWidget(self.restore_btn)
        layout.addRow(btn_layout)
        self.output_label = QLabel("")
        layout.addRow("Output:", self.output_label)

    def browse_project(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if directory:
            self.project_path_edit.setText(directory)

    def create_backup(self):
        project_path = self.project_path_edit.text().strip()
        if not project_path or not os.path.exists(project_path):
            self.output_label.setText("Invalid project path.")
            return
        backup_dir = QFileDialog.getExistingDirectory(self, "Select Backup Destination")
        if not backup_dir:
            return
        base_name = os.path.join(backup_dir, os.path.basename(project_path) + "_backup")
        try:
            shutil.make_archive(base_name, 'zip', project_path)
            self.output_label.setText(f"Backup created: {base_name}.zip")
        except Exception as e:
            self.output_label.setText(f"Backup failed: {e}")

    def restore_backup(self):
        project_path = self.project_path_edit.text().strip()
        if not project_path or not os.path.exists(project_path):
            self.output_label.setText("Invalid project path.")
            return
        backup_file, _ = QFileDialog.getOpenFileName(self, "Select Backup File", "", "Zip Files (*.zip)")
        if not backup_file:
            return
        try:
            shutil.unpack_archive(backup_file, project_path, 'zip')
            self.output_label.setText("Backup restored successfully.")
        except Exception as e:
            self.output_label.setText(f"Restore failed: {e}")