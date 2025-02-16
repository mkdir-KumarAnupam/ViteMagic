**Vite Magic**, which users can download and use directly. This version focuses on how users can download, install, and use the application without needing to worry about Python or dependencies.

---

# Vite Magic - Project Creator

![Vite Magic Logo](your_logo.png)

**Vite Magic** is a desktop application that automates the creation of React and Next.js projects. It simplifies the process of setting up a new project, installing dependencies, configuring authentication (Clerk and Firebase), and creating custom folders. With its user-friendly GUI, you can create and manage projects in just a few clicks!

---

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

## Download and Installation

### Prerequisites

- **Node.js and npm**: Required for React/Next.js project setup. Download and install from [nodejs.org](https://nodejs.org/).
- **VS Code (Optional)**: Recommended for opening the project after creation. Download from [code.visualstudio.com](https://code.visualstudio.com/).

### Steps

1. **Download the Application**:
   - Download the latest release of **Vite Magic** from the [Releases page](https://github.com/your-username/vite-magic/releases).

2. **Run the Application**:
   - **Windows**: Double-click the `ViteMagic.exe` file.
   - **macOS/Linux**: Open the terminal, navigate to the downloaded file, and run:
     ```bash
     ./ViteMagic
     ```

3. **Configure Settings (Optional)**:
   - Go to `Settings > Edit Project Settings` to configure the base directory and project placements.

---

## Usage

1. **Launch the Application**:
   - Run the downloaded executable to start **Vite Magic**.

2. **Create a New Project**:
   - Fill in the required fields:
     - **Project Placement**: Select where the project will be created.
     - **Project Type**: Choose between React or Next.js.
     - **Project Name**: Enter a name for your project.
     - **Custom Folders**: Add any custom folders (comma-separated).
     - **Authentication Setup**: Choose between Clerk, Firebase, both, or none.
   - Click **Create Project** to start the process.

3. **Monitor Progress**:
   - The progress bar and log output will show the status of the project creation.

4. **Open in VS Code**:
   - Once the project is created, it will automatically open in VS Code.

5. **Abort a Project (Optional)**:
   - Run the `AbortProject.py` script in the project directory to delete the project if needed.

---

## Screenshots

![Main Window](screenshots/main_window.png) <!-- Replace with actual screenshot -->
![Settings Dialog](screenshots/settings_dialog.png) <!-- Replace with actual screenshot -->

---

## Frequently Asked Questions (FAQ)

### 1. **What is the base directory?**
   - The base directory is the root folder where all your projects will be created. You can configure it in the **Settings** menu.

### 2. **Can I use this without VS Code?**
   - Yes, the application will still create the project, but it won't automatically open it in VS Code.

### 3. **How do I set up Clerk or Firebase?**
   - After creating the project, you’ll need to add your API keys to the generated `.env.local` (for Clerk) or `firebaseConfig.js` (for Firebase) files.

### 4. **Can I delete a project after creating it?**
   - Yes, use the `AbortProject.py` script included in the project directory to delete it.

---

## Contributing

If you'd like to contribute to the development of **Vite Magic**, follow these steps:

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

### Notes:
- Replace placeholders like `your-username`, `your_logo.png`, and `screenshots/main_window.png` with actual values.
- Add screenshots of your application to the `screenshots` folder and link them in the README.
- Update the `LICENSE` file with your preferred license (e.g., MIT, Apache, etc.).

Let me know if you need further adjustments! 😊
