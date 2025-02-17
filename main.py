import sys
from PySide6.QtWidgets import QApplication
from dashboard import Dashboard

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec())