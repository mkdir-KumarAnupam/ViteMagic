import os
import re
import json
import subprocess
import shutil
import time
import sys
import logging

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QComboBox, QPushButton, QTextEdit, QLabel,
    QProgressBar, QMessageBox, QDialog, QDialogButtonBox, QFileDialog, QCheckBox
)
from PySide6.QtCore import QThread, Signal, Slot, Qt
from PySide6.QtGui import QFont, QIcon

# ---------------- Constants ---------------- #
PROJECT_TYPES = ["React", "Next.js"]
AUTH_CHOICES = ["None", "clerk", "firebase", "both"]
TEMPLATE_OPTIONS = ["JavaScript", "TypeScript", "Tailwind CSS"]
ADDITIONAL_DEPENDENCIES = ["Redux", "React Router"]

TEMPLATE_STORAGE_FILE = "project_templates.json"

# ---------------- Logging Configuration ---------------- #
logging.basicConfig(filename="vite_magic.log", level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s")

# ---------------- Helper Functions ---------------- #
def is_valid_project_name(name: str) -> bool:
    # Allow alphanumerics, underscores, hyphens; adjust as needed.
    return bool(re.match(r'^[\w\-]+$', name))

def run_command(command, cwd, description, retry=1):
    """Helper to run subprocess commands with basic retry logic."""
    for attempt in range(retry):
        try:
            logging.info(f"Running: {command} in {cwd}")
            subprocess.run(command, cwd=cwd, shell=True, check=True)
            return
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during {description}: {e}")
            if attempt < retry - 1:
                time.sleep(1)
            else:
                raise

# ---------------- Project Creator Worker ---------------- #
class ProjectCreatorWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int)
    finished_signal = Signal()

    def __init__(self, base_dir, placement, project_type, project_name,
                 custom_folders, auth_choice, template_choice, extra_deps,
                 env_vars, github_integration):
        super().__init__()
        self.base_dir = base_dir
        self.placement = placement
        self.project_type = project_type
        self.project_name = project_name
        self.custom_folders = custom_folders
        self.auth_choice = auth_choice
        self.template_choice = template_choice
        self.extra_deps = extra_deps
        self.env_vars = env_vars  # Expected as dict
        self.github_integration = github_integration

    def run(self):
        try:
            self._create_base_dir()
            project_folder = self._create_project_folder()
            project_path = os.path.join(project_folder, self.project_name)
            if os.path.exists(project_path):
                self.log_signal.emit("Error: Project folder already exists.")
                self.progress_signal.emit(100)
                self.finished_signal.emit()
                return

            self._create_project(project_folder, project_path)
            self._install_dependencies(project_path)
            self._setup_authentication(project_path)
            self._install_extra_dependencies(project_path)
            self._create_git_repo(project_path)
            self._create_custom_folders(project_path)
            self._create_readme(project_path)
            self._update_index_html(project_path)
            self._create_abort_script(project_path)
            self._handle_github_integration(project_path)
            self._open_in_vscode(project_path)
            self._start_dev_server(project_path)
            self.progress_signal.emit(100)
            self.log_signal.emit("Project setup complete!")
        except subprocess.CalledProcessError as e:
            self.log_signal.emit(f"Subprocess error: {e}")
            logging.error(f"Subprocess error: {e}")
        except Exception as e:
            self.log_signal.emit(f"Unexpected error: {e}")
            logging.exception("Unexpected error")
        finally:
            self.finished_signal.emit()

    def _create_base_dir(self):
        os.makedirs(self.base_dir, exist_ok=True)
        self.log_signal.emit(f"Created base directory: {self.base_dir}")
        self.progress_signal.emit(5)

    def _create_project_folder(self):
        project_folder = os.path.join(self.base_dir, self.placement)
        os.makedirs(project_folder, exist_ok=True)
        self.log_signal.emit(f"Using project folder: {project_folder}")
        self.progress_signal.emit(10)
        return project_folder

    def _create_project(self, project_folder, project_path):
        self.log_signal.emit(f"Creating {self.project_type} project with template: {self.template_choice}...")
        # === Best Option to Avoid Vite Prompt ===
        if self.project_type.lower() == "react":
            cmd = f"echo {self.project_name} | npm create vite@latest {self.project_name} -- --template react"
            run_command(cmd, project_folder, "create react project", retry=2)
        else:
            cmd = f"npx create-next-app@latest {self.project_name}"
            run_command(cmd, project_folder, "create Next.js project", retry=2)
        self.progress_signal.emit(20)

    def _install_dependencies(self, project_path):
        self.log_signal.emit("Installing dependencies...")
        run_command("npm install", project_path, "npm install", retry=2)
        self.progress_signal.emit(30)

    def _setup_authentication(self, project_path):
        if self.auth_choice in ["clerk", "both"]:
            self.log_signal.emit("Setting up Clerk Authentication...")
            run_command("npm install @clerk/clerk-react", project_path, "install @clerk/clerk-react")
            env_path = os.path.join(project_path, ".env.local")
            with open(env_path, "a") as env_file:
                env_file.write("CLERK_API_KEY=your_api_key_here\n")
            self.progress_signal.emit(40)

        if self.auth_choice in ["firebase", "both"]:
            self.log_signal.emit("Setting up Firebase...")
            run_command("npm install firebase", project_path, "install firebase")
            with open(os.path.join(project_path, "firebaseConfig.js"), "w") as firebase_file:
                firebase_file.write("// Firebase configuration goes here")
            self.progress_signal.emit(50)
        # Handle any additional environment variables from UI
        if self.env_vars:
            self.log_signal.emit("Adding environment variables...")
            env_path = os.path.join(project_path, ".env.local")
            with open(env_path, "a") as env_file:
                for key, value in self.env_vars.items():
                    env_file.write(f"{key}={value}\n")
            self.progress_signal.emit(55)

    def _install_extra_dependencies(self, project_path):
        if self.extra_deps:
            self.log_signal.emit("Installing additional dependencies: " + ", ".join(self.extra_deps))
            for dep in self.extra_deps:
                run_command(f"npm install {dep.lower()}", project_path, f"install {dep}")
            self.progress_signal.emit(60)

    def _create_git_repo(self, project_path):
        self.log_signal.emit("Initializing Git repository...")
        run_command("git init", project_path, "git init")
        self.progress_signal.emit(65)

    def _create_custom_folders(self, project_path):
        if self.custom_folders.strip():
            folders = [folder.strip() for folder in self.custom_folders.split(",") if folder.strip()]
            for folder in folders:
                folder_path = os.path.join(project_path, folder)
                os.makedirs(folder_path, exist_ok=True)
                self.log_signal.emit(f"Created custom folder: {folder}")
            self.progress_signal.emit(70)

    def _create_readme(self, project_path):
        with open(os.path.join(project_path, "README.md"), "w") as readme:
            readme.write("Completed creation of the project")
        self.log_signal.emit("Created README.md")
        self.progress_signal.emit(75)

    def _update_index_html(self, project_path):
        index_html_path = os.path.join(
            project_path,
            "index.html" if self.project_type.lower() == "react" else "public/index.html"
        )
        if os.path.exists(index_html_path):
            with open(index_html_path, "r") as file:
                content = file.read()
            content = content.replace("Vite App", self.project_name)
            with open(index_html_path, "w") as file:
                file.write(content)
            self.log_signal.emit("Updated index.html with project name")
        self.progress_signal.emit(80)

    def _create_abort_script(self, project_path):
        with open(os.path.join(project_path, "AbortProject.py"), "w") as abort_script:
            abort_script.write(
                '''import os
import shutil
import time

def abort_project():
    project_path = os.path.dirname(os.path.abspath(__file__))
    confirm = input("Hey, would you like to delete this project? (yes/y): ").strip().lower()
    if confirm in ["yes", "y"]:
        time.sleep(1)
        shutil.rmtree(project_path, ignore_errors=True)
        print("Project deleted successfully.")
    else:
        print("Project deletion aborted.")

if __name__ == "__main__":
    abort_project()
'''
            )
        self.log_signal.emit("Created abort script")
        self.progress_signal.emit(85)

    def _handle_github_integration(self, project_path):
        if self.github_integration:
            self.log_signal.emit("Creating GitHub repository and pushing initial commit...")
            try:
                # Requires GitHub CLI (gh) to be installed and authenticated.
                run_command("gh repo create {} --public --source . --remote origin".format(self.project_name),
                            project_path, "GitHub repo creation", retry=2)
                run_command("git add .", project_path, "git add")
                run_command("git commit -m 'Initial commit'", project_path, "git commit")
                run_command("git push -u origin master", project_path, "git push", retry=2)
                self.log_signal.emit("GitHub repository created and initial commit pushed.")
            except Exception as e:
                self.log_signal.emit("GitHub integration failed: " + str(e))
            self.progress_signal.emit(88)

    def _open_in_vscode(self, project_path):
        self.log_signal.emit("Opening project in VS Code...")
        run_command("code " + project_path, project_path, "open in VS Code")
        self.progress_signal.emit(92)

    def _start_dev_server(self, project_path):
        self.log_signal.emit("Starting development server...")
        run_command("npm run dev", project_path, "start dev server", retry=2)
        self.progress_signal.emit(95)

