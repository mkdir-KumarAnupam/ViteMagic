import os
import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QTextEdit, QLabel,
    QProgressBar, QMessageBox, QCheckBox, QHBoxLayout, QDialog
)
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QFont, QIcon, QAction

from dialogs import SettingsDialog, HelpDialog, DependencyManagerDialog, ProjectDashboardDialog, BackupRestoreDialog
from worker import ProjectCreatorWorker
from utils import is_valid_project_name  # Import the function here
from constants import PROJECT_TYPES, AUTH_CHOICES, TEMPLATE_OPTIONS, ADDITIONAL_DEPENDENCIES, TEMPLATE_STORAGE_FILE
from dashboard import Dashboard

# Use the absolute path to ensure projects.json is read/written in the same directory as this script.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_FILE = os.path.join(BASE_DIR, "projects.json")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vite Magic")
        self.resize(900, 650)
        self.setMinimumSize(800, 600)

        # Default base directory where your top-level "placement" folders exist.
        self.base_dir = "C:\\Projects"

        # Available placement folders for your projects
        self.placement_list = [
            "PersonalProjects",
            "HackathonProjects",
            "AssignmentProjects",
            "ProfessionalProjects"
        ]

        # Theme handling
        self.current_theme = "Dark"
        self.themes = {
            "Dark": {
                "background": "#2e3440",
                "text": "#eceff4",
                "input_background": "#3b4252",
                "input_text": "#d8dee9",
                "button_background": "#5e81ac",
                "button_hover": "#81a1c1",
                "progress_bar": "#81a1c1"
            },
            "Light": {
                "background": "#f0f0f0",
                "text": "#333",
                "input_background": "#fff",
                "input_text": "#333",
                "button_background": "#007acc",
                "button_hover": "#005f99",
                "progress_bar": "#005f99"
            },
            "Ocean": {
                "background": "#1a1a2e",
                "text": "#e0e0e0",
                "input_background": "#16213e",
                "input_text": "#e0e0e0",
                "button_background": "#0f3460",
                "button_hover": "#1f4068",
                "progress_bar": "#1f4068"
            },
            "Forest": {
                "background": "#1a2e1a",
                "text": "#e0e0e0",
                "input_background": "#162e16",
                "input_text": "#e0e0e0",
                "button_background": "#0f600f",
                "button_hover": "#1f681f",
                "progress_bar": "#1f681f"
            },
            "Sunset": {
                "background": "#2e1a1a",
                "text": "#e0e0e0",
                "input_background": "#2e1616",
                "input_text": "#e0e0e0",
                "button_background": "#600f0f",
                "button_hover": "#681f1f",
                "progress_bar": "#681f1f"
            },
            "Midnight": {
                "background": "#000033",
                "text": "#ffffff",
                "input_background": "#000066",
                "input_text": "#ffffff",
                "button_background": "#000099",
                "button_hover": "#0000cc",
                "progress_bar": "#0000cc"
            }
        }

        self.setup_ui()
        self.worker = None

    def setup_ui(self):
        menu_bar = self.menuBar()

        # Dashboard
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.setIcon(QIcon(os.path.join(BASE_DIR, "icons", "dashboard.png")))
        dashboard_action.triggered.connect(self.open_dashboard)
        menu_bar.addAction(dashboard_action)

        # Settings menu
        settings_menu = menu_bar.addMenu(QIcon(os.path.join(BASE_DIR, "icons", "settings.png")), "Settings")
        edit_settings_action = settings_menu.addAction("Edit Project Settings")
        edit_settings_action.setIcon(QIcon(os.path.join(BASE_DIR, "icons", "edit.png")))
        edit_settings_action.triggered.connect(self.open_settings_dialog)

        # View menu
        view_menu = menu_bar.addMenu(QIcon(os.path.join(BASE_DIR, "icons", "view.png")), "View")
        toggle_theme_action = view_menu.addAction("Toggle Dark/Light Theme")
        toggle_theme_action.setIcon(QIcon(os.path.join(BASE_DIR, "icons", "theme.png")))
        toggle_theme_action.triggered.connect(self.toggle_theme)

        # Theme selection
        themes_menu = view_menu.addMenu("Select Theme")
        for theme_name in self.themes.keys():
            theme_action = QAction(theme_name, self)
            theme_action.triggered.connect(lambda checked, name=theme_name: self.apply_theme(name))
            themes_menu.addAction(theme_action)

        # Templates menu
        templates_menu = menu_bar.addMenu(QIcon(os.path.join(BASE_DIR, "icons", "template.png")), "Templates")
        save_template_action = templates_menu.addAction("Save Current Template")
        save_template_action.setIcon(QIcon(os.path.join(BASE_DIR, "icons", "save.png")))
        save_template_action.triggered.connect(self.save_template)

        load_template_action = templates_menu.addAction("Load Template")
        load_template_action.setIcon(QIcon(os.path.join(BASE_DIR, "icons", "load.png")))
        load_template_action.triggered.connect(self.load_template)

        # Help menu
        help_menu = menu_bar.addMenu(QIcon(os.path.join(BASE_DIR, "icons", "help.png")), "Help")
        help_action = help_menu.addAction("User Guide")
        help_action.setIcon(QIcon(os.path.join(BASE_DIR, "icons", "info.png")))
        help_action.triggered.connect(self.show_help)

        # Tools menu
        tools_menu = menu_bar.addMenu(QIcon(os.path.join(BASE_DIR, "icons", "tools.png")), "Tools")
        dep_manager_action = QAction("Manage Dependencies", self)
        dep_manager_action.triggered.connect(self.open_dependency_manager)
        tools_menu.addAction(dep_manager_action)

        dashboard_action = QAction("Project Dashboard", self)
        dashboard_action.triggered.connect(self.open_dashboard)
        tools_menu.addAction(dashboard_action)

        backup_action = QAction("Backup/Restore", self)
        backup_action.triggered.connect(self.open_backup_restore)
        tools_menu.addAction(backup_action)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Header
        header_label = QLabel("Vite Magic")
        header_font = QFont("Arial", 24, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #eceff4; padding: 10px;")
        main_layout.addWidget(header_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Project placement
        self.placement_combo = QComboBox()
        self.placement_combo.addItems(self.placement_list)
        self.placement_combo.setToolTip("Select the project placement folder")
        form_layout.addRow("Project Placement:", self.placement_combo)

        # Project type
        self.proj_type_combo = QComboBox()
        self.proj_type_combo.addItems(PROJECT_TYPES)
        self.proj_type_combo.setToolTip("Select the project type")
        form_layout.addRow("Project Type:", self.proj_type_combo)

        # Project name
        self.proj_name_edit = QLineEdit()
        self.proj_name_edit.setToolTip("Enter a valid project name (letters, numbers, underscores, hyphens)")
        form_layout.addRow("Project Name:", self.proj_name_edit)

        # Custom folders
        self.custom_folders_edit = QLineEdit()
        self.custom_folders_edit.setToolTip("Enter custom folder names separated by commas")
        form_layout.addRow("Custom Folders:", self.custom_folders_edit)

        # Auth choice
        self.auth_choice_combo = QComboBox()
        self.auth_choice_combo.addItems(AUTH_CHOICES)
        self.auth_choice_combo.setToolTip("Select authentication options")
        form_layout.addRow("Authentication Setup:", self.auth_choice_combo)

        # Template combo
        self.template_combo = QComboBox()
        self.template_combo.addItems(TEMPLATE_OPTIONS)
        self.template_combo.setToolTip("Select a project template (e.g., TypeScript, Tailwind CSS)")
        form_layout.addRow("Template:", self.template_combo)

        # Additional dependencies
        deps_layout = QHBoxLayout()
        self.deps_checkboxes = []
        for dep in ADDITIONAL_DEPENDENCIES:
            cb = QCheckBox(dep)
            cb.setToolTip(f"Include {dep} as an additional dependency")
            deps_layout.addWidget(cb)
            self.deps_checkboxes.append(cb)
        form_layout.addRow("Additional Dependencies:", deps_layout)

        # Environment variables
        self.env_vars_edit = QTextEdit()
        self.env_vars_edit.setPlaceholderText("Enter environment variables (e.g., KEY=VALUE), one per line")
        self.env_vars_edit.setToolTip("Define any environment variables for your project")
        form_layout.addRow("Environment Variables:", self.env_vars_edit)

        # GitHub integration
        self.github_checkbox = QCheckBox("Initialize GitHub Repository")
        self.github_checkbox.setToolTip("Automatically create a GitHub repository and push the initial commit")
        form_layout.addRow("GitHub Integration:", self.github_checkbox)

        main_layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton(QIcon(os.path.join(BASE_DIR, "icons", "create.png")), "Create Project")
        self.create_btn.setFixedHeight(40)
        self.create_btn.setToolTip("Click to start project creation")
        self.create_btn.clicked.connect(self.start_project_creation)
        btn_layout.addWidget(self.create_btn)

        self.cancel_btn = QPushButton(QIcon(os.path.join(BASE_DIR, "icons", "cancel.png")), "Cancel")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setToolTip("Cancel the project creation process")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_creation)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        main_layout.addWidget(self.log_text_edit)

        self.statusBar().showMessage("Ready")
        self.apply_theme(self.current_theme)

    def save_project_to_json(self, project_name, project_location):
        self.log_text_edit.append("Debug: Entering save_project_to_json.")
        print("Debug: Entering save_project_to_json.")

        self.log_text_edit.append(f"Debug: PROJECTS_FILE path -> {PROJECTS_FILE}")
        print(f"Debug: PROJECTS_FILE path -> {PROJECTS_FILE}")

        self.log_text_edit.append(f"Debug: Attempting to save -> name: {project_name}, location: {project_location}")
        print(f"Debug: Attempting to save -> name: {project_name}, location: {project_location}")

        project_data = {
            "name": project_name,
            "location": project_location
        }

        # Load existing projects (if any)
        projects = []
        if os.path.exists(PROJECTS_FILE):
            self.log_text_edit.append("Debug: projects.json exists, attempting to load.")
            print("Debug: projects.json exists, attempting to load.")
            try:
                with open(PROJECTS_FILE, "r") as f:
                    projects = json.load(f)
                self.log_text_edit.append(f"Debug: Loaded existing projects -> {projects}")
                print(f"Debug: Loaded existing projects -> {projects}")
            except json.JSONDecodeError as e:
                self.log_text_edit.append(f"Debug: JSON decode error: {e}, overwriting file.")
                print(f"Debug: JSON decode error: {e}, overwriting file.")
                projects = []
        else:
            self.log_text_edit.append("Debug: projects.json does not exist, creating a new one.")
            print("Debug: projects.json does not exist, creating a new one.")

        # Append new project to the list
        projects.append(project_data)
        self.log_text_edit.append(f"Debug: Final projects list -> {projects}")
        print(f"Debug: Final projects list -> {projects}")

        # Write back to projects.json
        try:
            with open(PROJECTS_FILE, "w") as f:
                json.dump(projects, f, indent=4)
            self.log_text_edit.append(f"Debug: Successfully wrote to {PROJECTS_FILE}")
            print(f"Debug: Successfully wrote to {PROJECTS_FILE}")
        except Exception as e:
            self.log_text_edit.append(f"Debug: Failed to write to {PROJECTS_FILE}: {e}")
            print(f"Debug: Failed to write to {PROJECTS_FILE}: {e}")

        self.log_text_edit.append(f"Project '{project_name}' saved to {PROJECTS_FILE}.")

    @Slot()
    def start_project_creation(self):
        self.log_text_edit.append("Debug: start_project_creation called.")
        print("Debug: start_project_creation called.")

        placement = self.placement_combo.currentText()
        project_type = self.proj_type_combo.currentText()
        project_name = self.proj_name_edit.text().strip()
        custom_folders = self.custom_folders_edit.text().strip()
        auth_choice = self.auth_choice_combo.currentText()
        template_choice = self.template_combo.currentText()
        github_integration = self.github_checkbox.isChecked()

        # Validate project name
        if not project_name or not is_valid_project_name(project_name):
            QMessageBox.warning(
                self,
                "Input Error",
                "Please enter a valid project name (letters, numbers, underscores, hyphens)."
            )
            return

        # Collect additional dependencies
        extra_deps = [cb.text() for cb in self.deps_checkboxes if cb.isChecked()]

        # Parse environment variables
        env_vars = {}
        for line in self.env_vars_edit.toPlainText().splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

        # Validate 
        if not placement or not project_type or not project_name or not auth_choice:
            QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return

        # Update UI
        self.log_text_edit.append("Starting project creation...")
        self.create_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.statusBar().showMessage("Project creation in progress...")

        # final project location
        project_location = os.path.join(self.base_dir, placement, project_name)

        self.log_text_edit.append(f"Debug: Computed project_location -> {project_location}")
        print(f"Debug: Computed project_location -> {project_location}")

        # Create and start the worker thread
        self.worker = ProjectCreatorWorker(
            self.base_dir,
            placement,
            project_type,
            project_name,
            custom_folders,
            auth_choice,
            template_choice,
            extra_deps,
            env_vars,
            github_integration
        )
        self.worker.log_signal.connect(self.update_log)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(
            lambda: self.project_creation_finished(project_name, project_location)
        )
        self.worker.start()

    def project_creation_finished(self, project_name, project_location):
        self.log_text_edit.append("Debug: project_creation_finished triggered.")
        print("Debug: project_creation_finished triggered.")

        # Save project to JSON
        self.save_project_to_json(project_name, project_location)

        self.log_text_edit.append("Project creation process finished.")
        self.create_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.statusBar().showMessage("Finished")

    @Slot()
    def cancel_creation(self):
        self.log_text_edit.append("Debug: cancel_creation called.")
        print("Debug: cancel_creation called.")

        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.log_text_edit.append("Project creation canceled by user.")
            self.progress_bar.setValue(0)
            self.create_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
            self.statusBar().showMessage("Canceled")

    @Slot(str)
    def update_log(self, message):
        self.log_text_edit.append(message)

    @Slot(int)
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def open_dashboard(self):
        self.log_text_edit.append("Debug: open_dashboard called.")
        print("Debug: open_dashboard called.")

        self.dashboard = Dashboard()
        self.dashboard.show()
        self.close()

    @Slot()
    def open_settings_dialog(self):
        self.log_text_edit.append("Debug: open_settings_dialog called.")
        print("Debug: open_settings_dialog called.")

        dialog = SettingsDialog(self.base_dir, self.placement_list, self)
        if dialog.exec() == QDialog.Accepted:
            new_base_dir, new_placements = dialog.get_values()
            if new_base_dir:
                self.base_dir = new_base_dir
            if new_placements:
                self.placement_list = new_placements
                self.placement_combo.clear()
                self.placement_combo.addItems(self.placement_list)
            self.statusBar().showMessage("Settings updated")

    @Slot()
    def toggle_theme(self):
        """
        Toggles between Dark and Light themes.
        """
        self.log_text_edit.append("Debug: toggle_theme called.")
        print("Debug: toggle_theme called.")

        if self.current_theme == "Dark":
            self.current_theme = "Light"
        else:
            self.current_theme = "Dark"
        self.apply_theme(self.current_theme)
        self.statusBar().showMessage("Theme toggled")

    def apply_theme(self, theme_name):
        """
        Apply a selected theme's colors to the main window.
        """
        self.log_text_edit.append(f"Debug: apply_theme called with {theme_name}.")
        print(f"Debug: apply_theme called with {theme_name}.")

        theme = self.themes.get(theme_name, self.themes["Dark"])
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme["background"]};
            }}
            QLabel {{
                color: {theme["text"]};
            }}
            QLineEdit, QComboBox, QTextEdit, QProgressBar {{
                background-color: {theme["input_background"]};
                color: {theme["input_text"]};
                border: 1px solid {theme["input_background"]};
                padding: 5px;
                border-radius: 4px;
            }}
            QPushButton {{
                background-color: {theme["button_background"]};
                color: {theme["text"]};
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme["button_hover"]};
            }}
            QProgressBar::chunk {{
                background-color: {theme["progress_bar"]};
                border-radius: 2px;
            }}
        """)
        self.current_theme = theme_name
        self.statusBar().showMessage(f"Theme changed to {theme_name}")

    def save_template(self):
        self.log_text_edit.append("Debug: save_template called.")
        print("Debug: save_template called.")

        template = {
            "placement": self.placement_combo.currentText(),
            "project_type": self.proj_type_combo.currentText(),
            "auth_choice": self.auth_choice_combo.currentText(),
            "template_choice": self.template_combo.currentText(),
            "custom_folders": self.custom_folders_edit.text(),
            "env_vars": self.env_vars_edit.toPlainText(),
            "extra_deps": [cb.isChecked() for cb in self.deps_checkboxes],
            "github_integration": self.github_checkbox.isChecked()
        }
        templates = {}
        if os.path.exists(TEMPLATE_STORAGE_FILE):
            with open(TEMPLATE_STORAGE_FILE, "r") as f:
                templates = json.load(f)

        # If no project name, store it under "default_template"
        key_name = self.proj_name_edit.text().strip() or "default_template"
        templates[key_name] = template

        with open(TEMPLATE_STORAGE_FILE, "w") as f:
            json.dump(templates, f, indent=4)

        self.statusBar().showMessage("Template saved")
        self.log_text_edit.append("Template saved.")

    def load_template(self):
        self.log_text_edit.append("Debug: load_template called.")
        print("Debug: load_template called.")

        if not os.path.exists(TEMPLATE_STORAGE_FILE):
            QMessageBox.information(self, "No Templates", "No templates have been saved yet.")
            return

        with open(TEMPLATE_STORAGE_FILE, "r") as f:
            templates = json.load(f)

        if templates:
            # Just load the first template in the dictionary
            template = next(iter(templates.values()))
            self.placement_combo.setCurrentText(template.get("placement", ""))
            self.proj_type_combo.setCurrentText(template.get("project_type", ""))
            self.auth_choice_combo.setCurrentText(template.get("auth_choice", ""))
            self.template_combo.setCurrentText(template.get("template_choice", ""))
            self.custom_folders_edit.setText(template.get("custom_folders", ""))
            self.env_vars_edit.setPlainText(template.get("env_vars", ""))

            deps_flags = template.get("extra_deps", [False] * len(self.deps_checkboxes))
            for cb, flag in zip(self.deps_checkboxes, deps_flags):
                cb.setChecked(flag)

            self.github_checkbox.setChecked(template.get("github_integration", False))
            self.statusBar().showMessage("Template loaded")
            self.log_text_edit.append("Template loaded.")
        else:
            QMessageBox.information(self, "No Templates", "No templates found in storage.")

    def show_help(self):
        """
        Display the user guide/help dialog.
        """
        self.log_text_edit.append("Debug: show_help called.")
        print("Debug: show_help called.")

        help_dialog = HelpDialog(self)
        help_dialog.exec()

    def open_dependency_manager(self):
        """
        Open the dependency manager dialog.
        """
        self.log_text_edit.append("Debug: open_dependency_manager called.")
        print("Debug: open_dependency_manager called.")

        dlg = DependencyManagerDialog(self)
        dlg.exec()

    def open_backup_restore(self):
        """
        Open the backup/restore dialog.
        """
        self.log_text_edit.append("Debug: open_backup_restore called.")
        print("Debug: open_backup_restore called.")

        dlg = BackupRestoreDialog(self)
        dlg.exec()
