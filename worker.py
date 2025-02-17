import os
import re
import json
import subprocess
import shutil
import time
import logging
from PySide6.QtCore import QThread, Signal

def is_valid_project_name(name: str) -> bool:
    return bool(re.match(r'^[\w\-]+$', name))

def run_command(command, cwd, description, retry=1):
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

class ProjectCreatorWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int)
    finished_signal = Signal()

    def __init__(self, base_dir, placement, project_type, project_name, custom_folders,
                 auth_choice, template_choice, extra_deps, env_vars, github_integration):
        super().__init__()
        self.base_dir = base_dir
        self.placement = placement
        self.project_type = project_type
        self.project_name = project_name
        self.custom_folders = custom_folders
        self.auth_choice = auth_choice
        self.template_choice = template_choice
        self.extra_deps = extra_deps
        self.env_vars = env_vars
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
''')
        self.log_signal.emit("Created abort script")
        self.progress_signal.emit(85)

    def _handle_github_integration(self, project_path):
        if self.github_integration:
            self.log_signal.emit("Creating GitHub repository and pushing initial commit...")
            try:
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
        try:
            subprocess.Popen("npm run dev", cwd=project_path, shell=True)
            self.log_signal.emit("Development server started (non-blocking).")
        except Exception as e:
            self.log_signal.emit("Error starting development server: " + str(e))
        self.progress_signal.emit(95)
