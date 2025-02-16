Vite Magic is a desktop application built with Python and PySide6 that automates the creation of React and Next.js projects. It simplifies the process of setting up a new project, installing dependencies, configuring authentication (Clerk and Firebase), and creating custom folders. The app also includes a user-friendly GUI for ease of use.

![icon-for-an-app-which-generates-vite-code-removebg-preview](https://github.com/user-attachments/assets/adb7ed36-e467-4c72-b35a-328df2477dab)


## Features

- **Project Creation**:
  - Create React or Next.js projects with a single click.
  - Automatically install dependencies using `npm`.

- **Authentication Setup**:
  - Supports Clerk and Firebase authentication.
  - Automatically installs required packages and configures environment files.

- **Custom Folders**:
  - Add custom folders to your project during creation.

- **Abort Script**:
  - Includes a Python script to easily delete the project if needed.

- **VS Code Integration**:
  - Automatically opens the project in VS Code after creation.

- **Progress Tracking**:
  - Real-time progress bar and log output to track the project creation process.

- **Customizable Settings**:
  - Configure the base directory and project placements.

---

## Screenshots

![image](https://github.com/user-attachments/assets/4b0971ae-7d65-479b-a680-821d8e6b6137)
->
![image](https://github.com/user-attachments/assets/cb56a0d5-afb1-416e-991c-32263d867b3c)


---

## Installation

### Prerequisites

- **Python 3.8 or higher**
- **Node.js and npm** (for React/Next.js project setup)
- **Git** (optional, for initializing a Git repository)

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mkdir-KumarAnupam/vite-magic.git
   cd vite-magic
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python main.py
   ```

---

## Usage

1. **Launch the Application**:
   - Run `python main.py` to start the application.

2. **Configure Settings (Optional)**:
   - Go to `Settings > Edit Project Settings` to configure the base directory and project placements.

3. **Create a New Project**:
   - Fill in the required fields:
     - **Project Placement**: Select where the project will be created.
     - **Project Type**: Choose between React or Next.js.
     - **Project Name**: Enter a name for your project.
     - **Custom Folders**: Add any custom folders (comma-separated).
     - **Authentication Setup**: Choose between Clerk, Firebase, both, or none.
   - Click **Create Project** to start the process.

4. **Monitor Progress**:
   - The progress bar and log output will show the status of the project creation.

5. **Open in VS Code**:
   - Once the project is created, it will automatically open in VS Code.

6. **Abort a Project (Optional)**:
   - Run the `AbortProject.py` script in the project directory to delete the project if needed.

---

## Packaging the Application

To distribute the application as a standalone executable:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Create the Executable**:
   ```bash
   pyinstaller --onefile --windowed --icon=your_icon.ico main.py
   ```

   Replace `your_icon.ico` with the path to your custom icon.

3. **Locate the Executable**:
   - The executable will be created in the `dist` folder.

---

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **PySide6**: For the GUI framework.
- **Vite**: For the React project template.
- **Next.js**: For the Next.js project template.
- **Clerk** and **Firebase**: For authentication support.

---

## Support

If you encounter any issues or have questions, feel free to open an issue on GitHub or contact the maintainer.

---

Enjoy using **Vite Magic**! 🚀

---
