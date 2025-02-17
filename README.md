Sir, here is the updated "About Me" text reflecting the new features in this version:

---

# Vite Magic

**Vite Magic** is a desktop application built with Python and PySide6 that automates the creation of React and Next.js projects. It streamlines the process of setting up new projects by handling dependency installation, authentication configuration (Clerk and Firebase), and custom folder creation—all through a user-friendly graphical interface.

![icon-for-an-app-which-generates-vite-code-removebg-preview](https://github.com/user-attachments/assets/adb7ed36-e467-4c72-b35a-328df2477dab)

---

## New Features in This Version

- **Enhanced User Interface**:  
  - **Icons & Tooltips**: Intuitive icons and informative tooltips on buttons and inputs guide you through every step.
  - **Dark/Light Theme**: Easily switch between dark and light modes to suit your preference.
  - **Responsive Layout**: Optimized layout that adapts seamlessly to various window sizes.

- **Expanded Project Creation Options**:  
  - **Template Selection**: Choose from a variety of templates including TypeScript, JavaScript, and Tailwind CSS for more tailored project setups.
  - **Dependency Management**: Option to select additional dependencies (e.g., Redux, React Router) during project creation.
  - **Environment Variables**: Directly add environment variables (like API keys) as part of the setup process.
  - **Git Integration**: Automatically initialize a Git repository, with options to create and push to a GitHub repository.
  - **Project Templates**: Save and load custom project templates for repetitive tasks.

- **Improved Error Handling and Performance**:  
  - **Validation & Detailed Error Messages**: Enhanced input validation and informative error messages guide you to quickly resolve issues.
  - **Background Processing**: Long-running tasks execute in the background, ensuring the interface remains responsive with detailed progress feedback.
  - **Optimized Code Base**: Modular, reusable functions and robust logging improve maintainability and troubleshooting.

- **Additional Quality-of-Life Enhancements**:  
  - **Abort Script**: A built-in Python script allows you to easily delete a project if needed.
  - **VS Code Integration**: Automatically open the newly created project in VS Code for immediate development.

---

## Screenshots

![image](https://github.com/user-attachments/assets/44d4a886-5fb8-4b59-a2fb-87169e730f7d)

![image](https://github.com/user-attachments/assets/79f7f045-bd6b-4ef8-a1e6-8132216117a7)

![image](https://github.com/user-attachments/assets/a4247afd-7869-4b52-aa8e-88db515b07e6)

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
   - Navigate to `Settings > Edit Project Settings` to customize your base directory and project placements.

3. **Create a New Project**:
   - Fill in the required fields:
     - **Project Placement**: Select where the project will be created.
     - **Project Type**: Choose between React, Next.js, or Vue (with additional template options such as TypeScript, Tailwind CSS, etc.).
     - **Project Name**: Enter a unique name for your project.
     - **Custom Folders**: Add any custom folders (comma-separated) you wish to include.
     - **Authentication Setup**: Choose from Clerk, Firebase, both, or none.
     - **Extra Dependencies**: Optionally list additional dependencies (e.g., Redux, React Router).\n   - Click **Create Project** to initiate the setup process.

4. **Monitor Progress**:
   - A real-time progress bar and log output display the status of the project creation process.

5. **Open in VS Code**:
   - Upon successful creation, your project will automatically open in VS Code for immediate development.

6. **Abort a Project (Optional)**:
   - Use the included `AbortProject.py` script in the project directory to delete the project if required.

---

## Packaging the Application

To distribute **Vite Magic** as a standalone executable:

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
   - The executable is created in the `dist` folder.

---

## Contributing

Contributions are welcome! Please follow these steps if you'd like to contribute:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **PySide6**: For the powerful and flexible GUI framework.
- **Vite**: For the React project template.
- **Next.js**: For the Next.js project template.
- **Clerk** and **Firebase**: For authentication support.

---

## Support

For any issues or questions, please open an issue on GitHub or contact the maintainer.

---

Enjoy using **Vite Magic** and happy coding! 🚀

---