# ---------------- Settings Dialog ---------------- #
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

# ---------------- Help Dialog ---------------- #
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Guide")
        self.resize(500, 400)
        layout = QVBoxLayout(self)
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setPlainText(
            "Vite Magic User Guide:\n\n"
            "1. Fill in the required fields for project placement, type, name, and choose additional options.\n"
            "2. Use the extra options to select a template, additional dependencies, and set environment variables.\n"
            "3. Toggle between dark/light themes via the View menu.\n"
            "4. Use the Templates menu to save/load project templates for reuse.\n"
            "5. GitHub integration requires GitHub CLI (gh) to be installed and authenticated.\n"
            "6. Detailed logs are available in the log area and vite_magic.log file."
        )
        layout.addWidget(help_text)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

# ---------------- Main Window ---------------- #
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vite Magic")
        self.resize(900, 650)
        self.setMinimumSize(800, 600)

        # Configuration variables
        self.base_dir = "C:\\Projects"
        self.placement_list = ["PersonalProjects", "HackathonProjects", "AssignmentProjects", "ProfessionalProjects"]
        self.dark_theme = True  # Default theme

        # Top Menu Bar for settings, view (theme toggle), templates and help
        menu_bar = self.menuBar()

        settings_menu = menu_bar.addMenu(QIcon("icons/settings.png"), "Settings")
        edit_settings_action = settings_menu.addAction("Edit Project Settings")
        edit_settings_action.setIcon(QIcon("icons/edit.png"))
        edit_settings_action.triggered.connect(self.open_settings_dialog)

        view_menu = menu_bar.addMenu(QIcon("icons/view.png"), "View")
        toggle_theme_action = view_menu.addAction("Toggle Dark/Light Theme")
        toggle_theme_action.setIcon(QIcon("icons/theme.png"))
        toggle_theme_action.triggered.connect(self.toggle_theme)

        templates_menu = menu_bar.addMenu(QIcon("icons/template.png"), "Templates")
        save_template_action = templates_menu.addAction("Save Current Template")
        save_template_action.setIcon(QIcon("icons/save.png"))
        save_template_action.triggered.connect(self.save_template)
        load_template_action = templates_menu.addAction("Load Template")
        load_template_action.setIcon(QIcon("icons/load.png"))
        load_template_action.triggered.connect(self.load_template)

        help_menu = menu_bar.addMenu(QIcon("icons/help.png"), "Help")
        help_action = help_menu.addAction("User Guide")
        help_action.setIcon(QIcon("icons/info.png"))
        help_action.triggered.connect(self.show_help)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Header Label
        header_label = QLabel("Vite Magic")
        header_font = QFont("Arial", 24, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #eceff4; padding: 10px;")
        main_layout.addWidget(header_label)

        # Form layout for user inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.placement_combo = QComboBox()
        self.placement_combo.addItems(self.placement_list)
        self.placement_combo.setToolTip("Select the project placement folder")
        form_layout.addRow("Project Placement:", self.placement_combo)

        self.proj_type_combo = QComboBox()
        self.proj_type_combo.addItems(PROJECT_TYPES)
        self.proj_type_combo.setToolTip("Select the project type")
        form_layout.addRow("Project Type:", self.proj_type_combo)

        self.proj_name_edit = QLineEdit()
        self.proj_name_edit.setToolTip("Enter a valid project name (letters, numbers, underscores, hyphens)")
        form_layout.addRow("Project Name:", self.proj_name_edit)

        self.custom_folders_edit = QLineEdit()
        self.custom_folders_edit.setToolTip("Enter custom folder names separated by commas")
        form_layout.addRow("Custom Folders:", self.custom_folders_edit)

        self.auth_choice_combo = QComboBox()
        self.auth_choice_combo.addItems(AUTH_CHOICES)
        self.auth_choice_combo.setToolTip("Select authentication options")
        form_layout.addRow("Authentication Setup:", self.auth_choice_combo)

        # New: Template Selection
        self.template_combo = QComboBox()
        self.template_combo.addItems(TEMPLATE_OPTIONS)
        self.template_combo.setToolTip("Select a project template (e.g., TypeScript, Tailwind CSS)")
        form_layout.addRow("Template:", self.template_combo)

        # New: Additional Dependencies (as checkboxes)
        deps_layout = QHBoxLayout()
        self.deps_checkboxes = []
        for dep in ADDITIONAL_DEPENDENCIES:
            cb = QCheckBox(dep)
            cb.setToolTip(f"Include {dep} as an additional dependency")
            deps_layout.addWidget(cb)
            self.deps_checkboxes.append(cb)
        form_layout.addRow("Additional Dependencies:", deps_layout)

        # New: Environment Variables
        self.env_vars_edit = QTextEdit()
        self.env_vars_edit.setPlaceholderText("Enter environment variables (e.g., KEY=VALUE), one per line")
        self.env_vars_edit.setToolTip("Define any environment variables for your project")
        form_layout.addRow("Environment Variables:", self.env_vars_edit)

        # New: GitHub Integration
        self.github_checkbox = QCheckBox("Initialize GitHub Repository")
        self.github_checkbox.setToolTip("Automatically create a GitHub repository and push the initial commit")
        form_layout.addRow("GitHub Integration:", self.github_checkbox)

        main_layout.addLayout(form_layout)

        # Horizontal layout for control buttons
        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton(QIcon("icons/create.png"), "Create Project")
        self.create_btn.setFixedHeight(40)
        self.create_btn.setToolTip("Click to start project creation")
        self.create_btn.clicked.connect(self.start_project_creation)
        btn_layout.addWidget(self.create_btn)

        self.cancel_btn = QPushButton(QIcon("icons/cancel.png"), "Cancel")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setToolTip("Cancel the project creation process")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_creation)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)

        # Progress Bar (green filler only, no percentage text)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Log text area for output
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        main_layout.addWidget(self.log_text_edit)

        # Status Bar for real-time status updates
        self.statusBar().showMessage("Ready")

        self.worker = None

        self.apply_theme()  # Apply default (dark) theme

    @Slot()
    def open_settings_dialog(self):
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
        self.dark_theme = not self.dark_theme
        self.apply_theme()
        self.statusBar().showMessage("Theme toggled")

    def apply_theme(self):
        if self.dark_theme:
            self.setStyleSheet("""
                QMainWindow { background-color: #2e3440; }
                QLabel { color: #eceff4; }
                QLineEdit, QComboBox, QTextEdit, QProgressBar {
                    background-color: #3b4252;
                    color: #d8dee9;
                    border: 1px solid #4c566a;
                    padding: 5px;
                    border-radius: 4px;
                }
                QPushButton {
                    background-color: #5e81ac;
                    color: #eceff4;
                    border: none;
                    border-radius: 4px;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:hover { background-color: #81a1c1; }
                QProgressBar::chunk { background-color: #81a1c1; border-radius: 2px; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: #f0f0f0; }
                QLabel { color: #333; }
                QLineEdit, QComboBox, QTextEdit, QProgressBar {
                    background-color: #fff;
                    color: #333;
                    border: 1px solid #ccc;
                    padding: 5px;
                    border-radius: 4px;
                }
                QPushButton {
                    background-color: #007acc;
                    color: #fff;
                    border: none;
                    border-radius: 4px;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:hover { background-color: #005f99; }
                QProgressBar::chunk { background-color: #005f99; border-radius: 2px; }
            """)

    @Slot()
    def start_project_creation(self):
        placement = self.placement_combo.currentText()
        project_type = self.proj_type_combo.currentText()
        project_name = self.proj_name_edit.text().strip()
        custom_folders = self.custom_folders_edit.text().strip()
        auth_choice = self.auth_choice_combo.currentText()
        template_choice = self.template_combo.currentText()
        github_integration = self.github_checkbox.isChecked()

        # Validate project name
        if not project_name or not is_valid_project_name(project_name):
            QMessageBox.warning(self, "Input Error", "Please enter a valid project name (letters, numbers, underscores, hyphens).")
            return

        # Gather additional dependencies
        extra_deps = [cb.text() for cb in self.deps_checkboxes if cb.isChecked()]

        # Process environment variables (each line as KEY=VALUE)
        env_vars = {}
        for line in self.env_vars_edit.toPlainText().splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

        if not placement or not project_type or not project_name or not auth_choice:
            QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return

        self.log_text_edit.append("Starting project creation...")
        self.create_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.statusBar().showMessage("Project creation in progress...")

        self.worker = ProjectCreatorWorker(
            self.base_dir, placement, project_type,
            project_name, custom_folders, auth_choice,
            template_choice, extra_deps, env_vars, github_integration
        )
        self.worker.log_signal.connect(self.update_log)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.project_creation_finished)
        self.worker.start()

    @Slot()
    def cancel_creation(self):
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

    @Slot()
    def project_creation_finished(self):
        self.log_text_edit.append("Project creation process finished.")
        self.create_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.statusBar().showMessage("Finished")

    # ----- Template Save/Load Methods ----- #
    def save_template(self):
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
        # Load existing templates
        templates = {}
        if os.path.exists(TEMPLATE_STORAGE_FILE):
            with open(TEMPLATE_STORAGE_FILE, "r") as f:
                templates = json.load(f)
        # Use project name as key for template storage
        templates[self.proj_name_edit.text().strip() or "default_template"] = template
        with open(TEMPLATE_STORAGE_FILE, "w") as f:
            json.dump(templates, f, indent=4)
        self.statusBar().showMessage("Template saved")
        self.log_text_edit.append("Template saved.")

    def load_template(self):
        if not os.path.exists(TEMPLATE_STORAGE_FILE):
            QMessageBox.information(self, "No Templates", "No templates have been saved yet.")
            return
        with open(TEMPLATE_STORAGE_FILE, "r") as f:
            templates = json.load(f)
        # For simplicity, load the first template available
        if templates:
            template = next(iter(templates.values()))
            self.placement_combo.setCurrentText(template.get("placement", ""))
            self.proj_type_combo.setCurrentText(template.get("project_type", ""))
            self.auth_choice_combo.setCurrentText(template.get("auth_choice", ""))
            self.template_combo.setCurrentText(template.get("template_choice", ""))
            self.custom_folders_edit.setText(template.get("custom_folders", ""))
            self.env_vars_edit.setPlainText(template.get("env_vars", ""))
            # Update dependency checkboxes
            deps_flags = template.get("extra_deps", [False] * len(self.deps_checkboxes))
            for cb, flag in zip(self.deps_checkboxes, deps_flags):
                cb.setChecked(flag)
            self.github_checkbox.setChecked(template.get("github_integration", False))
            self.statusBar().showMessage("Template loaded")
            self.log_text_edit.append("Template loaded.")
        else:
            QMessageBox.information(self, "No Templates", "No templates found in storage.")

    def show_help(self):
        help_dialog = HelpDialog(self)
        help_dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
