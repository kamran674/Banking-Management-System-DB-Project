# cbs_app_enhanced_complete.py - FINAL VERSION WITH CUSTOMER MODE
import sys, decimal
from PyQt5 import QtWidgets, QtCore, QtGui
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# ----------------------------
# DB CONFIG - CHANGE PASSWORD HERE
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Pass@0674',  # <-- SET YOUR MYSQL PASSWORD HERE
    'database': 'cbs_dbs',
    'autocommit': False
}


# ----------------------------

def db_connect():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None


# Utility: write audit log
def write_audit(cursor, operation, table, user, details):
    try:
        cursor.execute(
            "INSERT INTO AuditLog (Operation, TableAffected, UserName, Details) VALUES (%s,%s,%s,%s)",
            (operation, table, user, details)
        )
    except Exception as e:
        print(f"Audit log error: {e}")


# Utility: convert hex to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


# ----------------------------
# Loading Overlay Widget
class LoadingOverlay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.hide()
        self.angle = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_rotation)
        self.message = "Loading..."

    def show_loading(self, message="Loading..."):
        self.message = message
        self.setGeometry(self.parent().rect())
        self.show()
        self.timer.start(50)

    def hide_loading(self):
        self.hide()
        self.timer.stop()

    def update_rotation(self):
        self.angle = (self.angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(self.rect(), QtGui.QColor(15, 23, 32, 180))
        center = self.rect().center()

        painter.save()
        painter.translate(center)
        painter.rotate(self.angle)

        for i in range(12):
            if i % 3 == 0:
                painter.setPen(QtGui.QPen(QtGui.QColor("#0ea5a4"), 6))
            elif i % 3 == 1:
                painter.setPen(QtGui.QPen(QtGui.QColor("#7fe6d9"), 4))
            else:
                painter.setPen(QtGui.QPen(QtGui.QColor("#a7f3d0"), 2))
            painter.drawLine(0, -20, 0, -30)
            painter.rotate(30)
        painter.restore()

        painter.setPen(QtGui.QColor("#a7f3d0"))
        painter.setFont(QtGui.QFont("Segoe UI", 16, QtGui.QFont.Bold))
        text_rect = QtCore.QRect(center.x() - 100, center.y() + 40, 200, 30)
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, self.message)


# ----------------------------
# Enhanced Stylesheet with gradients and modern design
ENHANCED_STYLE = """
QMainWindow, QDialog, QWidget { 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0f1720, stop:1 #1e293b); 
    color: #f1f5f9; 
    font-family: 'Segoe UI', 'Arial', sans-serif; 
    font-size: 22px;
}

QGroupBox {
    border: 2px solid #0ea5a4;
    border-radius: 12px;
    margin-top: 15px;
    padding-top: 15px;
    background: rgba(15, 23, 32, 0.8);
    color: #a7f3d0;
    font-weight: bold;
    font-size: 20px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px 0 8px;
    font-size: 20px;
    color: #a7f3d0;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #0ea5a4, stop:1 #0d9488);
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 20px;
    color: white;
    font-weight: 700;
    border: none;
    min-height: 26px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #14b8b4, stop:1 #0ea5a4);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #0d9488, stop:1 #0c7c6b);
}

QPushButton#deleteBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #dc2626, stop:1 #b91c1c);
    color: white;
    font-weight: 700;
}
QPushButton#deleteBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ef4444, stop:1 #dc2626);
}

QPushButton#editBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #d97706, stop:1 #b45309);
    color: white;
    font-weight: 700;
}

QPushButton#editBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f59e0b, stop:1 #d97706);
}

QLineEdit, QComboBox, QTextEdit, QDateEdit { 
    background: rgba(7, 16, 20, 0.9);
    border: 2px solid #0ea5a4;
    padding: 12px 15px;
    font-size: 20px;
    color: #dbeafe;
    border-radius: 10px;
    selection-background-color: #0ea5a4;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 2px solid #7fe6d9;
    background: rgba(7, 16, 20, 1);
}

QTableWidget {
    background: #071014;
    alternate-background-color: #0a141a;
    gridline-color: #1e293b;
    border: none;
    border-radius: 8px;
    font-size: 18px;
}

QTableWidget::item {
    padding: 12px 8px;
    font-size: 17px;
    border-bottom: 1px solid #1e293b;
}

QTableWidget::item:selected {
    background: #0ea5a4;
    color: white;
}

QHeaderView::section { 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #063537, stop:1 #0ea5a4);
    color: white;
    padding: 12px 8px;
    border: none;
    font-size: 18px;
    font-weight: bold;
    border-radius: 0px;
}

QFrame#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #042a2a, stop:1 #064646);
    border-right: 3px solid #0ea5a4;
    min-width: 320px;
}

QPushButton#sideBtn { 
    text-align: left; 
    padding: 20px 25px;
    background: transparent; 
    border: none; 
    font-size: 20px;
    color: #cdeeea; 
    font-weight: 600;
    margin: 4px 8px;
    border-radius: 8px;
    min-height: 25px;
}

QPushButton#sideBtn:hover { 
    color: #ffffff; 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #064646, stop:1 #0ea5a4);
    border-left: 4px solid #7fe6d9;
    padding-left: 21px;
}

QPushButton#sideBtn:pressed {
    background: #0ea5a4;
}

QLabel#title {
    font-size: 26px;
    font-weight: 800;
    color: #a7f3d0;
}
"""

# Light theme style - IMPROVED
LIGHT_STYLE = """
QMainWindow, QDialog, QWidget { 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #f8fafc, stop:1 #e2e8f0); 
    color: #1e293b; 
    font-family: 'Segoe UI', 'Arial', sans-serif; 
    font-size: 22px;
}

QGroupBox {
    border: 2px solid #0ea5a4;
    border-radius: 12px;
    margin-top: 15px;
    padding-top: 15px;
    background: rgba(255, 255, 255, 0.95);
    color: #0f766e;
    font-weight: bold;
    font-size: 20px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px 0 8px;
    font-size: 20px;
    color: #0f766e;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #0ea5a4, stop:1 #0d9488);
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 20px;
    color: white;
    font-weight: 700;
    border: none;
    min-height: 26px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #14b8b4, stop:1 #0ea5a4);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #0d9488, stop:1 #0c7c6b);
}

QPushButton#deleteBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #dc2626, stop:1 #b91c1c);
    color: white;
    font-weight: 700;
}
QPushButton#deleteBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ef4444, stop:1 #dc2626);
}

QPushButton#editBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #d97706, stop:1 #b45309);
    color: white;
    font-weight: 700;
}

QPushButton#editBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f59e0b, stop:1 #d97706);
}

QLineEdit, QComboBox, QTextEdit, QDateEdit { 
    background: white;
    border: 2px solid #cbd5e1;
    padding: 12px 15px;
    font-size: 20px;
    color: #1e293b;
    border-radius: 10px;
    selection-background-color: #0ea5a4;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 2px solid #0ea5a4;
    background: white;
}

QTableWidget {
    background: white;
    alternate-background-color: #f8fafc;
    gridline-color: #e2e8f0;
    border: none;
    border-radius: 8px;
    font-size: 18px;
}

QTableWidget::item {
    padding: 12px 8px;
    font-size: 17px;
    border-bottom: 1px solid #e2e8f0;
    color: #1e293b;
}

QTableWidget::item:selected {
    background: #0ea5a4;
    color: white;
}

QHeaderView::section { 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #cffafe, stop:1 #0ea5a4);
    color: #1e293b;
    padding: 12px 8px;
    border: none;
    font-size: 18px;
    font-weight: bold;
    border-radius: 0px;
}

QFrame#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #f0fdfa, stop:1 #ccfbf1);
    border-right: 3px solid #0ea5a4;
    min-width: 320px;
}

QPushButton#sideBtn { 
    text-align: left; 
    padding: 20px 25px;
    background: transparent; 
    border: none; 
    font-size: 20px;
    color: #0f766e; 
    font-weight: 600;
    margin: 4px 8px;
    border-radius: 8px;
    min-height: 25px;
}

QPushButton#sideBtn:hover { 
    color: #134e4a; 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #ccfbf1, stop:1 #0ea5a4);
    border-left: 4px solid #0d9488;
    padding-left: 21px;
}

QPushButton#sideBtn:pressed {
    background: #0ea5a4;
    color: white;
}

QLabel#title {
    font-size: 26px;
    font-weight: 800;
    color: #0f766e;
}
"""


# ----------------------------
# Login Window with Customer/Admin Selection
class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FinFlow CBS - Login")
        self.setFixedSize(800, 800)
        self.setStyleSheet(ENHANCED_STYLE)
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        header = QtWidgets.QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #042a2a, stop:1 #0ea5a4);
                border-bottom: 3px solid #7fe6d9;
            }
        """)

        header_layout = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("🔐 FinFlow Pro - CBS")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: white;")
        header_layout.addWidget(title, alignment=QtCore.Qt.AlignCenter)
        header.setLayout(header_layout)

        main_layout.addWidget(header)

        center_widget = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout()
        center_layout.setContentsMargins(50, 40, 50, 40)

        welcome = QtWidgets.QLabel("Welcome Back!")
        welcome.setStyleSheet("font-size: 24px; font-weight: 700; color: #a7f3d0;")
        welcome.setAlignment(QtCore.Qt.AlignCenter)
        center_layout.addWidget(welcome)
        center_layout.addSpacing(20)

        # Login Type Selection
        login_type_box = QtWidgets.QGroupBox("Select Login Type")
        login_type_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #7c3aed;
                border-radius: 12px;
                background: rgba(15, 23, 32, 0.8);
            }
            QGroupBox::title {
                color: #8b5cf6;
                font-weight: bold;
            }
        """)

        login_type_layout = QtWidgets.QHBoxLayout()
        login_type_layout.setSpacing(20)

        # Radio buttons for login type
        self.login_type_group = QtWidgets.QButtonGroup()

        self.admin_radio = QtWidgets.QRadioButton("👨‍💼 Administrator")
        self.admin_radio.setChecked(True)
        self.admin_radio.setStyleSheet("""
            QRadioButton {
                font-size: 18px;
                font-weight: 600;
                color: #a7f3d0;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
            }
        """)

        self.customer_radio = QtWidgets.QRadioButton("👤 Customer")
        self.customer_radio.setStyleSheet("""
            QRadioButton {
                font-size: 18px;
                font-weight: 600;
                color: #a7f3d0;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
            }
        """)

        self.login_type_group.addButton(self.admin_radio, 1)
        self.login_type_group.addButton(self.customer_radio, 2)

        login_type_layout.addWidget(self.admin_radio)
        login_type_layout.addWidget(self.customer_radio)
        login_type_box.setLayout(login_type_layout)
        center_layout.addWidget(login_type_box)
        center_layout.addSpacing(20)

        form_box = QtWidgets.QGroupBox("Login Credentials")
        form_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #0ea5a4;
                border-radius: 12px;
                background: rgba(15, 23, 32, 0.8);
            }
            QGroupBox::title {
                color: #7fe6d9;
                font-weight: bold;
            }
        """)

        form_layout = QtWidgets.QFormLayout()
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        self.user_input = QtWidgets.QLineEdit()
       # self.user_input.setText("admin")
        self.user_input.setPlaceholderText("Enter username")
        self.user_input.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                font-size: 18px;
                border-radius: 8px;
            }
        """)

        self.pass_input = QtWidgets.QLineEdit()
        #self.pass_input.setText("admin123")
        self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pass_input.setPlaceholderText("Enter password")
        self.pass_input.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                font-size: 18px;
                border-radius: 8px;
            }
        """)

        form_layout.addRow("👤 Username:", self.user_input)
        form_layout.addRow("🔒 Password:", self.pass_input)
        form_box.setLayout(form_layout)
        center_layout.addWidget(form_box)
        center_layout.addSpacing(20)

        self.msg = QtWidgets.QLabel("")
        self.msg.setStyleSheet("color: #fca5a5; font-size: 16px;")
        self.msg.setAlignment(QtCore.Qt.AlignCenter)
        center_layout.addWidget(self.msg)
        center_layout.addSpacing(10)

        btn = QtWidgets.QPushButton("🚀 Login")
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #0ea5a4, stop:1 #7c3aed);
                border-radius: 10px;
                padding: 16px;
                font-size: 20px;
                font-weight: 700;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #14b8b4, stop:1 #8b5cf6);
            }
        """)
        btn.clicked.connect(self.do_login)
        center_layout.addWidget(btn)

        center_widget.setLayout(center_layout)
        main_layout.addWidget(center_widget)

        footer = QtWidgets.QLabel("© 2025 FinFlow Pro CBS | Secure Banking Solution")
        footer.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 15px;")
        footer.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(footer)

        self.setLayout(main_layout)

    def do_login(self):
        u = self.user_input.text().strip()
        p = self.pass_input.text().strip()

        if not u or not p:
            self.msg.setText("⚠️ Please enter username & password")
            return

        try:
            conn = db_connect()
            if conn is None:
                self.msg.setText("❌ Cannot connect to database")
                return

            cur = conn.cursor(dictionary=True)

            if self.admin_radio.isChecked():
                # Admin login
                cur.execute("SELECT * FROM AppUser WHERE Username=%s AND Password=%s", (u, p))
                row = cur.fetchone()

                if row:
                    self.msg.setText("✅ Admin login successful! Redirecting...")
                    QtCore.QTimer.singleShot(500, lambda: self.open_main_window(u, 'admin'))
                else:
                    self.msg.setText("❌ Invalid admin credentials")

            else:
                # Customer login
                cur.execute("SELECT * FROM Customer WHERE Name=%s AND Password=%s", (u, p))
                row = cur.fetchone()

                if row:
                    self.msg.setText("✅ Customer login successful! Redirecting...")
                    QtCore.QTimer.singleShot(500, lambda: self.open_main_window(u, 'customer', row['CustomerID']))
                else:
                    self.msg.setText("❌ Invalid customer credentials")

            cur.close()
            conn.close()

        except Exception as e:
            self.msg.setText(f"⚠️ Database Error: {str(e)}")

    def open_main_window(self, username, user_type, customer_id=None):
        try:
            if user_type == 'admin':
                self.main = EnhancedMainWindow(user=username, user_type=user_type)
                self.main.show()
                self.close()
            else:
                self.customer_dashboard = CustomerDashboardWindow(customer_id=customer_id, customer_name=username)
                self.customer_dashboard.show()
                self.close()
        except Exception as e:
            print("Error opening window:", e)
            self.msg.setText(f"❌ Error: {str(e)}")


# ----------------------------
# Customer Dashboard Window - COMPLETE FIXED VERSION
class CustomerDashboardWindow(QtWidgets.QMainWindow):
    def __init__(self, customer_id, customer_name):
        super().__init__()
        print(f"DEBUG: Creating CustomerDashboardWindow for {customer_name} (ID: {customer_id})")  # Debug line
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.setWindowTitle(f"FinFlow Pro - Customer Portal | Welcome, {customer_name}")
        self.resize(1400, 900)
        self.setStyleSheet(ENHANCED_STYLE)

        self.loading_overlay = LoadingOverlay(self)
        self.init_ui()

    def init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        v = QtWidgets.QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)
        central.setLayout(v)

        # Header
        header = QtWidgets.QFrame()
        header.setFixedHeight(120)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #042a2a, stop:1 #0ea5a4);
                border-bottom: 3px solid #7fe6d9;
            }
        """)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(30, 20, 30, 20)

        title_layout = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("🏦 Customer Banking Portal")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: white;")

        welcome = QtWidgets.QLabel(f"Welcome, {self.customer_name}")
        welcome.setStyleSheet("font-size: 18px; color: #a7f3d0;")

        title_layout.addWidget(title)
        title_layout.addWidget(welcome)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Profile Edit Button
        profile_btn = QtWidgets.QPushButton("👤 Edit Profile")
        profile_btn.setFixedSize(140, 45)
        profile_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3b82f6, stop:1 #1d4ed8);
                border-radius: 8px;
                font-size: 16px;
                color: white;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4f46e5, stop:1 #3730a3);
            }
        """)
        profile_btn.clicked.connect(self.edit_customer_profile)
        header_layout.addWidget(profile_btn)

        # Logout button
        logout_btn = QtWidgets.QPushButton("🚪 Logout")
        logout_btn.setFixedSize(120, 45)
        logout_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #ef4444, stop:1 #dc2626);
                border-radius: 8px;
                font-size: 16px;
                color: white;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #f87171, stop:1 #ef4444);
            }
        """)
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)

        header.setLayout(header_layout)
        v.addWidget(header)

        # Main content - USING SPLITTER FOR BETTER LAYOUT
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Left Panel - Account Summary
        left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(20, 20, 20, 20)

        # Quick Stats
        stats_box = QtWidgets.QGroupBox("📊 Current Stats")
        stats_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #0ea5a4;
                border-radius: 12px;
                background: rgba(15, 23, 32, 0.8);
            }
            QGroupBox::title {
                color: #0ea5a4;
                font-weight: bold;
            }
        """)

        stats_layout = QtWidgets.QVBoxLayout()
        stats_layout.setSpacing(15)

        # Account Count
        acc_count_widget = QtWidgets.QWidget()
        acc_count_layout = QtWidgets.QHBoxLayout()
        acc_count_icon = QtWidgets.QLabel("💳")
        acc_count_icon.setStyleSheet("font-size: 24px;")
        self.acc_count_label = QtWidgets.QLabel("0")
        self.acc_count_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #3b82f6;")
        acc_count_layout.addWidget(acc_count_icon)
        acc_count_layout.addWidget(QtWidgets.QLabel("Active Accounts:"))
        acc_count_layout.addStretch()
        acc_count_layout.addWidget(self.acc_count_label)
        acc_count_widget.setLayout(acc_count_layout)
        stats_layout.addWidget(acc_count_widget)

        # Total Balance
        balance_widget = QtWidgets.QWidget()
        balance_layout = QtWidgets.QHBoxLayout()
        balance_icon = QtWidgets.QLabel("💰")
        balance_icon.setStyleSheet("font-size: 24px;")
        self.balance_label = QtWidgets.QLabel("Rs 0.00")
        self.balance_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #10b981;")
        balance_layout.addWidget(balance_icon)
        balance_layout.addWidget(QtWidgets.QLabel("Total Balance:"))
        balance_layout.addStretch()
        balance_layout.addWidget(self.balance_label)
        balance_widget.setLayout(balance_layout)
        stats_layout.addWidget(balance_widget)

        # Today's Transactions
        today_tx_widget = QtWidgets.QWidget()
        today_tx_layout = QtWidgets.QHBoxLayout()
        today_tx_icon = QtWidgets.QLabel("💸")
        today_tx_icon.setStyleSheet("font-size: 24px;")
        self.today_tx_label = QtWidgets.QLabel("0")
        self.today_tx_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #f59e0b;")
        today_tx_layout.addWidget(today_tx_icon)
        today_tx_layout.addWidget(QtWidgets.QLabel("Today's Transactions:"))
        today_tx_layout.addStretch()
        today_tx_layout.addWidget(self.today_tx_label)
        today_tx_widget.setLayout(today_tx_layout)
        stats_layout.addWidget(today_tx_widget)

        stats_box.setLayout(stats_layout)
        left_layout.addWidget(stats_box)

        # Banking Information
        info_box = QtWidgets.QGroupBox("ℹ️ Rules & Regulation")
        info_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3b82f6;
                border-radius: 12px;
                background: rgba(15, 23, 32, 0.8);
            }
            QGroupBox::title {
                color: #3b82f6;
                font-weight: bold;
            }
        """)

        info_layout = QtWidgets.QVBoxLayout()
        info_text = QtWidgets.QLabel(
            "✅ Deposit: Add money to your own accounts\n\n"
            "✅ Withdraw: Take money from your own accounts\n\n"
            "✅ Transfer: Send money to other bank accounts\n\n"
            "💰 Daily withdrawal limit: Rs 50,000 per account\n\n"
            "💰 Daily transfer limit: Rs 100,000 per account\n\n"
            "📞 Contact support: 0800-12345 (24/7)"
        )
        info_text.setStyleSheet("color: #94a3b8; font-size: 16px; padding: 10px;")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_box.setLayout(info_layout)
        left_layout.addWidget(info_box)

        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        splitter.addWidget(left_panel)

        # Right Panel - Tabs for operations
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setContentsMargins(20, 20, 20, 20)

        # Tabs Widget
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #0ea5a4;
                border-radius: 8px;
                background: rgba(15, 23, 32, 0.8);
            }
            QTabBar::tab {
                background: #1e293b;
                color: #94a3b8;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 16px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: #0ea5a4;
                color: white;
            }
            QTabBar::tab:hover {
                background: #164e63;
            }
        """)

        # Tab 1: My Accounts
        accounts_tab = self.create_accounts_tab()
        self.tabs.addTab(accounts_tab, "🏦 My Accounts")

        # Tab 2: Banking Operations (Deposit, Withdraw, Transfer)
        operations_tab = self.create_banking_operations_tab()
        self.tabs.addTab(operations_tab, "🏧 Operations")

        # Tab 3: Transaction History
        history_tab = self.create_transaction_history_tab()
        self.tabs.addTab(history_tab, "📋 Transaction History")

        right_layout.addWidget(self.tabs)
        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)

        # Set splitter sizes (30% left, 70% right)
        splitter.setSizes([300, 1000])

        v.addWidget(splitter)

        # Footer
        footer = QtWidgets.QLabel("© 2025 FinFlow Pro CBS | Enterprice Banking solution                                                                Developed by Malik Kamran Ali")
        footer.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 15px; background: #042a2a;")
        footer.setAlignment(QtCore.Qt.AlignCenter)
        v.addWidget(footer)

        # Load initial data
        QtCore.QTimer.singleShot(100, self.load_customer_data)  # Load after UI shows

    def create_accounts_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Accounts Table
        self.accounts_table = QtWidgets.QTableWidget()
        self.accounts_table.setColumnCount(6)
        self.accounts_table.setHorizontalHeaderLabels(["Account No", "Type", "Balance", "Status", "Branch", "Created"])
        self.accounts_table.horizontalHeader().setStretchLastSection(True)
        self.accounts_table.setAlternatingRowColors(True)
        self.accounts_table.setMinimumHeight(300)

        layout.addWidget(self.accounts_table)

        # Refresh button
        refresh_btn = QtWidgets.QPushButton("🔄 Refresh Accounts")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #6b7280, stop:1 #4b5563);
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: 600;
                color: white;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #9ca3af, stop:1 #6b7280);
            }
        """)
        refresh_btn.clicked.connect(self.load_customer_data)
        layout.addWidget(refresh_btn)

        tab.setLayout(layout)
        return tab

    def create_banking_operations_tab(self):
        tab = QtWidgets.QWidget()

        # Create a scroll area for the entire tab
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout()
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(30)

        # Deposit Section
        deposit_box = QtWidgets.QGroupBox("💰 Deposit to Your Account")
        deposit_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #10b981;
                border-radius: 12px;
                background: rgba(15, 23, 32, 0.8);
                padding: 15px;
            }
            QGroupBox::title {
                color: #10b981;
                font-weight: bold;
                font-size: 18px;
                padding: 5px 15px;
                subcontrol-origin: margin;
                left: 10px;
            }
        """)

        deposit_layout = QtWidgets.QFormLayout()
        deposit_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        deposit_layout.setSpacing(15)
        deposit_layout.setContentsMargins(10, 20, 10, 10)

        # Account selection
        account_label = QtWidgets.QLabel("🏦 Select Your Account:")
        self.cust_deposit_account = QtWidgets.QComboBox()
        self.cust_deposit_account.setMinimumWidth(300)
        self.cust_deposit_account.setMaximumWidth(400)

        # Amount input
        amount_label = QtWidgets.QLabel("💵 Amount (Rs):")
        self.cust_deposit_amount = QtWidgets.QLineEdit()
        self.cust_deposit_amount.setPlaceholderText("Enter amount in Rs")
        self.cust_deposit_amount.setMaximumWidth(300)

        # Remark input
        remark_label = QtWidgets.QLabel("📝 Remark:")
        self.cust_deposit_remark = QtWidgets.QLineEdit()
        self.cust_deposit_remark.setPlaceholderText("Remark (optional)")
        self.cust_deposit_remark.setMaximumWidth(300)

        deposit_layout.addRow(account_label, self.cust_deposit_account)
        deposit_layout.addRow(amount_label, self.cust_deposit_amount)
        deposit_layout.addRow(remark_label, self.cust_deposit_remark)

        # Deposit button
        btn_deposit = QtWidgets.QPushButton("💰 Deposit Now")
        btn_deposit.setMinimumHeight(50)
        btn_deposit.setCursor(QtCore.Qt.PointingHandCursor)
        btn_deposit.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #10b981, stop:1 #059669);
                border-radius: 10px;
                padding: 15px;
                font-size: 18px;
                font-weight: 600;
                color: white;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #34d399, stop:1 #10b981);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #059669, stop:1 #047857);
                padding: 16px 14px 14px 16px;
            }
        """)
        btn_deposit.clicked.connect(self.customer_deposit)

        # Add button with proper alignment
        deposit_layout.addRow("", btn_deposit)

        # Align the button to the right
        deposit_layout.setAlignment(btn_deposit, QtCore.Qt.AlignCenter)

        deposit_box.setLayout(deposit_layout)
        scroll_layout.addWidget(deposit_box)

        # Withdraw Section
        withdraw_box = QtWidgets.QGroupBox("💸 Withdraw from Your Account")
        withdraw_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #f59e0b;
                border-radius: 12px;
                background: rgba(15, 23, 32, 0.8);
                padding: 15px;
            }
            QGroupBox::title {
                color: #f59e0b;
                font-weight: bold;
                font-size: 18px;
                padding: 5px 15px;
                subcontrol-origin: margin;
                left: 10px;
            }
        """)

        withdraw_layout = QtWidgets.QFormLayout()
        withdraw_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        withdraw_layout.setSpacing(15)
        withdraw_layout.setContentsMargins(10, 20, 10, 10)

        # Account selection
        withdraw_acc_label = QtWidgets.QLabel("🏦 Select Your Account:")
        self.cust_withdraw_account = QtWidgets.QComboBox()
        self.cust_withdraw_account.setMinimumWidth(300)
        self.cust_withdraw_account.setMaximumWidth(400)

        # Amount input
        withdraw_amount_label = QtWidgets.QLabel("💵 Amount (Rs):")
        self.cust_withdraw_amount = QtWidgets.QLineEdit()
        self.cust_withdraw_amount.setPlaceholderText("Enter amount in Rs")
        self.cust_withdraw_amount.setMaximumWidth(300)

        # Remark input
        withdraw_remark_label = QtWidgets.QLabel("📝 Remark:")
        self.cust_withdraw_remark = QtWidgets.QLineEdit()
        self.cust_withdraw_remark.setPlaceholderText("Remark (optional)")
        self.cust_withdraw_remark.setMaximumWidth(300)

        withdraw_layout.addRow(withdraw_acc_label, self.cust_withdraw_account)
        withdraw_layout.addRow(withdraw_amount_label, self.cust_withdraw_amount)
        withdraw_layout.addRow(withdraw_remark_label, self.cust_withdraw_remark)

        # Withdraw button
        btn_withdraw = QtWidgets.QPushButton("💸 Withdraw Now")
        btn_withdraw.setMinimumHeight(50)
        btn_withdraw.setCursor(QtCore.Qt.PointingHandCursor)
        btn_withdraw.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #f59e0b, stop:1 #d97706);
                border-radius: 10px;
                padding: 15px;
                font-size: 18px;
                font-weight: 600;
                color: white;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #fbbf24, stop:1 #f59e0b);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #d97706, stop:1 #b45309);
                padding: 16px 14px 14px 16px;
            }
        """)
        btn_withdraw.clicked.connect(self.customer_withdraw)

        withdraw_layout.addRow("", btn_withdraw)
        withdraw_layout.setAlignment(btn_withdraw, QtCore.Qt.AlignCenter)
        withdraw_box.setLayout(withdraw_layout)
        scroll_layout.addWidget(withdraw_box)

        # Transfer Section
        transfer_box = QtWidgets.QGroupBox("🔄 Transfer to Another Account")
        transfer_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3b82f6;
                border-radius: 12px;
                background: rgba(15, 23, 32, 0.8);
                padding: 15px;
            }
            QGroupBox::title {
                color: #3b82f6;
                font-weight: bold;
                font-size: 18px;
                padding: 5px 15px;
                subcontrol-origin: margin;
                left: 10px;
            }
        """)

        transfer_layout = QtWidgets.QFormLayout()
        transfer_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        transfer_layout.setSpacing(15)
        transfer_layout.setContentsMargins(10, 20, 10, 10)

        # From account selection
        from_label = QtWidgets.QLabel("🏦 From Your Account:")
        self.cust_transfer_from = QtWidgets.QComboBox()
        self.cust_transfer_from.setMinimumWidth(300)
        self.cust_transfer_from.setMaximumWidth(400)

        # To account input
        to_label = QtWidgets.QLabel("➡️ To Account Number:")
        self.cust_transfer_to = QtWidgets.QLineEdit()
        self.cust_transfer_to.setPlaceholderText("Enter recipient account number")
        self.cust_transfer_to.setMaximumWidth(300)

        # Amount input
        transfer_amount_label = QtWidgets.QLabel("💵 Amount (Rs):")
        self.cust_transfer_amount = QtWidgets.QLineEdit()
        self.cust_transfer_amount.setPlaceholderText("Enter amount in Rs")
        self.cust_transfer_amount.setMaximumWidth(300)

        # Remark input
        transfer_remark_label = QtWidgets.QLabel("📝 Remark:")
        self.cust_transfer_remark = QtWidgets.QLineEdit()
        self.cust_transfer_remark.setPlaceholderText("Remark (optional)")
        self.cust_transfer_remark.setMaximumWidth(300)

        transfer_layout.addRow(from_label, self.cust_transfer_from)
        transfer_layout.addRow(to_label, self.cust_transfer_to)
        transfer_layout.addRow(transfer_amount_label, self.cust_transfer_amount)
        transfer_layout.addRow(transfer_remark_label, self.cust_transfer_remark)

        # Transfer button
        btn_transfer = QtWidgets.QPushButton("🔄 Transfer Now")
        btn_transfer.setMinimumHeight(50)
        btn_transfer.setCursor(QtCore.Qt.PointingHandCursor)
        btn_transfer.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3b82f6, stop:1 #1d4ed8);
                border-radius: 10px;
                padding: 15px;
                font-size: 18px;
                font-weight: 600;
                color: white;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4f46e5, stop:1 #3730a3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1d4ed8, stop:1 #1e40af);
                padding: 16px 14px 14px 16px;
            }
        """)
        btn_transfer.clicked.connect(self.customer_transfer)

        transfer_layout.addRow("", btn_transfer)
        transfer_layout.setAlignment(btn_transfer, QtCore.Qt.AlignCenter)
        transfer_box.setLayout(transfer_layout)
        scroll_layout.addWidget(transfer_box)

        # Add stretch to push everything up
        scroll_layout.addStretch()

        scroll_widget.setLayout(scroll_layout)

        # Create scroll area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # Style the scroll area
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e293b;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #0ea5a4;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #14b8b4;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)

        # Set the scroll area as the main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        tab.setLayout(main_layout)

        return tab
    def create_transaction_history_tab(self):
        tab = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create scroll widget
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout()
        scroll_layout.setContentsMargins(10, 10, 10, 10)

        # Transaction Table
        self.transactions_table = QtWidgets.QTableWidget()
        self.transactions_table.setColumnCount(7)
        self.transactions_table.setHorizontalHeaderLabels(["ID", "From", "To", "Amount", "Type", "Remark", "Date"])
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setMinimumHeight(400)

        scroll_layout.addWidget(self.transactions_table)

        # Filter options
        filter_widget = QtWidgets.QWidget()
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.setContentsMargins(0, 10, 0, 10)

        filter_label = QtWidgets.QLabel("Filter by:")
        filter_label.setStyleSheet("color: #94a3b8; font-size: 14px;")

        self.filter_type_combo = QtWidgets.QComboBox()
        self.filter_type_combo.addItems(["All", "Deposit", "Withdrawal", "Transfer"])
        self.filter_type_combo.setMaximumWidth(150)

        self.filter_date_from = QtWidgets.QDateEdit()
        self.filter_date_from.setCalendarPopup(True)
        self.filter_date_from.setDate(QtCore.QDate.currentDate().addMonths(-1))
        self.filter_date_from.setMaximumWidth(150)

        self.filter_date_to = QtWidgets.QDateEdit()
        self.filter_date_to.setCalendarPopup(True)
        self.filter_date_to.setDate(QtCore.QDate.currentDate())
        self.filter_date_to.setMaximumWidth(150)

        filter_btn = QtWidgets.QPushButton("🔍 Apply Filter")
        filter_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3b82f6, stop:1 #1d4ed8);
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 600;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4f46e5, stop:1 #3730a3);
            }
        """)
        filter_btn.clicked.connect(self.filter_transactions)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(QtWidgets.QLabel("Type:"))
        filter_layout.addWidget(self.filter_type_combo)
        filter_layout.addWidget(QtWidgets.QLabel("From:"))
        filter_layout.addWidget(self.filter_date_from)
        filter_layout.addWidget(QtWidgets.QLabel("To:"))
        filter_layout.addWidget(self.filter_date_to)
        filter_layout.addWidget(filter_btn)
        filter_layout.addStretch()

        filter_widget.setLayout(filter_layout)
        scroll_layout.addWidget(filter_widget)

        # Refresh button
        refresh_btn = QtWidgets.QPushButton("🔄 Refresh Transactions")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #6b7280, stop:1 #4b5563);
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: 600;
                color: white;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #9ca3af, stop:1 #6b7280);
            }
        """)
        refresh_btn.clicked.connect(self.load_transaction_history)
        scroll_layout.addWidget(refresh_btn)

        scroll_widget.setLayout(scroll_layout)

        # Create scroll area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        main_layout.addWidget(scroll_area)
        tab.setLayout(main_layout)

        return tab
    def filter_transactions(self):
        self.load_transaction_history()

    def load_transaction_history(self):
        try:
            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor()

            # Build query with filters
            query = """
                SELECT t.TransID, 
                       COALESCE(t.FromAccount, 'N/A') as FromAcc,
                       COALESCE(t.ToAccount, 'N/A') as ToAcc,
                       t.Amount, t.Type, t.Remark, t.DateTime 
                FROM TRANSACTION t
                WHERE (t.FromAccount IN (SELECT AccountNo FROM Account WHERE CustomerID = %s)
                   OR t.ToAccount IN (SELECT AccountNo FROM Account WHERE CustomerID = %s))
            """
            params = [self.customer_id, self.customer_id]

            # Add type filter
            tx_type = self.filter_type_combo.currentText()
            if tx_type != "All":
                query += " AND t.Type = %s"
                params.append(tx_type)

            # Add date filter
            date_from = self.filter_date_from.date().toString("yyyy-MM-dd")
            date_to = self.filter_date_to.date().toString("yyyy-MM-dd")
            query += " AND DATE(t.DateTime) BETWEEN %s AND %s"
            params.extend([date_from, date_to])

            query += " ORDER BY t.DateTime DESC LIMIT 100"

            cur.execute(query, tuple(params))
            transactions = cur.fetchall()

            self.transactions_table.setRowCount(len(transactions))

            for i, row in enumerate(transactions):
                for j, value in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    if j == 3:  # Amount column
                        item.setForeground(QtGui.QColor("#f59e0b"))
                        try:
                            amount = float(value)
                            item.setText(f"Rs {amount:,.2f}")
                        except:
                            pass
                    elif j == 4:  # Type column
                        if value == 'Deposit':
                            item.setForeground(QtGui.QColor("#10b981"))
                        elif value == 'Withdrawal':
                            item.setForeground(QtGui.QColor("#ef4444"))
                        elif value == 'Transfer':
                            item.setForeground(QtGui.QColor("#3b82f6"))
                    self.transactions_table.setItem(i, j, item)

            cur.close()
            conn.close()

        except Exception as e:
            print("Error loading transaction history:", e)

    def load_customer_accounts_combo(self):
        if not hasattr(self, 'cust_deposit_account'):
            return

        self.cust_deposit_account.clear()
        self.cust_withdraw_account.clear()
        self.cust_transfer_from.clear()

        try:
            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor()
            cur.execute("""
                SELECT AccountNo, Type, Balance 
                FROM Account 
                WHERE CustomerID=%s AND Status='Active'
                ORDER BY AccountNo
            """, (self.customer_id,))
            accounts = cur.fetchall()

            for account in accounts:
                account_text = f"{account[0]} ({account[1]}) - Rs {account[2]:,.2f}"
                self.cust_deposit_account.addItem(account_text, account[0])
                self.cust_withdraw_account.addItem(account_text, account[0])
                self.cust_transfer_from.addItem(account_text, account[0])

            cur.close()
            conn.close()
        except Exception as e:
            print("Error loading customer accounts:", e)

    def load_customer_data(self):
        self.loading_overlay.show_loading("Loading your data...")
        try:
            print(f"DEBUG: Loading data for customer ID: {self.customer_id}")  # Debug line

            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.warning(self, "Error",
                                              "Cannot connect to database. Please try again.")
                return

            cur = conn.cursor()

            # Load summary data
            cur.execute("""
                SELECT 
                    COUNT(*) as account_count,
                    SUM(Balance) as total_balance
                FROM Account 
                WHERE CustomerID=%s AND Status='Active'
            """, (self.customer_id,))
            result = cur.fetchone()

            if result:
                account_count = result[0] or 0
                total_balance = result[1] or 0
                self.acc_count_label.setText(str(account_count))
                self.balance_label.setText(f"Rs {float(total_balance):,.2f}")

            # Load today's transactions
            cur.execute("""
                SELECT COUNT(*) as tx_count
                FROM TRANSACTION t
                JOIN Account a ON t.FromAccount = a.AccountNo OR t.ToAccount = a.AccountNo
                WHERE a.CustomerID=%s AND DATE(t.DateTime) = CURDATE()
            """, (self.customer_id,))
            tx_result = cur.fetchone()
            today_tx = tx_result[0] if tx_result else 0
            self.today_tx_label.setText(str(today_tx))

            # Load accounts table
            cur.execute("""
                SELECT a.AccountNo, a.Type, a.Balance, a.Status, b.Name, a.CreatedAt 
                FROM Account a 
                LEFT JOIN BRANCH b ON a.BranchID = b.BranchID 
                WHERE a.CustomerID = %s 
                ORDER BY a.AccountNo DESC
            """, (self.customer_id,))
            accounts = cur.fetchall()

            self.accounts_table.setRowCount(len(accounts))
            for i, row in enumerate(accounts):
                for j, value in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    if j == 2:  # Balance column
                        item.setForeground(QtGui.QColor("#f59e0b"))
                        try:
                            balance = float(value)
                            item.setText(f"Rs {balance:,.2f}")
                        except:
                            pass
                    elif j == 3:  # Status column
                        if value == 'Active':
                            item.setForeground(QtGui.QColor("#10b981"))
                        elif value == 'Suspended':
                            item.setForeground(QtGui.QColor("#ef4444"))
                        else:
                            item.setForeground(QtGui.QColor("#94a3b8"))
                    self.accounts_table.setItem(i, j, item)

            # Load account combos
            self.load_customer_accounts_combo()

            # Load transaction history
            self.load_transaction_history()

            cur.close()
            conn.close()

            print(f"DEBUG: Data loaded successfully for {self.customer_name}")  # Debug line

        except Exception as e:
            print(f"Error loading customer data: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load data:\n{str(e)}")
        finally:
            self.loading_overlay.hide_loading()

    def customer_deposit(self):
        if not hasattr(self, 'cust_deposit_account') or self.cust_deposit_account.count() == 0:
            QtWidgets.QMessageBox.warning(self, "Validation", "No active accounts available")
            return

        account_no = self.cust_deposit_account.currentData()
        amount_str = self.cust_deposit_amount.text().strip()
        remark = self.cust_deposit_remark.text().strip()

        if not amount_str:
            QtWidgets.QMessageBox.warning(self, "Validation", "Amount is required")
            return

        try:
            amount = decimal.Decimal(amount_str)
            if amount <= 0:
                QtWidgets.QMessageBox.warning(self, "Validation", "Amount must be positive")
                return
        except (ValueError, decimal.InvalidOperation):
            QtWidgets.QMessageBox.warning(self, "Validation", "Invalid amount")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                cur.execute("SELECT Balance, Status FROM Account WHERE AccountNo=%s", (account_no,))
                account = cur.fetchone()

                if not account:
                    raise Exception("Account not found")

                if account[1] != 'Active':
                    raise Exception("Account is not active")

                new_balance = account[0] + amount
                cur.execute("UPDATE Account SET Balance=%s WHERE AccountNo=%s", (new_balance, account_no))
                cur.execute("""
                    INSERT INTO TRANSACTION (FromAccount, ToAccount, Amount, Type, Remark) 
                    VALUES (NULL, %s, %s, 'Deposit', %s)
                """, (account_no, amount, remark))

                write_audit(cur, 'INSERT', 'TRANSACTION', self.customer_name,
                            f'Customer deposit {amount} to account {account_no}')
                conn.commit()

                QtWidgets.QMessageBox.information(self, "Success",
                                                  f"Deposit of Rs {float(amount):,.2f} completed successfully!\nNew balance: Rs {float(new_balance):,.2f}")
                self.cust_deposit_amount.clear()
                self.cust_deposit_remark.clear()
                self.load_customer_data()

            except Exception as e:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Deposit failed:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def customer_withdraw(self):
        if not hasattr(self, 'cust_withdraw_account') or self.cust_withdraw_account.count() == 0:
            QtWidgets.QMessageBox.warning(self, "Validation", "No active accounts available")
            return

        account_no = self.cust_withdraw_account.currentData()
        amount_str = self.cust_withdraw_amount.text().strip()
        remark = self.cust_withdraw_remark.text().strip()

        if not amount_str:
            QtWidgets.QMessageBox.warning(self, "Validation", "Amount is required")
            return

        try:
            amount = decimal.Decimal(amount_str)
            if amount <= 0:
                QtWidgets.QMessageBox.warning(self, "Validation", "Amount must be positive")
                return

            # Check withdrawal limit (50,000 per day)
            if amount > 50000:
                QtWidgets.QMessageBox.warning(self, "Validation", "Daily withdrawal limit is Rs 50,000")
                return
        except (ValueError, decimal.InvalidOperation):
            QtWidgets.QMessageBox.warning(self, "Validation", "Invalid amount")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                cur.execute("SELECT Balance, Status FROM Account WHERE AccountNo=%s", (account_no,))
                account = cur.fetchone()

                if not account:
                    raise Exception("Account not found")

                if account[1] != 'Active':
                    raise Exception("Account is not active")

                if account[0] < amount:
                    raise Exception("Insufficient balance")

                new_balance = account[0] - amount
                cur.execute("UPDATE Account SET Balance=%s WHERE AccountNo=%s", (new_balance, account_no))
                cur.execute("""
                    INSERT INTO TRANSACTION (FromAccount, ToAccount, Amount, Type, Remark) 
                    VALUES (%s, NULL, %s, 'Withdrawal', %s)
                """, (account_no, amount, remark))

                write_audit(cur, 'INSERT', 'TRANSACTION', self.customer_name,
                            f'Customer withdrawal {amount} from account {account_no}')
                conn.commit()

                QtWidgets.QMessageBox.information(self, "Success",
                                                  f"Withdrawal of Rs {float(amount):,.2f} completed successfully!\nNew balance: Rs {float(new_balance):,.2f}")
                self.cust_withdraw_amount.clear()
                self.cust_withdraw_remark.clear()
                self.load_customer_data()

            except Exception as e:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Withdrawal failed:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def customer_transfer(self):
        if not hasattr(self, 'cust_transfer_from') or self.cust_transfer_from.count() == 0:
            QtWidgets.QMessageBox.warning(self, "Validation", "No active accounts available")
            return

        from_account = self.cust_transfer_from.currentData()
        to_account = self.cust_transfer_to.text().strip()
        amount_str = self.cust_transfer_amount.text().strip()
        remark = self.cust_transfer_remark.text().strip()

        if not to_account or not amount_str:
            QtWidgets.QMessageBox.warning(self, "Validation", "To account and amount are required")
            return

        try:
            to_account_int = int(to_account)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Validation", "To account must be a valid number")
            return

        if from_account == to_account_int:
            QtWidgets.QMessageBox.warning(self, "Validation", "Cannot transfer to the same account")
            return

        try:
            amount = decimal.Decimal(amount_str)
            if amount <= 0:
                QtWidgets.QMessageBox.warning(self, "Validation", "Amount must be positive")
                return

            # Check transfer limit (100,000 per day)
            if amount > 100000:
                QtWidgets.QMessageBox.warning(self, "Validation", "Daily transfer limit is Rs 100,000")
                return
        except (ValueError, decimal.InvalidOperation):
            QtWidgets.QMessageBox.warning(self, "Validation", "Invalid amount")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                cur.execute("SELECT Balance, Status FROM Account WHERE AccountNo=%s", (from_account,))
                from_acc = cur.fetchone()

                if not from_acc:
                    raise Exception("From account not found")

                if from_acc[1] != 'Active':
                    raise Exception("From account is not active")

                cur.execute("SELECT Balance, Status FROM Account WHERE AccountNo=%s", (to_account_int,))
                to_acc = cur.fetchone()

                if not to_acc:
                    raise Exception("To account not found")

                if to_acc[1] != 'Active':
                    raise Exception("To account is not active")

                if from_acc[0] < amount:
                    raise Exception("Insufficient balance in from account")

                new_balance_from = from_acc[0] - amount
                new_balance_to = to_acc[0] + amount

                cur.execute("UPDATE Account SET Balance=%s WHERE AccountNo=%s", (new_balance_from, from_account))
                cur.execute("UPDATE Account SET Balance=%s WHERE AccountNo=%s", (new_balance_to, to_account_int))
                cur.execute("""
                    INSERT INTO TRANSACTION (FromAccount, ToAccount, Amount, Type, Remark) 
                    VALUES (%s, %s, %s, 'Transfer', %s)
                """, (from_account, to_account_int, amount, remark))

                write_audit(cur, 'INSERT', 'TRANSACTION', self.customer_name,
                            f'Customer transfer {amount} from {from_account} to {to_account_int}')
                conn.commit()

                QtWidgets.QMessageBox.information(self, "Success",
                                                  f"Transfer of Rs {float(amount):,.2f} completed successfully!\n"
                                                  f"From account new balance: Rs {float(new_balance_from):,.2f}")

                self.cust_transfer_to.clear()
                self.cust_transfer_amount.clear()
                self.cust_transfer_remark.clear()
                self.load_customer_data()

            except Exception as e:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Transfer failed:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def edit_customer_profile(self):
        try:
            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM Customer WHERE CustomerID=%s", (self.customer_id,))
            customer = cur.fetchone()
            cur.close()
            conn.close()

            if not customer:
                QtWidgets.QMessageBox.warning(self, "Error", "Customer not found")
                return

            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Edit Your Profile")
            dialog.setFixedSize(650, 500)
            dialog.setStyleSheet(ENHANCED_STYLE)

            layout = QtWidgets.QVBoxLayout()
            layout.setSpacing(20)

            title = QtWidgets.QLabel("✏️ Edit Your Profile")
            title.setStyleSheet("font-size: 22px; font-weight: 700; color: #a7f3d0;")
            title.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(title)

            form = QtWidgets.QFormLayout()
            form.setSpacing(15)

            name_edit = QtWidgets.QLineEdit()
            name_edit.setText(customer['Name'])

            contact_edit = QtWidgets.QLineEdit()
            contact_edit.setText(customer['Contact'] or '')

            # Password fields
            current_password_label = QtWidgets.QLabel("Current Password:")
            current_password = QtWidgets.QLineEdit()
            current_password.setEchoMode(QtWidgets.QLineEdit.Password)
            current_password.setPlaceholderText("Enter current password")

            new_password_label = QtWidgets.QLabel("New Password:")
            new_password = QtWidgets.QLineEdit()
            new_password.setEchoMode(QtWidgets.QLineEdit.Password)
            new_password.setPlaceholderText("Enter new password")

            confirm_password_label = QtWidgets.QLabel("Confirm Password:")
            confirm_password = QtWidgets.QLineEdit()
            confirm_password.setEchoMode(QtWidgets.QLineEdit.Password)
            confirm_password.setPlaceholderText("Confirm new password")

            form.addRow("👤 Name:", name_edit)
            form.addRow("📞 Contact:", contact_edit)
            form.addRow(current_password_label, current_password)
            form.addRow(new_password_label, new_password)
            form.addRow(confirm_password_label, confirm_password)

            layout.addLayout(form)

            info_label = QtWidgets.QLabel("Note: Leave password fields blank if you don't want to change password")
            info_label.setStyleSheet("color: #94a3b8; font-size: 14px;")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

            btn_layout = QtWidgets.QHBoxLayout()
            save_btn = QtWidgets.QPushButton("💾 Save Changes")
            cancel_btn = QtWidgets.QPushButton("❌ Cancel")

            save_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #10b981, stop:1 #059669);
                    border-radius: 10px;
                    padding: 12px;
                    font-size: 16px;
                    font-weight: 600;
                    color: white;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #34d399, stop:1 #10b981);
                }
            """)

            cancel_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #6b7280, stop:1 #4b5563);
                    border-radius: 10px;
                    padding: 12px;
                    font-size: 16px;
                    font-weight: 600;
                    color: white;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #9ca3af, stop:1 #6b7280);
                }
            """)

            save_btn.clicked.connect(lambda: self.save_customer_profile(
                customer['CustomerID'],
                name_edit.text(),
                contact_edit.text(),
                current_password.text(),
                new_password.text(),
                confirm_password.text(),
                dialog
            ))
            cancel_btn.clicked.connect(dialog.reject)

            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)

            dialog.setLayout(layout)
            dialog.exec_()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load profile:\n{str(e)}")

    def save_customer_profile(self, customer_id, name, contact, current_pass, new_pass, confirm_pass, dialog):
        if not name:
            QtWidgets.QMessageBox.warning(self, "Validation", "Name is required")
            return

        # Password change logic
        password_to_save = None
        if current_pass or new_pass or confirm_pass:
            # User wants to change password
            if not current_pass:
                QtWidgets.QMessageBox.warning(self, "Validation", "Current password is required")
                return

            if not new_pass:
                QtWidgets.QMessageBox.warning(self, "Validation", "New password is required")
                return

            if new_pass != confirm_pass:
                QtWidgets.QMessageBox.warning(self, "Validation", "New passwords don't match")
                return

            # Verify current password
            try:
                conn = db_connect()
                if conn is None:
                    QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                    return

                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT Password FROM Customer WHERE CustomerID=%s", (customer_id,))
                result = cur.fetchone()

                if not result:
                    QtWidgets.QMessageBox.warning(self, "Error", "Customer not found")
                    return

                if result['Password'] != current_pass:
                    QtWidgets.QMessageBox.warning(self, "Error", "Current password is incorrect")
                    return

                password_to_save = new_pass
                cur.close()
                conn.close()

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Password verification failed:\n{str(e)}")
                return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")

                if password_to_save:
                    # Update with new password
                    cur.execute("""
                        UPDATE Customer SET Name=%s, Contact=%s, Password=%s 
                        WHERE CustomerID=%s
                    """, (name, contact, password_to_save, customer_id))
                else:
                    # Update without changing password
                    cur.execute("""
                        UPDATE Customer SET Name=%s, Contact=%s 
                        WHERE CustomerID=%s
                    """, (name, contact, customer_id))

                write_audit(cur, 'UPDATE', 'Customer', self.customer_name, f'Updated profile information')
                conn.commit()

                # Update the customer name in the window
                self.customer_name = name
                self.setWindowTitle(f"FinFlow Pro - Customer Portal | Welcome, {name}")

                # Find and update the welcome label
                central = self.centralWidget()
                if central:
                    main_layout = central.layout()
                    if main_layout and main_layout.count() > 0:
                        header = main_layout.itemAt(0).widget()
                        if header:
                            header_layout = header.layout()
                            if header_layout and header_layout.count() > 0:
                                title_layout = header_layout.itemAt(0).layout()
                                if title_layout and title_layout.count() > 1:
                                    welcome_label = title_layout.itemAt(1).widget()
                                    if welcome_label:
                                        welcome_label.setText(f"Welcome, {name}")

                QtWidgets.QMessageBox.information(self, "Success",
                                                  "Profile updated successfully!\n" +
                                                  (
                                                      "Password has been changed." if password_to_save else "Password remains unchanged."))
                dialog.accept()

            except Exception as e:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to update profile:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def logout(self):
        reply = QtWidgets.QMessageBox.question(self, "Logout",
                                               "Are you sure you want to logout?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()


# ----------------------------
# Enhanced Main Window - ADMIN DASHBOARD
class EnhancedMainWindow(QtWidgets.QMainWindow):
    def __init__(self, user, user_type='admin'):
        super().__init__()
        self.current_theme = 'dark'
        self.user = user
        self.user_type = user_type

        self.setWindowTitle(f"FinFlow Pro - CBS | Welcome, {user}")
        self.resize(1600, 900)
        self.setStyleSheet(ENHANCED_STYLE)

        self.loading_overlay = LoadingOverlay(self)
        self.init_ui()

    def init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        h = QtWidgets.QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        central.setLayout(h)

        sidebar = QtWidgets.QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(350)

        sv = QtWidgets.QVBoxLayout()
        sv.setContentsMargins(0, 0, 0, 0)
        sv.setSpacing(0)

        brand_header = QtWidgets.QFrame()
        brand_header.setFixedHeight(120)
        brand_header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #042a2a, stop:1 #0ea5a4);
                border-bottom: 3px solid #7fe6d9;
            }
        """)

        brand_layout = QtWidgets.QVBoxLayout()
        brand_layout.setContentsMargins(10, 10, 10, 10)

        brand_title = QtWidgets.QLabel("🏦 FinFlow Pro")
        brand_title.setStyleSheet("font-weight: 800; font-size: 24px; color: white;")

        brand_subtitle = QtWidgets.QLabel("Core Banking System")
        brand_subtitle.setStyleSheet("font-weight: 600; font-size: 16px; color: #a7f3d0;")

        user_label = QtWidgets.QLabel(f"👤User : {self.user} ")
        user_label.setStyleSheet("font-weight: 500; font-size: 14px; color: #cdeeea; margin-top: 10px;")

        brand_layout.addWidget(brand_title)
        brand_layout.addWidget(brand_subtitle)
        brand_layout.addWidget(user_label)
        brand_header.setLayout(brand_layout)

        sv.addWidget(brand_header)

        nav_widget = QtWidgets.QWidget()
        nav_layout = QtWidgets.QVBoxLayout()
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(5)

        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard, "#0ea5a4"),
            ("👥 Customers", self.show_customers, "#3b82f6"),
            ("💳 Accounts", self.show_accounts, "#8b5cf6"),
            ("💸 Transactions", self.show_transactions, "#10b981"),
            ("⚙️ TCL Demo", self.show_tcl_demo, "#f59e0b"),
        ]

        self.nav_buttons = {}
        for text, action, color in nav_buttons:
            btn = QtWidgets.QPushButton(text)
            btn.setObjectName("sideBtn")
            btn.setFixedHeight(55)
            btn.setCursor(QtCore.Qt.PointingHandCursor)

            btn.setStyleSheet(f"""
                QPushButton#sideBtn {{
                    text-align: left;
                    padding: 15px 25px;
                    background: transparent;
                    border: none;
                    font-size: 18px;
                    color: #cdeeea;
                    font-weight: 600;
                    border-radius: 8px;
                }}
                QPushButton#sideBtn:hover {{
                    color: white;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 50),
                                                stop:1 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 150));
                    border-left: 4px solid {color};
                    padding-left: 21px;
                }}
            """)

            btn.clicked.connect(action)
            nav_layout.addWidget(btn)
            self.nav_buttons[text] = btn

        nav_layout.addStretch()

        self.btn_theme = QtWidgets.QPushButton("🌙 Switch to Light Mode")
        self.btn_theme.setObjectName("sideBtn")
        self.btn_theme.setFixedHeight(55)
        self.btn_theme.clicked.connect(self.toggle_theme)
        nav_layout.addWidget(self.btn_theme)

        btn_logout = QtWidgets.QPushButton("🚪 Logout")
        btn_logout.setObjectName("sideBtn")
        btn_logout.setFixedHeight(55)
        btn_logout.clicked.connect(self.logout)
        nav_layout.addWidget(btn_logout)

        nav_widget.setLayout(nav_layout)
        sv.addWidget(nav_widget)

        sidebar.setLayout(sv)
        h.addWidget(sidebar)

        main_content = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stack = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.stack)

        self.page_dash = self.create_dashboard_page()
        self.page_cust = self.create_customers_page()
        self.page_acc = self.create_accounts_page()
        self.page_tx = self.create_transactions_page()
        self.page_tcl = self.create_tcl_demo_page()

        self.stack.addWidget(self.page_dash)
        self.stack.addWidget(self.page_cust)
        self.stack.addWidget(self.page_acc)
        self.stack.addWidget(self.page_tx)
        self.stack.addWidget(self.page_tcl)

        footer = self.create_enhanced_footer()
        main_layout.addWidget(footer)

        main_content.setLayout(main_layout)
        h.addWidget(main_content)

        self.show_dashboard()

    def logout(self):
        reply = QtWidgets.QMessageBox.question(self, "Logout",
                                               "Are you sure you want to logout?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()

    def create_enhanced_footer(self):
        footer = QtWidgets.QFrame()
        footer.setFixedHeight(70)

        if self.current_theme == 'dark':
            footer_style = """
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 #042a2a, stop:1 #0ea5a4);
                    border-top: 3px solid #7fe6d9;
                }
            """
        else:
            footer_style = """
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 #f0fdfa, stop:1 #0ea5a4);
                    border-top: 3px solid #0d9488;
                }
            """
        footer.setStyleSheet(footer_style)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)

        status_container = QtWidgets.QHBoxLayout()
        status_indicator = QtWidgets.QLabel("●")
        if self.current_theme == 'dark':
            status_indicator.setStyleSheet("color: #10b981; font-size: 20px; font-weight: bold;")
            status_text = QtWidgets.QLabel("System Online")
            status_text.setStyleSheet("color: #cbd5e1; font-size: 14px; font-weight: 600;")
        else:
            status_indicator.setStyleSheet("color: #059669; font-size: 20px; font-weight: bold;")
            status_text = QtWidgets.QLabel("System Online")
            status_text.setStyleSheet("color: #475569; font-size: 14px; font-weight: 600;")
        status_container.addWidget(status_indicator)
        status_container.addWidget(status_text)

        copyright = QtWidgets.QLabel("© 2025 FinFlow Pro CBS | Enterprise Banking Solution")
        if self.current_theme == 'dark':
            copyright.setStyleSheet("color: #7fe6d9; font-size: 14px; font-weight: 500;")
        else:
            copyright.setStyleSheet("color: #0f766e; font-size: 14px; font-weight: 500;")

        db_info = QtWidgets.QLabel("Developed By Malik kamran Ali")
        if self.current_theme == 'dark':
            db_info.setStyleSheet("color: #a7f3d0; font-size: 14px; font-weight: 600;")
        else:
            db_info.setStyleSheet("color: #0d9488; font-size: 14px; font-weight: 600;")

        layout.addLayout(status_container)
        layout.addWidget(copyright)
        layout.addStretch()
        layout.addWidget(db_info)

        footer.setLayout(layout)
        return footer

    def create_stat_card(self, title, value_label, color, description, icon):
        card = QtWidgets.QFrame()
        card.setFixedHeight(150)
        if self.current_theme == 'dark':
            card.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 30),
                                                stop:1 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 10));
                    border: 2px solid {color};
                    border-radius: 15px;
                }}
            """)
        else:
            card.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 15),
                                                stop:1 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 5));
                    border: 2px solid {color};
                    border-radius: 15px;
                }}
            """)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)

        icon_label = QtWidgets.QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 48px;
            color: {color};
        """)
        layout.addWidget(icon_label)

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(5)

        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {color};
        """)

        value_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 800;
            color: {color};
        """)
        value_label.setAlignment(QtCore.Qt.AlignLeft)

        desc_label = QtWidgets.QLabel(description)
        if self.current_theme == 'dark':
            desc_label.setStyleSheet("""
                font-size: 14px;
                color: #94a3b8;
            """)
        else:
            desc_label.setStyleSheet("""
                font-size: 14px;
                color: #64748b;
            """)
        desc_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        text_layout.addWidget(desc_label)

        layout.addLayout(text_layout)
        card.setLayout(layout)

        return card

    def create_dashboard_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        header = QtWidgets.QHBoxLayout()

        if self.current_theme == 'dark':
            welcome_text = QtWidgets.QLabel(f"Welcome back, {self.user}! 👋")
            welcome_text.setStyleSheet("font-size: 28px; font-weight: 700; color: #a7f3d0;")

            date_label = QtWidgets.QLabel(datetime.now().strftime("%A, %B %d, %Y"))
            date_label.setStyleSheet("font-size: 16px; color: #94a3b8; font-weight: 500;")
        else:
            welcome_text = QtWidgets.QLabel(f"Welcome back, {self.user}! 👋")
            welcome_text.setStyleSheet("font-size: 28px; font-weight: 700; color: #0f766e;")

            date_label = QtWidgets.QLabel(datetime.now().strftime("%A, %B %d, %Y"))
            date_label.setStyleSheet("font-size: 16px; color: #64748b; font-weight: 500;")

        header.addWidget(welcome_text)
        header.addStretch()
        header.addWidget(date_label)
        layout.addLayout(header)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(20)
        grid.setContentsMargins(0, 10, 0, 10)

        self.lbl_customers_count = QtWidgets.QLabel("0")
        self.lbl_accounts_count = QtWidgets.QLabel("0")
        self.lbl_total_balance = QtWidgets.QLabel("Rs 0.00")
        self.lbl_today_tx = QtWidgets.QLabel("0")
        self.lbl_active_accounts = QtWidgets.QLabel("0")
        self.lbl_total_transactions = QtWidgets.QLabel("0")

        cards = [
            (self.create_stat_card("Total Customers", self.lbl_customers_count, "#0ea5a4", "Registered customers", "👥"),
             0, 0),
            (self.create_stat_card("Total Accounts", self.lbl_accounts_count, "#3b82f6", "Bank accounts", "💳"), 0, 1),
            (self.create_stat_card("Total Balance", self.lbl_total_balance, "#10b981", "Deposited amount", "💰"), 0, 2),
            (self.create_stat_card("Today's Transactions", self.lbl_today_tx, "#f59e0b", "Transactions today", "💸"), 1,
             0),
            (self.create_stat_card("Active Accounts", self.lbl_active_accounts, "#8b5cf6", "Active bank accounts", "✅"),
             1, 1),
            (self.create_stat_card("All Transactions", self.lbl_total_transactions, "#ef4444", "Total transactions",
                                   "📊"), 1, 2),
        ]

        for card, row, col in cards:
            grid.addWidget(card, row, col)

        layout.addLayout(grid)

        if self.current_theme == 'dark':
            quick_box = QtWidgets.QGroupBox("Quick Actions")
            quick_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #7c3aed;
                    border-radius: 12px;
                    background: rgba(15, 23, 32, 0.8);
                }
                QGroupBox::title {
                    color: #8b5cf6;
                    font-weight: bold;
                }
            """)
        else:
            quick_box = QtWidgets.QGroupBox("Quick Actions")
            quick_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #7c3aed;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.9);
                }
                QGroupBox::title {
                    color: #7c3aed;
                    font-weight: bold;
                }
            """)

        quick_layout = QtWidgets.QHBoxLayout()
        quick_layout.setSpacing(15)

        quick_actions = [
            ("➕ New Customer", "Add new customer", lambda: self.show_customers()),
            ("🏦 Open Account", "Create new account", lambda: self.show_accounts()),
            ("💰 Quick Deposit", "Make deposit", lambda: self.show_transactions()),
            ("🔄 Refresh Data", "Refresh dashboard", lambda: self.refresh_dashboard()),
        ]

        for text, tooltip, action in quick_actions:
            btn = QtWidgets.QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setFixedHeight(60)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            if self.current_theme == 'dark':
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                    stop:0 #4f46e5, stop:1 #7c3aed);
                        border-radius: 10px;
                        font-size: 16px;
                        color: white;
                        font-weight: 600;
                        padding: 10px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                    stop:0 #6366f1, stop:1 #8b5cf6);
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                    stop:0 #4f46e5, stop:1 #7c3aed);
                        border-radius: 10px;
                        font-size: 16px;
                        color: white;
                        font-weight: 600;
                        padding: 10px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                    stop:0 #6366f1, stop:1 #8b5cf6);
                    }
                """)
            btn.clicked.connect(action)
            quick_layout.addWidget(btn)

        quick_box.setLayout(quick_layout)
        layout.addWidget(quick_box)

        if self.current_theme == 'dark':
            activity_box = QtWidgets.QGroupBox("Recent Activity")
            activity_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #0ea5a4;
                    border-radius: 12px;
                    background: rgba(15, 23, 32, 0.8);
                }
                QGroupBox::title {
                    color: #0ea5a4;
                    font-weight: bold;
                }
            """)
        else:
            activity_box = QtWidgets.QGroupBox("Recent Activity")
            activity_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #0ea5a4;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.9);
                }
                QGroupBox::title {
                    color: #0ea5a4;
                    font-weight: bold;
                }
            """)

        activity_layout = QtWidgets.QVBoxLayout()
        self.recent_activity_table = QtWidgets.QTableWidget()
        self.recent_activity_table.setColumnCount(4)
        self.recent_activity_table.setHorizontalHeaderLabels(["Time", "Action", "User", "Details"])
        self.recent_activity_table.horizontalHeader().setStretchLastSection(True)
        self.recent_activity_table.setMaximumHeight(200)
        activity_layout.addWidget(self.recent_activity_table)
        activity_box.setLayout(activity_layout)
        layout.addWidget(activity_box)

        layout.addStretch()
        w.setLayout(layout)
        return w

    def refresh_dashboard(self):
        self.loading_overlay.show_loading("Refreshing dashboard...")
        try:
            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM Customer")
            self.lbl_customers_count.setText(str(cur.fetchone()[0]))

            cur.execute("SELECT COUNT(*) FROM Account")
            self.lbl_accounts_count.setText(str(cur.fetchone()[0]))

            cur.execute("SELECT IFNULL(SUM(Balance),0) FROM Account WHERE Status='Active'")
            total_bal = cur.fetchone()[0]
            self.lbl_total_balance.setText(f"Rs {float(total_bal):,.2f}")

            cur.execute("SELECT COUNT(*) FROM TRANSACTION WHERE DATE(DateTime) = CURDATE()")
            self.lbl_today_tx.setText(str(cur.fetchone()[0]))

            cur.execute("SELECT COUNT(*) FROM Account WHERE Status='Active'")
            self.lbl_active_accounts.setText(str(cur.fetchone()[0]))

            cur.execute("SELECT COUNT(*) FROM TRANSACTION")
            self.lbl_total_transactions.setText(str(cur.fetchone()[0]))

            cur.execute("""
                SELECT DateTime, Operation, UserName, Details 
                FROM AuditLog 
                ORDER BY DateTime DESC 
                LIMIT 10
            """)
            rows = cur.fetchall()
            self.recent_activity_table.setRowCount(len(rows))

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    if self.current_theme == 'dark':
                        if j == 1:
                            if value == 'INSERT':
                                item.setForeground(QtGui.QColor("#10b981"))
                            elif value == 'UPDATE':
                                item.setForeground(QtGui.QColor("#f59e0b"))
                            elif value == 'DELETE':
                                item.setForeground(QtGui.QColor("#ef4444"))
                    else:
                        if j == 1:
                            if value == 'INSERT':
                                item.setForeground(QtGui.QColor("#059669"))
                            elif value == 'UPDATE':
                                item.setForeground(QtGui.QColor("#d97706"))
                            elif value == 'DELETE':
                                item.setForeground(QtGui.QColor("#dc2626"))
                    self.recent_activity_table.setItem(i, j, item)

            cur.close()
            conn.close()

        except Exception as e:
            print("Dashboard refresh error:", e)
        finally:
            self.loading_overlay.hide_loading()

    def create_customers_page(self):
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout()
        v.setContentsMargins(25, 25, 25, 25)
        v.setSpacing(20)

        header = QtWidgets.QHBoxLayout()
        if self.current_theme == 'dark':
            title = QtWidgets.QLabel("👥 Customer Management")
            title.setStyleSheet("font-size:26px;font-weight:700;color:#a7f3d0;")
        else:
            title = QtWidgets.QLabel("👥 Customer Management")
            title.setStyleSheet("font-size:26px;font-weight:700;color:#0f766e;")

        search_box = QtWidgets.QLineEdit()
        search_box.setPlaceholderText("🔍 Search customers...")
        search_box.setFixedWidth(300)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(search_box)
        v.addLayout(header)

        if self.current_theme == 'dark':
            form_box = QtWidgets.QGroupBox("➕ Add New Customer")
            form_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #3b82f6;
                    border-radius: 12px;
                    background: rgba(15, 23, 32, 0.8);
                }
                QGroupBox::title {
                    color: #3b82f6;
                    font-weight: bold;
                }
            """)
        else:
            form_box = QtWidgets.QGroupBox("➕ Add New Customer")
            form_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #3b82f6;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.9);
                }
                QGroupBox::title {
                    color: #3b82f6;
                    font-weight: bold;
                }
            """)

        form_layout = QtWidgets.QFormLayout()
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        self.input_name = QtWidgets.QLineEdit()
        self.input_name.setPlaceholderText("Full name")

        self.input_cnic = QtWidgets.QLineEdit()
        self.input_cnic.setPlaceholderText("CNIC (13 digits)")

        self.input_contact = QtWidgets.QLineEdit()
        self.input_contact.setPlaceholderText("Contact number")

        self.combo_cust_type = QtWidgets.QComboBox()
        self.combo_cust_type.addItems(['Individual', 'Business'])

        self.input_dob = QtWidgets.QDateEdit()
        self.input_dob.setCalendarPopup(True)
        self.input_dob.setDate(QtCore.QDate.currentDate().addYears(-25))

        self.input_password = QtWidgets.QLineEdit()
        self.input_password.setPlaceholderText("Set customer password")
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)

        addbtn = QtWidgets.QPushButton("➕ Add Customer")
        addbtn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3b82f6, stop:1 #1d4ed8);
                border-radius: 10px;
                padding: 12px;
                font-size: 18px;
                font-weight: 600;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4f46e5, stop:1 #3730a3);
            }
        """)
        addbtn.clicked.connect(self.add_customer)

        form_layout.addRow("👤 Name:", self.input_name)
        form_layout.addRow("🆔 CNIC:", self.input_cnic)
        form_layout.addRow("📞 Contact:", self.input_contact)
        form_layout.addRow("🔒 Password:", self.input_password)
        form_layout.addRow("🏢 Type:", self.combo_cust_type)
        form_layout.addRow("🎂 Date of Birth:", self.input_dob)
        form_layout.addRow("", addbtn)

        form_box.setLayout(form_layout)
        v.addWidget(form_box)

        if self.current_theme == 'dark':
            table_box = QtWidgets.QGroupBox("📋 All Customers")
            table_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #0ea5a4;
                    border-radius: 12px;
                    background: rgba(15, 23, 32, 0.8);
                }
                QGroupBox::title {
                    color: #0ea5a4;
                    font-weight: bold;
                }
            """)
        else:
            table_box = QtWidgets.QGroupBox("📋 All Customers")
            table_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #0ea5a4;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.9);
                }
                QGroupBox::title {
                    color: #0ea5a4;
                    font-weight: bold;
                }
            """)

        table_layout = QtWidgets.QVBoxLayout()
        self.cust_table = QtWidgets.QTableWidget()
        self.cust_table.setColumnCount(7)
        self.cust_table.setHorizontalHeaderLabels(["ID", "Name", "CNIC", "Contact", "Type", "Created", "Actions"])
        self.cust_table.horizontalHeader().setStretchLastSection(True)
        self.cust_table.verticalHeader().setDefaultSectionSize(70)
        self.cust_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.cust_table)
        table_box.setLayout(table_layout)
        v.addWidget(table_box)

        w.setLayout(v)
        return w

    def load_customers(self):
        self.loading_overlay.show_loading("Loading customers...")
        try:
            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor()
            cur.execute("SELECT CustomerID,Name,CNIC,Contact,Type,CreatedAt FROM Customer ORDER BY CustomerID ASC")
            rows = cur.fetchall()
            self.cust_table.setRowCount(len(rows))

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    if self.current_theme == 'dark':
                        if j == 1:
                            item.setForeground(QtGui.QColor("#7fe6d9"))
                            item.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Bold))
                        elif j == 4:
                            if value == 'Business':
                                item.setForeground(QtGui.QColor("#f59e0b"))
                            else:
                                item.setForeground(QtGui.QColor("#10b981"))
                    else:
                        if j == 1:
                            item.setForeground(QtGui.QColor("#0d9488"))
                            item.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Bold))
                        elif j == 4:
                            if value == 'Business':
                                item.setForeground(QtGui.QColor("#d97706"))
                            else:
                                item.setForeground(QtGui.QColor("#059669"))
                    self.cust_table.setItem(i, j, item)
                self.cust_table.setRowHeight(i, 70)

                actions_widget = QtWidgets.QWidget()
                actions_layout = QtWidgets.QHBoxLayout()
                actions_layout.setContentsMargins(5, 5, 5, 5)
                actions_layout.setSpacing(10)

                view_btn = QtWidgets.QPushButton("👁️ View")
                view_btn.setFixedSize(90, 40)
                view_btn.setStyleSheet("""
                    QPushButton {
                        background: #3b82f6;
                        color: white;
                        border-radius: 6px;
                        font-weight: 600;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background: #2563eb;
                    }
                """)
                view_btn.clicked.connect(lambda checked, idx=row[0]: self.view_customer_details(idx))

                edit_btn = QtWidgets.QPushButton("✏️ Edit")
                edit_btn.setObjectName("editBtn")
                edit_btn.setFixedSize(90, 40)
                edit_btn.clicked.connect(lambda checked, idx=row[0]: self.edit_customer(idx))

                delete_btn = QtWidgets.QPushButton("🗑️ Delete")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedSize(90, 40)
                delete_btn.clicked.connect(lambda checked, idx=row[0]: self.delete_customer(idx))

                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_widget.setLayout(actions_layout)
                self.cust_table.setCellWidget(i, 6, actions_widget)

            cur.close()
            conn.close()

        except Exception as e:
            print("Load customers error:", e)
        finally:
            self.loading_overlay.hide_loading()
            self.refresh_dashboard()

    def add_customer(self):
        name = self.input_name.text().strip()
        cnic = self.input_cnic.text().strip()
        contact = self.input_contact.text().strip()
        password = self.input_password.text().strip()
        cust_type = self.combo_cust_type.currentText()
        dob = self.input_dob.date().toString("yyyy-MM-dd")

        if not name or not cnic:
            QtWidgets.QMessageBox.warning(self, "Validation", "Name and CNIC are required")
            return

        if not password:
            QtWidgets.QMessageBox.warning(self, "Validation", "Password is required")
            return

        if len(cnic) != 13:
            QtWidgets.QMessageBox.warning(self, "Validation", "CNIC must be 13 digits")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")

                if cust_type == 'Individual':
                    cur.execute(
                        "INSERT INTO Customer (Name, CNIC, Contact, Password, Type, DOB) VALUES (%s,%s,%s,%s,%s,%s)",
                        (name, cnic, contact, password, cust_type, dob))
                else:
                    cur.execute("INSERT INTO Customer (Name, CNIC, Contact, Password, Type) VALUES (%s,%s,%s,%s,%s)",
                                (name, cnic, contact, password, cust_type))

                write_audit(cur, 'INSERT', 'Customer', self.user, f'Added {cust_type} customer: {name} with password')
                conn.commit()

                QtWidgets.QMessageBox.information(self, "Success",
                                                  f"Customer added successfully!\n"
                                                  f"Customer login credentials:\n"
                                                  f"Username: {name}\n"
                                                  f"Password: {password}")

                self.input_name.clear()
                self.input_cnic.clear()
                self.input_contact.clear()
                self.input_password.clear()
                self.load_customers()

            except mysql.connector.IntegrityError:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", "CNIC already exists!")
            except Exception as e:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to add customer:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def edit_customer(self, customer_id):
        try:
            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM Customer WHERE CustomerID=%s", (customer_id,))
            customer = cur.fetchone()
            cur.close()
            conn.close()

            if not customer:
                QtWidgets.QMessageBox.warning(self, "Error", "Customer not found")
                return

            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Edit Customer")
            dialog.setFixedSize(650, 550)
            if self.current_theme == 'dark':
                dialog.setStyleSheet(ENHANCED_STYLE)
            else:
                dialog.setStyleSheet(LIGHT_STYLE)

            layout = QtWidgets.QVBoxLayout()
            form = QtWidgets.QFormLayout()
            name_edit = QtWidgets.QLineEdit()
            name_edit.setText(customer['Name'])
            cnic_edit = QtWidgets.QLineEdit()
            cnic_edit.setText(customer['CNIC'])
            contact_edit = QtWidgets.QLineEdit()
            contact_edit.setText(customer['Contact'] or '')

            password_edit = QtWidgets.QLineEdit()
            password_edit.setText(customer['Password'])
            password_edit.setEchoMode(QtWidgets.QLineEdit.Password)

            type_combo = QtWidgets.QComboBox()
            type_combo.addItems(['Individual', 'Business'])
            type_combo.setCurrentText(customer['Type'])

            dob_edit = QtWidgets.QDateEdit()
            dob_edit.setCalendarPopup(True)
            if customer['DOB']:
                dob_edit.setDate(QtCore.QDate.fromString(customer['DOB'], "yyyy-MM-dd"))
            else:
                dob_edit.setDate(QtCore.QDate.currentDate().addYears(-25))

            form.addRow("Name:", name_edit)
            form.addRow("CNIC:", cnic_edit)
            form.addRow("Contact:", contact_edit)
            form.addRow("Password:", password_edit)
            form.addRow("Type:", type_combo)
            form.addRow("Date of Birth:", dob_edit)
            layout.addLayout(form)

            btn_layout = QtWidgets.QHBoxLayout()
            save_btn = QtWidgets.QPushButton("💾 Save")
            cancel_btn = QtWidgets.QPushButton("❌ Cancel")

            save_btn.clicked.connect(lambda: self.save_customer_edit(customer_id, name_edit.text(),
                                                                     cnic_edit.text(), contact_edit.text(),
                                                                     password_edit.text(), type_combo.currentText(),
                                                                     dob_edit.date().toString("yyyy-MM-dd"),
                                                                     dialog))
            cancel_btn.clicked.connect(dialog.reject)

            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)
            dialog.setLayout(layout)
            dialog.exec_()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to edit customer:\n{str(e)}")

    def save_customer_edit(self, customer_id, name, cnic, contact, password, cust_type, dob, dialog):
        if not name or not cnic:
            QtWidgets.QMessageBox.warning(self, "Validation", "Name and CNIC are required")
            return

        if not password:
            QtWidgets.QMessageBox.warning(self, "Validation", "Password is required")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                if cust_type == 'Individual':
                    cur.execute(
                        "UPDATE Customer SET Name=%s, CNIC=%s, Contact=%s, Password=%s, Type=%s, DOB=%s WHERE CustomerID=%s",
                        (name, cnic, contact, password, cust_type, dob, customer_id))
                else:
                    cur.execute(
                        "UPDATE Customer SET Name=%s, CNIC=%s, Contact=%s, Password=%s, Type=%s, DOB=NULL WHERE CustomerID=%s",
                        (name, cnic, contact, password, cust_type, customer_id))

                write_audit(cur, 'UPDATE', 'Customer', self.user, f'Updated customer: {name}')
                conn.commit()

                QtWidgets.QMessageBox.information(self, "Success", "Customer updated successfully!")
                dialog.accept()
                self.load_customers()

            except Exception as e:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to update customer:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def delete_customer(self, customer_id):
        reply = QtWidgets.QMessageBox.question(self, "Confirm Delete",
                                               "Are you sure you want to delete this customer?\nThis will also delete all associated accounts!",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                conn = db_connect()
                if conn is None:
                    QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                    return

                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT Name FROM Customer WHERE CustomerID=%s", (customer_id,))
                customer = cur.fetchone()

                if not customer:
                    QtWidgets.QMessageBox.warning(self, "Error", "Customer not found")
                    return

                cur.execute("START TRANSACTION")
                cur.execute("DELETE FROM Account WHERE CustomerID=%s", (customer_id,))
                cur.execute("DELETE FROM Customer WHERE CustomerID=%s", (customer_id,))
                write_audit(cur, 'DELETE', 'Customer', self.user, f'Deleted customer: {customer["Name"]}')
                conn.commit()

                QtWidgets.QMessageBox.information(self, "Success", "Customer deleted successfully!")
                self.load_customers()

            except Exception as e:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete customer:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

    def view_customer_details(self, customer_id):
        try:
            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT c.*, COUNT(a.AccountNo) as AccountCount, 
                       SUM(a.Balance) as TotalBalance 
                FROM Customer c 
                LEFT JOIN Account a ON c.CustomerID = a.CustomerID 
                WHERE c.CustomerID = %s 
                GROUP BY c.CustomerID
            """, (customer_id,))
            customer = cur.fetchone()
            cur.close()
            conn.close()

            if not customer:
                QtWidgets.QMessageBox.warning(self, "Error", "Customer not found")
                return

            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Customer Details")
            dialog.setFixedSize(800, 650)
            if self.current_theme == 'dark':
                dialog.setStyleSheet(ENHANCED_STYLE)
            else:
                dialog.setStyleSheet(LIGHT_STYLE)

            layout = QtWidgets.QVBoxLayout()

            info_box = QtWidgets.QGroupBox("Customer Information")
            info_layout = QtWidgets.QFormLayout()

            info_layout.addRow("ID:", QtWidgets.QLabel(str(customer['CustomerID'])))
            info_layout.addRow("Name:", QtWidgets.QLabel(customer['Name']))
            info_layout.addRow("CNIC:", QtWidgets.QLabel(customer['CNIC']))
            info_layout.addRow("Contact:", QtWidgets.QLabel(customer['Contact'] or 'N/A'))
            info_layout.addRow("Type:", QtWidgets.QLabel(customer['Type']))
            info_layout.addRow("Date of Birth:", QtWidgets.QLabel(str(customer['DOB'] or 'N/A')))
            info_layout.addRow("Registered:", QtWidgets.QLabel(str(customer['CreatedAt'])))

            stats_box = QtWidgets.QGroupBox("Account Statistics")
            stats_layout = QtWidgets.QFormLayout()
            stats_layout.addRow("Total Accounts:", QtWidgets.QLabel(str(customer['AccountCount'] or 0)))
            stats_layout.addRow("Total Balance:", QtWidgets.QLabel(f"Rs {float(customer['TotalBalance'] or 0):,.2f}"))

            info_box.setLayout(info_layout)
            stats_box.setLayout(stats_layout)

            layout.addWidget(info_box)
            layout.addWidget(stats_box)

            close_btn = QtWidgets.QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)

            dialog.setLayout(layout)
            dialog.exec_()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to view customer details:\n{str(e)}")

    # ... [The rest of the EnhancedMainWindow class remains the same as in your original code]
    # Including: create_accounts_page(), create_transactions_page(), create_tcl_demo_page()
    # and all their helper methods (deposit(), withdraw(), transfer(), etc.)

    # Note: Only the customer-related methods have been modified. The rest of the
    # admin functionality remains exactly as in your original code.

    def create_accounts_page(self):
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout()
        v.setContentsMargins(25, 25, 25, 25)
        v.setSpacing(20)

        if self.current_theme == 'dark':
            title = QtWidgets.QLabel("💳 Account Management")
            title.setStyleSheet("font-size:26px;font-weight:700;color:#a7f3d0;")
        else:
            title = QtWidgets.QLabel("💳 Account Management")
            title.setStyleSheet("font-size:26px;font-weight:700;color:#0f766e;")
        v.addWidget(title)

        if self.current_theme == 'dark':
            form_box = QtWidgets.QGroupBox("🏦 Create New Account")
            form_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #8b5cf6;
                    border-radius: 12px;
                    background: rgba(15, 23, 32, 0.8);
                }
                QGroupBox::title {
                    color: #8b5cf6;
                    font-weight: bold;
                }
            """)
        else:
            form_box = QtWidgets.QGroupBox("🏦 Create New Account")
            form_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #8b5cf6;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.9);
                }
                QGroupBox::title {
                    color: #8b5cf6;
                    font-weight: bold;
                }
            """)

        form = QtWidgets.QGridLayout()
        form.setSpacing(15)

        self.combo_cust_for_acc = QtWidgets.QComboBox()
        self.load_customers_into_combo()

        self.combo_acc_type = QtWidgets.QComboBox()
        self.combo_acc_type.addItems(['Savings', 'Current', 'Basic Banking'])

        self.combo_branch = QtWidgets.QComboBox()
        self.load_branches_into_combo()

        self.input_initial = QtWidgets.QLineEdit()
        self.input_initial.setPlaceholderText("Initial Balance")
        self.input_initial.setText("0")

        btn_create_acc = QtWidgets.QPushButton("🏦 Create Account")
        btn_create_acc.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #8b5cf6, stop:1 #7c3aed);
                border-radius: 10px;
                padding: 12px;
                font-size: 18px;
                font-weight: 600;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #a78bfa, stop:1 #8b5cf6);
            }
        """)
        btn_create_acc.clicked.connect(self.create_account)

        form.addWidget(QtWidgets.QLabel("👤 Customer:"), 0, 0)
        form.addWidget(self.combo_cust_for_acc, 0, 1)
        form.addWidget(QtWidgets.QLabel("🏦 Type:"), 1, 0)
        form.addWidget(self.combo_acc_type, 1, 1)
        form.addWidget(QtWidgets.QLabel("📍 Branch:"), 2, 0)
        form.addWidget(self.combo_branch, 2, 1)
        form.addWidget(QtWidgets.QLabel("💰 Initial Balance:"), 3, 0)
        form.addWidget(self.input_initial, 3, 1)
        form.addWidget(btn_create_acc, 4, 0, 1, 2)

        form_box.setLayout(form)
        v.addWidget(form_box)

        if self.current_theme == 'dark':
            table_box = QtWidgets.QGroupBox("📋 All Accounts")
            table_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #0ea5a4;
                    border-radius: 12px;
                    background: rgba(15, 23, 32, 0.8);
                }
                QGroupBox::title {
                    color: #0ea5a4;
                    font-weight: bold;
                }
            """)
        else:
            table_box = QtWidgets.QGroupBox("📋 All Accounts")
            table_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #0ea5a4;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.9);
                }
                QGroupBox::title {
                    color: #0ea5a4;
                    font-weight: bold;
                }
            """)

        table_layout = QtWidgets.QVBoxLayout()
        self.acc_table = QtWidgets.QTableWidget()
        self.acc_table.setColumnCount(8)
        self.acc_table.setHorizontalHeaderLabels(
            ["AccountNo", "Customer", "Type", "Balance", "Status", "Branch", "Created", "Actions"])
        self.acc_table.horizontalHeader().setStretchLastSection(True)
        self.acc_table.verticalHeader().setDefaultSectionSize(70)
        self.acc_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.acc_table)
        table_box.setLayout(table_layout)
        v.addWidget(table_box)

        w.setLayout(v)
        return w

    def load_accounts(self):
        self.loading_overlay.show_loading("Loading accounts...")
        try:
            self.load_customers_into_combo()
            self.load_branches_into_combo()

            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor()
            cur.execute("""
                SELECT a.AccountNo, c.Name, a.Type, a.Balance, a.Status, b.Name, a.CreatedAt 
                FROM Account a 
                LEFT JOIN Customer c ON a.CustomerID = c.CustomerID 
                LEFT JOIN BRANCH b ON a.BranchID = b.BranchID 
                ORDER BY a.AccountNo DESC
            """)
            rows = cur.fetchall()
            self.acc_table.setRowCount(len(rows))

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    if self.current_theme == 'dark':
                        if j == 2:
                            if value == 'Savings':
                                item.setForeground(QtGui.QColor("#10b981"))
                            elif value == 'Current':
                                item.setForeground(QtGui.QColor("#3b82f6"))
                            else:
                                item.setForeground(QtGui.QColor("#8b5cf6"))
                        elif j == 3:
                            item.setForeground(QtGui.QColor("#f59e0b"))
                            try:
                                balance = float(value)
                                item.setText(f"Rs {balance:,.2f}")
                            except:
                                pass
                        elif j == 4:
                            if value == 'Active':
                                item.setForeground(QtGui.QColor("#10b981"))
                            elif value == 'Suspended':
                                item.setForeground(QtGui.QColor("#ef4444"))
                            else:
                                item.setForeground(QtGui.QColor("#94a3b8"))
                    else:
                        if j == 2:
                            if value == 'Savings':
                                item.setForeground(QtGui.QColor("#059669"))
                            elif value == 'Current':
                                item.setForeground(QtGui.QColor("#2563eb"))
                            else:
                                item.setForeground(QtGui.QColor("#7c3aed"))
                        elif j == 3:
                            item.setForeground(QtGui.QColor("#d97706"))
                            try:
                                balance = float(value)
                                item.setText(f"Rs {balance:,.2f}")
                            except:
                                pass
                        elif j == 4:
                            if value == 'Active':
                                item.setForeground(QtGui.QColor("#059669"))
                            elif value == 'Suspended':
                                item.setForeground(QtGui.QColor("#dc2626"))
                            else:
                                item.setForeground(QtGui.QColor("#64748b"))
                    self.acc_table.setItem(i, j, item)
                self.acc_table.setRowHeight(i, 70)

                actions_widget = QtWidgets.QWidget()
                actions_layout = QtWidgets.QHBoxLayout()
                actions_layout.setContentsMargins(5, 5, 5, 5)
                actions_layout.setSpacing(10)

                view_tx_btn = QtWidgets.QPushButton("📊 View")
                view_tx_btn.setFixedSize(90, 40)
                view_tx_btn.setToolTip("View transactions")
                view_tx_btn.setStyleSheet("""
                    QPushButton {
                        background: #3b82f6;
                        color: white;
                        border-radius: 6px;
                        font-weight: 600;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background: #2563eb;
                    }
                """)
                view_tx_btn.clicked.connect(lambda checked, acc_no=row[0]: self.view_account_transactions(acc_no))

                edit_btn = QtWidgets.QPushButton("✏️ Edit")
                edit_btn.setObjectName("editBtn")
                edit_btn.setFixedSize(90, 40)
                edit_btn.setToolTip("Edit account")
                edit_btn.clicked.connect(lambda checked, acc_no=row[0]: self.edit_account(acc_no))

                delete_btn = QtWidgets.QPushButton("🗑️ Delete")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedSize(90, 40)
                delete_btn.setToolTip("Delete account")
                delete_btn.clicked.connect(lambda checked, acc_no=row[0]: self.delete_account(acc_no))

                actions_layout.addWidget(view_tx_btn)
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_widget.setLayout(actions_layout)
                self.acc_table.setCellWidget(i, 7, actions_widget)

            cur.close()
            conn.close()

        except Exception as e:
            print("Load accounts error:", e)
        finally:
            self.loading_overlay.hide_loading()
            self.refresh_dashboard()

    def load_customers_into_combo(self):
        self.combo_cust_for_acc.clear()
        try:
            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor()
            cur.execute("SELECT CustomerID,Name FROM Customer ORDER BY Name")
            rows = cur.fetchall()
            for r in rows:
                self.combo_cust_for_acc.addItem(f"{r[1]} (ID:{r[0]})", r[0])
            cur.close()
            conn.close()
        except Exception as e:
            print("Load customers combo error:", e)

    def load_branches_into_combo(self):
        self.combo_branch.clear()
        try:
            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor()
            cur.execute("SELECT BranchID,Name FROM BRANCH ORDER BY Name")
            rows = cur.fetchall()
            for r in rows:
                self.combo_branch.addItem(r[1], r[0])
            cur.close()
            conn.close()
        except Exception as e:
            print("Load branches combo error:", e)

    def create_account(self):
        if self.combo_cust_for_acc.count() == 0:
            QtWidgets.QMessageBox.warning(self, "Validation", "No customers available")
            return

        cust_id = self.combo_cust_for_acc.currentData()
        acc_type = self.combo_acc_type.currentText()
        branch_id = self.combo_branch.currentData()

        try:
            initial = float(self.input_initial.text() or 0)
            if initial < 0:
                raise ValueError("Balance cannot be negative")
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Validation", "Invalid initial balance")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                cur.execute("INSERT INTO Account (CustomerID,Type,Balance,BranchID) VALUES (%s,%s,%s,%s)",
                            (cust_id, acc_type, initial, branch_id))
                write_audit(cur, 'INSERT', 'Account', self.user, f'Create {acc_type} account for Cust {cust_id}')
                conn.commit()

                QtWidgets.QMessageBox.information(self, "Success", "Account created successfully!")
                self.input_initial.clear()
                self.load_accounts()
                self.load_customers_into_combo()

            except Exception as e:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to create account:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def edit_account(self, account_no):
        try:
            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT a.*, c.Name as CustomerName, b.Name as BranchName 
                FROM Account a 
                LEFT JOIN Customer c ON a.CustomerID = c.CustomerID 
                LEFT JOIN BRANCH b ON a.BranchID = b.BranchID 
                WHERE a.AccountNo=%s
            """, (account_no,))
            account = cur.fetchone()
            cur.close()
            conn.close()

            if not account:
                QtWidgets.QMessageBox.warning(self, "Error", "Account not found")
                return

            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Edit Account")
            dialog.setFixedSize(650, 550)
            if self.current_theme == 'dark':
                dialog.setStyleSheet(ENHANCED_STYLE)
            else:
                dialog.setStyleSheet(LIGHT_STYLE)

            layout = QtWidgets.QVBoxLayout()
            form = QtWidgets.QFormLayout()

            if self.current_theme == 'dark':
                acc_info = QtWidgets.QLabel(f"Account: {account_no} | Customer: {account['CustomerName']}")
                acc_info.setStyleSheet("color: #7fe6d9; font-weight: bold;")
            else:
                acc_info = QtWidgets.QLabel(f"Account: {account_no} | Customer: {account['CustomerName']}")
                acc_info.setStyleSheet("color: #0d9488; font-weight: bold;")
            form.addRow(acc_info)

            balance_edit = QtWidgets.QLineEdit()
            balance_edit.setText(str(account['Balance']))

            status_combo = QtWidgets.QComboBox()
            status_combo.addItems(['Active', 'Closed', 'Suspended'])
            status_combo.setCurrentText(account['Status'])

            form.addRow("Balance:", balance_edit)
            form.addRow("Status:", status_combo)
            layout.addLayout(form)

            btn_layout = QtWidgets.QHBoxLayout()
            save_btn = QtWidgets.QPushButton("💾 Save")
            cancel_btn = QtWidgets.QPushButton("❌ Cancel")

            save_btn.clicked.connect(
                lambda: self.save_account_edit(account_no, balance_edit.text(), status_combo.currentText(), dialog))
            cancel_btn.clicked.connect(dialog.reject)

            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)
            dialog.setLayout(layout)
            dialog.exec_()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to edit account:\n{str(e)}")

    def save_account_edit(self, account_no, balance, status, dialog):
        try:
            balance_float = float(balance)
            if balance_float < 0:
                QtWidgets.QMessageBox.warning(self, "Validation", "Balance cannot be negative")
                return
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Validation", "Invalid balance amount")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                cur.execute("UPDATE Account SET Balance=%s, Status=%s WHERE AccountNo=%s",
                            (balance_float, status, account_no))
                write_audit(cur, 'UPDATE', 'Account', self.user, f'Updated account: {account_no}')
                conn.commit()

                QtWidgets.QMessageBox.information(self, "Success", "Account updated successfully!")
                dialog.accept()
                self.load_accounts()

            except Exception as e:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to update account:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def delete_account(self, account_no):
        reply = QtWidgets.QMessageBox.question(self, "Confirm Delete",
                                               "Are you sure you want to delete this account?\nThis will also delete all associated transactions!",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                conn = db_connect()
                if conn is None:
                    QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                    return

                cur = conn.cursor()
                try:
                    cur.execute("START TRANSACTION")
                    cur.execute("DELETE FROM TRANSACTION WHERE FromAccount=%s OR ToAccount=%s",
                                (account_no, account_no))
                    cur.execute("DELETE FROM Account WHERE AccountNo=%s", (account_no,))
                    write_audit(cur, 'DELETE', 'Account', self.user, f'Deleted account: {account_no}')
                    conn.commit()

                    QtWidgets.QMessageBox.information(self, "Success", "Account deleted successfully!")
                    self.load_accounts()

                except Exception as e:
                    conn.rollback()
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete account:\n{str(e)}")
                finally:
                    cur.close()
                    conn.close()

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def view_account_transactions(self, account_no):
        try:
            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor()
            cur.execute("""
                SELECT TransID, 
                       COALESCE(FromAccount, 'N/A') as FromAcc,
                       COALESCE(ToAccount, 'N/A') as ToAcc,
                       Amount, Type, Remark, DateTime 
                FROM TRANSACTION 
                WHERE FromAccount = %s OR ToAccount = %s
                ORDER BY DateTime DESC
                LIMIT 50
            """, (account_no, account_no))
            rows = cur.fetchall()
            cur.close()
            conn.close()

            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(f"Transactions for Account {account_no}")
            dialog.setFixedSize(800, 500)
            if self.current_theme == 'dark':
                dialog.setStyleSheet(ENHANCED_STYLE)
            else:
                dialog.setStyleSheet(LIGHT_STYLE)

            layout = QtWidgets.QVBoxLayout()
            table = QtWidgets.QTableWidget()
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels(["ID", "From", "To", "Amount", "Type", "Remark", "When"])
            table.horizontalHeader().setStretchLastSection(True)
            table.setAlternatingRowColors(True)
            table.setRowCount(len(rows))

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    if self.current_theme == 'dark':
                        if j == 3:
                            item.setForeground(QtGui.QColor("#f59e0b"))
                            try:
                                amount = float(value)
                                item.setText(f"Rs {amount:,.2f}")
                            except:
                                pass
                        elif j == 4:
                            if value == 'Deposit':
                                item.setForeground(QtGui.QColor("#10b981"))
                            elif value == 'Withdrawal':
                                item.setForeground(QtGui.QColor("#ef4444"))
                            elif value == 'Transfer':
                                item.setForeground(QtGui.QColor("#3b82f6"))
                    else:
                        if j == 3:
                            item.setForeground(QtGui.QColor("#d97706"))
                            try:
                                amount = float(value)
                                item.setText(f"Rs {amount:,.2f}")
                            except:
                                pass
                        elif j == 4:
                            if value == 'Deposit':
                                item.setForeground(QtGui.QColor("#059669"))
                            elif value == 'Withdrawal':
                                item.setForeground(QtGui.QColor("#dc2626"))
                            elif value == 'Transfer':
                                item.setForeground(QtGui.QColor("#2563eb"))
                    table.setItem(i, j, item)
                table.setRowHeight(i, 50)

            layout.addWidget(table)
            close_btn = QtWidgets.QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            dialog.setLayout(layout)
            dialog.exec_()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to view transactions:\n{str(e)}")

    def create_transactions_page(self):
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout()
        v.setContentsMargins(25, 25, 25, 25)
        v.setSpacing(20)

        if self.current_theme == 'dark':
            title = QtWidgets.QLabel("💸 Transaction Management")
            title.setStyleSheet("font-size:26px;font-weight:700;color:#a7f3d0;")
        else:
            title = QtWidgets.QLabel("💸 Transaction Management")
            title.setStyleSheet("font-size:26px;font-weight:700;color:#0f766e;")
        v.addWidget(title)

        if self.current_theme == 'dark':
            deposit_box = QtWidgets.QGroupBox("💰 Deposit / Withdraw")
            deposit_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #10b981;
                    border-radius: 12px;
                    background: rgba(15, 23, 32, 0.8);
                }
                QGroupBox::title {
                    color: #10b981;
                    font-weight: bold;
                }
            """)
        else:
            deposit_box = QtWidgets.QGroupBox("💰 Deposit / Withdraw")
            deposit_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #10b981;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.9);
                }
                QGroupBox::title {
                    color: #10b981;
                    font-weight: bold;
                }
            """)

        deposit_layout = QtWidgets.QFormLayout()
        deposit_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        self.tx_account = QtWidgets.QLineEdit()
        self.tx_account.setPlaceholderText("Account Number")

        self.tx_amount = QtWidgets.QLineEdit()
        self.tx_amount.setPlaceholderText("Amount")

        self.tx_remark = QtWidgets.QLineEdit()
        self.tx_remark.setPlaceholderText("Remark (optional)")

        btn_deposit = QtWidgets.QPushButton("💰 Deposit")
        btn_deposit.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #10b981, stop:1 #059669);
                border-radius: 10px;
                padding: 12px;
                font-size: 18px;
                font-weight: 600;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #34d399, stop:1 #10b981);
            }
        """)
        btn_deposit.clicked.connect(self.deposit)

        btn_withdraw = QtWidgets.QPushButton("💸 Withdraw")
        btn_withdraw.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #f59e0b, stop:1 #d97706);
                border-radius: 10px;
                padding: 12px;
                font-size: 18px;
                font-weight: 600;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #fbbf24, stop:1 #f59e0b);
            }
        """)
        btn_withdraw.clicked.connect(self.withdraw)

        deposit_layout.addRow("🏦 Account No:", self.tx_account)
        deposit_layout.addRow("💵 Amount:", self.tx_amount)
        deposit_layout.addRow("📝 Remark:", self.tx_remark)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(btn_deposit)
        button_layout.addWidget(btn_withdraw)
        deposit_layout.addRow("", button_layout)
        deposit_box.setLayout(deposit_layout)
        v.addWidget(deposit_box)

        if self.current_theme == 'dark':
            transfer_box = QtWidgets.QGroupBox("🔄 Transfer Funds")
            transfer_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #3b82f6;
                    border-radius: 12px;
                    background: rgba(15, 23, 32, 0.8);
                }
                QGroupBox::title {
                    color: #3b82f6;
                    font-weight: bold;
                }
            """)
        else:
            transfer_box = QtWidgets.QGroupBox("🔄 Transfer Funds")
            transfer_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #3b82f6;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.9);
                }
                QGroupBox::title {
                    color: #3b82f6;
                    font-weight: bold;
                }
            """)

        transfer_layout = QtWidgets.QFormLayout()
        transfer_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        self.tr_from = QtWidgets.QLineEdit()
        self.tr_from.setPlaceholderText("From Account Number")

        self.tr_to = QtWidgets.QLineEdit()
        self.tr_to.setPlaceholderText("To Account Number")

        self.tr_amount = QtWidgets.QLineEdit()
        self.tr_amount.setPlaceholderText("Amount")

        self.tr_remark = QtWidgets.QLineEdit()
        self.tr_remark.setPlaceholderText("Remark (optional)")

        btn_transfer = QtWidgets.QPushButton("🔄 Transfer")
        btn_transfer.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3b82f6, stop:1 #1d4ed8);
                border-radius: 10px;
                padding: 12px;
                font-size: 18px;
                font-weight: 600;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4f46e5, stop:1 #3730a3);
            }
        """)
        btn_transfer.clicked.connect(self.transfer)

        transfer_layout.addRow("➡️ From Account:", self.tr_from)
        transfer_layout.addRow("⬅️ To Account:", self.tr_to)
        transfer_layout.addRow("💵 Amount:", self.tr_amount)
        transfer_layout.addRow("📝 Remark:", self.tr_remark)
        transfer_layout.addRow("", btn_transfer)
        transfer_box.setLayout(transfer_layout)
        v.addWidget(transfer_box)

        if self.current_theme == 'dark':
            history_box = QtWidgets.QGroupBox("📋 Transaction History")
            history_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #0ea5a4;
                    border-radius: 12px;
                    background: rgba(15, 23, 32, 0.8);
                }
                QGroupBox::title {
                    color: #0ea5a4;
                    font-weight: bold;
                }
            """)
        else:
            history_box = QtWidgets.QGroupBox("📋 Transaction History")
            history_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #0ea5a4;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.9);
                }
                QGroupBox::title {
                    color: #0ea5a4;
                    font-weight: bold;
                }
            """)

        history_layout = QtWidgets.QVBoxLayout()
        self.tx_table = QtWidgets.QTableWidget()
        self.tx_table.setColumnCount(7)
        self.tx_table.setHorizontalHeaderLabels(["ID", "From", "To", "Amount", "Type", "Remark", "When"])
        self.tx_table.horizontalHeader().setStretchLastSection(True)
        self.tx_table.setAlternatingRowColors(True)
        history_layout.addWidget(self.tx_table)

        btn_refresh = QtWidgets.QPushButton("🔄 Refresh Transactions")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #6b7280, stop:1 #4b5563);
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                font-weight: 600;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #9ca3af, stop:1 #6b7280);
            }
        """)
        btn_refresh.clicked.connect(self.load_transactions)
        history_layout.addWidget(btn_refresh)
        history_box.setLayout(history_layout)
        v.addWidget(history_box)

        w.setLayout(v)
        return w

    def deposit(self):
        account_no = self.tx_account.text().strip()
        amount_str = self.tx_amount.text().strip()
        remark = self.tx_remark.text().strip()

        if not account_no or not amount_str:
            QtWidgets.QMessageBox.warning(self, "Validation", "Account number and amount are required")
            return

        try:
            amount = decimal.Decimal(amount_str)
            if amount <= 0:
                QtWidgets.QMessageBox.warning(self, "Validation", "Amount must be positive")
                return
        except (ValueError, decimal.InvalidOperation):
            QtWidgets.QMessageBox.warning(self, "Validation", "Invalid amount")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                cur.execute("SELECT Balance, Status FROM Account WHERE AccountNo=%s", (account_no,))
                account = cur.fetchone()

                if not account:
                    raise Exception("Account not found")

                if account[1] != 'Active':
                    raise Exception("Account is not active")

                new_balance = account[0] + amount
                cur.execute("UPDATE Account SET Balance=%s WHERE AccountNo=%s", (new_balance, account_no))
                cur.execute("""
                    INSERT INTO TRANSACTION (FromAccount, ToAccount, Amount, Type, Remark) 
                    VALUES (NULL, %s, %s, 'Deposit', %s)
                """, (account_no, amount, remark))

                write_audit(cur, 'INSERT', 'TRANSACTION', self.user, f'Deposit {amount} to account {account_no}')
                conn.commit()

                QtWidgets.QMessageBox.information(self, "Success",
                                                  f"Deposit of Rs {float(amount):,.2f} completed successfully!\nNew balance: Rs {float(new_balance):,.2f}")
                self.tx_account.clear()
                self.tx_amount.clear()
                self.tx_remark.clear()
                self.load_transactions()
                self.refresh_dashboard()

            except Exception as e:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Deposit failed:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def withdraw(self):
        account_no = self.tx_account.text().strip()
        amount_str = self.tx_amount.text().strip()
        remark = self.tx_remark.text().strip()

        if not account_no or not amount_str:
            QtWidgets.QMessageBox.warning(self, "Validation", "Account number and amount are required")
            return

        try:
            amount = decimal.Decimal(amount_str)
            if amount <= 0:
                QtWidgets.QMessageBox.warning(self, "Validation", "Amount must be positive")
                return
        except (ValueError, decimal.InvalidOperation):
            QtWidgets.QMessageBox.warning(self, "Validation", "Invalid amount")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                cur.execute("SELECT Balance, Status FROM Account WHERE AccountNo=%s", (account_no,))
                account = cur.fetchone()

                if not account:
                    raise Exception("Account not found")

                if account[1] != 'Active':
                    raise Exception("Account is not active")

                if account[0] < amount:
                    raise Exception("Insufficient balance")

                new_balance = account[0] - amount
                cur.execute("UPDATE Account SET Balance=%s WHERE AccountNo=%s", (new_balance, account_no))
                cur.execute("""
                    INSERT INTO TRANSACTION (FromAccount, ToAccount, Amount, Type, Remark) 
                    VALUES (%s, NULL, %s, 'Withdrawal', %s)
                """, (account_no, amount, remark))

                write_audit(cur, 'INSERT', 'TRANSACTION', self.user, f'Withdrawal {amount} from account {account_no}')
                conn.commit()

                QtWidgets.QMessageBox.information(self, "Success",
                                                  f"Withdrawal of Rs {float(amount):,.2f} completed successfully!\nNew balance: Rs {float(new_balance):,.2f}")
                self.tx_account.clear()
                self.tx_amount.clear()
                self.tx_remark.clear()
                self.load_transactions()
                self.refresh_dashboard()

            except Exception as e:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Withdrawal failed:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def transfer(self):
        from_account = self.tr_from.text().strip()
        to_account = self.tr_to.text().strip()
        amount_str = self.tr_amount.text().strip()
        remark = self.tr_remark.text().strip()

        if not from_account or not to_account or not amount_str:
            QtWidgets.QMessageBox.warning(self, "Validation", "From account, to account and amount are required")
            return

        if from_account == to_account:
            QtWidgets.QMessageBox.warning(self, "Validation", "Cannot transfer to the same account")
            return

        try:
            amount = decimal.Decimal(amount_str)
            if amount <= 0:
                QtWidgets.QMessageBox.warning(self, "Validation", "Amount must be positive")
                return
        except (ValueError, decimal.InvalidOperation):
            QtWidgets.QMessageBox.warning(self, "Validation", "Invalid amount")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                cur.execute("SELECT Balance, Status FROM Account WHERE AccountNo=%s", (from_account,))
                from_acc = cur.fetchone()

                if not from_acc:
                    raise Exception("From account not found")

                if from_acc[1] != 'Active':
                    raise Exception("From account is not active")

                cur.execute("SELECT Balance, Status FROM Account WHERE AccountNo=%s", (to_account,))
                to_acc = cur.fetchone()

                if not to_acc:
                    raise Exception("To account not found")

                if to_acc[1] != 'Active':
                    raise Exception("To account is not active")

                if from_acc[0] < amount:
                    raise Exception("Insufficient balance in from account")

                new_balance_from = from_acc[0] - amount
                new_balance_to = to_acc[0] + amount

                cur.execute("UPDATE Account SET Balance=%s WHERE AccountNo=%s", (new_balance_from, from_account))
                cur.execute("UPDATE Account SET Balance=%s WHERE AccountNo=%s", (new_balance_to, to_account))
                cur.execute("""
                    INSERT INTO TRANSACTION (FromAccount, ToAccount, Amount, Type, Remark) 
                    VALUES (%s, %s, %s, 'Transfer', %s)
                """, (from_account, to_account, amount, remark))

                write_audit(cur, 'INSERT', 'TRANSACTION', self.user,
                            f'Transfer {amount} from {from_account} to {to_account}')
                conn.commit()

                QtWidgets.QMessageBox.information(self, "Success",
                                                  f"Transfer of Rs {float(amount):,.2f} completed successfully!\n"
                                                  f"From account new balance: Rs {float(new_balance_from):,.2f}\n"
                                                  f"To account new balance: Rs {float(new_balance_to):,.2f}")

                self.tr_from.clear()
                self.tr_to.clear()
                self.tr_amount.clear()
                self.tr_remark.clear()
                self.load_transactions()
                self.refresh_dashboard()

            except Exception as e:
                conn.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Transfer failed:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def load_transactions(self):
        self.loading_overlay.show_loading("Loading transactions...")
        try:
            conn = db_connect()
            if conn is None:
                return

            cur = conn.cursor()
            cur.execute("""
                SELECT TransID, 
                       COALESCE(FromAccount, 'N/A') as FromAcc,
                       COALESCE(ToAccount, 'N/A') as ToAcc,
                       Amount, Type, Remark, DateTime 
                FROM TRANSACTION 
                ORDER BY DateTime DESC
                LIMIT 100
            """)
            rows = cur.fetchall()
            self.tx_table.setRowCount(len(rows))

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    if self.current_theme == 'dark':
                        if j == 3:
                            item.setForeground(QtGui.QColor("#f59e0b"))
                            try:
                                amount = float(value)
                                item.setText(f"Rs {amount:,.2f}")
                            except:
                                pass
                        elif j == 4:
                            if value == 'Deposit':
                                item.setForeground(QtGui.QColor("#10b981"))
                            elif value == 'Withdrawal':
                                item.setForeground(QtGui.QColor("#ef4444"))
                            elif value == 'Transfer':
                                item.setForeground(QtGui.QColor("#3b82f6"))
                    else:
                        if j == 3:
                            item.setForeground(QtGui.QColor("#d97706"))
                            try:
                                amount = float(value)
                                item.setText(f"Rs {amount:,.2f}")
                            except:
                                pass
                        elif j == 4:
                            if value == 'Deposit':
                                item.setForeground(QtGui.QColor("#059669"))
                            elif value == 'Withdrawal':
                                item.setForeground(QtGui.QColor("#dc2626"))
                            elif value == 'Transfer':
                                item.setForeground(QtGui.QColor("#2563eb"))
                    self.tx_table.setItem(i, j, item)
                self.tx_table.setRowHeight(i, 60)

            cur.close()
            conn.close()

        except Exception as e:
            print("Load transactions error:", e)
        finally:
            self.loading_overlay.hide_loading()

    def create_tcl_demo_page(self):
        # Create a scroll area for the entire page
        scroll_widget = QtWidgets.QWidget()
        scroll_widget.setObjectName("tclScrollWidget")

        v = QtWidgets.QVBoxLayout()
        v.setContentsMargins(25, 25, 25, 25)
        v.setSpacing(30)

        if self.current_theme == 'dark':
            title = QtWidgets.QLabel("⚙️ TCL Commands Demonstration")
            title.setStyleSheet("font-size:26px;font-weight:700;color:#a7f3d0;")
        else:
            title = QtWidgets.QLabel("⚙️ TCL Commands Demonstration")
            title.setStyleSheet("font-size:26px;font-weight:700;color:#0f766e;")
        v.addWidget(title)

        if self.current_theme == 'dark':
            demo_box = QtWidgets.QGroupBox("Transaction Control Language (TCL) Demo")
            demo_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #f59e0b;
                    border-radius: 12px;
                    background: rgba(15, 23, 32, 0.8);
                    padding: 15px;
                }
                QGroupBox::title {
                    color: #f59e0b;
                    font-weight: bold;
                    font-size: 20px;
                    padding: 5px 15px;
                    subcontrol-origin: margin;
                    left: 10px;
                }
            """)
        else:
            demo_box = QtWidgets.QGroupBox("Transaction Control Language (TCL) Demo")
            demo_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #f59e0b;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.95);
                    padding: 15px;
                }
                QGroupBox::title {
                    color: #f59e0b;
                    font-weight: bold;
                    font-size: 20px;
                    padding: 5px 15px;
                    subcontrol-origin: margin;
                    left: 10px;
                }
            """)

        demo_layout = QtWidgets.QVBoxLayout()
        demo_layout.setSpacing(25)
        demo_layout.setContentsMargins(10, 25, 10, 10)  # Added more top margin for title

        # Create demo scenarios
        commit_box = self.create_demo_scenario(
            "1. COMMIT Demo - Successful Transaction",
            "Demonstrates BEGIN → Update Balance → COMMIT\nBalance updated permanently in database",
            "🚀 Execute COMMIT Demo",
            self.demo_commit,
            "#10b981"
        )
        demo_layout.addWidget(commit_box)

        rollback_box = self.create_demo_scenario(
            "2. ROLLBACK Demo - Transaction with Error",
            "Demonstrates BEGIN → Operation → Error → ROLLBACK\nNo changes applied when error occurs",
            "🔄 Execute ROLLBACK Demo",
            self.demo_rollback,
            "#ef4444"
        )
        demo_layout.addWidget(rollback_box)

        savepoint_box = self.create_demo_scenario(
            "3. SAVEPOINT Demo - Partial Rollback",
            "Demonstrates BEGIN → Insert Record → SAVEPOINT A → Insert Another → ROLLBACK TO A\nPartial operation undone while keeping first insert",
            "🎯 Execute SAVEPOINT Demo",
            self.demo_savepoint,
            "#3b82f6"
        )
        demo_layout.addWidget(savepoint_box)

        atomic_box = self.create_demo_scenario(
            "4. ATOMIC Transfer Demo - All or Nothing",
            "Demonstrates BEGIN → Debit Sender → Credit Receiver → COMMIT\nBoth accounts updated atomically (all or nothing)",
            "⚡ Execute Atomic Transfer",
            self.demo_atomic_transfer,
            "#8b5cf6"
        )
        demo_layout.addWidget(atomic_box)

        demo_box.setLayout(demo_layout)
        v.addWidget(demo_box)

        if self.current_theme == 'dark':
            results_box = QtWidgets.QGroupBox("📊 Demo Results")
            results_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #0ea5a4;
                    border-radius: 12px;
                    background: rgba(15, 23, 32, 0.8);
                    padding: 15px;
                }
                QGroupBox::title {
                    color: #0ea5a4;
                    font-weight: bold;
                    font-size: 18px;
                    padding: 5px 15px;
                    subcontrol-origin: margin;
                    left: 10px;
                }
            """)
        else:
            results_box = QtWidgets.QGroupBox("📊 Demo Results")
            results_box.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #0ea5a4;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.95);
                    padding: 15px;
                }
                QGroupBox::title {
                    color: #0ea5a4;
                    font-weight: bold;
                    font-size: 18px;
                    padding: 5px 15px;
                    subcontrol-origin: margin;
                    left: 10px;
                }
            """)

        results_layout = QtWidgets.QVBoxLayout()
        self.tcl_results = QtWidgets.QTextEdit()
        self.tcl_results.setReadOnly(True)
        self.tcl_results.setMaximumHeight(250)
        self.tcl_results.setMinimumHeight(200)
        if self.current_theme == 'dark':
            self.tcl_results.setStyleSheet("""
                QTextEdit {
                    background: #071014;
                    border: 2px solid #164e4d;
                    border-radius: 8px;
                    padding: 10px;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 14px;
                    color: #dbeafe;
                }
            """)
        else:
            self.tcl_results.setStyleSheet("""
                QTextEdit {
                    background: white;
                    border: 2px solid #cbd5e1;
                    border-radius: 8px;
                    padding: 10px;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 14px;
                    color: #1e293b;
                }
            """)
        results_layout.addWidget(self.tcl_results)
        results_box.setLayout(results_layout)
        v.addWidget(results_box)

        v.addStretch()
        scroll_widget.setLayout(v)

        # Create scroll area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        if self.current_theme == 'dark':
            scroll_area.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background: transparent;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #1e293b;
                    width: 12px;
                    margin: 0px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background: #0ea5a4;
                    min-height: 20px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #14b8b4;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                    height: 0px;
                }
            """)
        else:
            scroll_area.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background: transparent;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #e2e8f0;
                    width: 12px;
                    margin: 0px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background: #0ea5a4;
                    min-height: 20px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #14b8b4;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                    height: 0px;
                }
            """)

        return scroll_area

    def create_demo_scenario(self, title, description, button_text, action, color):
        box = QtWidgets.QGroupBox(title)

        if self.current_theme == 'dark':
            box.setStyleSheet(f"""
                QGroupBox {{
                    border: 2px solid {color};
                    border-radius: 12px;
                    background: rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 0.1);
                    padding: 15px;
                }}
                QGroupBox::title {{
                    color: {color};
                    font-weight: bold;
                    font-size: 18px;
                    padding: 5px 10px;
                    subcontrol-origin: margin;
                    left: 10px;
                }}
            """)
        else:
            box.setStyleSheet(f"""
                QGroupBox {{
                    border: 2px solid {color};
                    border-radius: 12px;
                    background: rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 0.05);
                    padding: 15px;
                }}
                QGroupBox::title {{
                    color: {color};
                    font-weight: bold;
                    font-size: 18px;
                    padding: 5px 10px;
                    subcontrol-origin: margin;
                    left: 10px;
                }}
            """)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(10, 20, 10, 10)

        # Description with proper word wrap
        desc_label = QtWidgets.QLabel(description)
        desc_label.setWordWrap(True)
        if self.current_theme == 'dark':
            desc_label.setStyleSheet("color: #cbd5e1; font-size: 15px; line-height: 1.4;")
        else:
            desc_label.setStyleSheet("color: #475569; font-size: 15px; line-height: 1.4;")
        layout.addWidget(desc_label)

        # Input fields section
        if "COMMIT" in title:
            input_container = QtWidgets.QWidget()
            input_layout = QtWidgets.QHBoxLayout()
            input_layout.setContentsMargins(0, 10, 0, 0)
            input_layout.setSpacing(10)

            # Account input
            acc_label = QtWidgets.QLabel("Account:")
            acc_label.setMinimumWidth(70)
            self.commit_acc = QtWidgets.QLineEdit()
            self.commit_acc.setPlaceholderText("Account Number")
            self.commit_acc.setMinimumWidth(150)
            self.commit_acc.setMaximumWidth(200)

            # Amount input
            amount_label = QtWidgets.QLabel("Amount:")
            amount_label.setMinimumWidth(60)
            self.commit_amount = QtWidgets.QLineEdit()
            self.commit_amount.setPlaceholderText("Deposit Amount")
            self.commit_amount.setMinimumWidth(150)
            self.commit_amount.setMaximumWidth(200)

            input_layout.addWidget(acc_label)
            input_layout.addWidget(self.commit_acc)
            input_layout.addSpacing(20)
            input_layout.addWidget(amount_label)
            input_layout.addWidget(self.commit_amount)
            input_layout.addStretch()

            input_container.setLayout(input_layout)
            layout.addWidget(input_container)

        elif "ROLLBACK" in title:
            input_container = QtWidgets.QWidget()
            input_layout = QtWidgets.QHBoxLayout()
            input_layout.setContentsMargins(0, 10, 0, 0)
            input_layout.setSpacing(10)

            # Account input
            acc_label = QtWidgets.QLabel("Account:")
            acc_label.setMinimumWidth(70)
            self.rollback_acc = QtWidgets.QLineEdit()
            self.rollback_acc.setPlaceholderText("Account Number")
            self.rollback_acc.setMinimumWidth(150)
            self.rollback_acc.setMaximumWidth(200)

            # Amount input
            amount_label = QtWidgets.QLabel("Amount:")
            amount_label.setMinimumWidth(60)
            self.rollback_amount = QtWidgets.QLineEdit()
            self.rollback_amount.setPlaceholderText("Withdrawal Amount")
            self.rollback_amount.setMinimumWidth(150)
            self.rollback_amount.setMaximumWidth(200)

            input_layout.addWidget(acc_label)
            input_layout.addWidget(self.rollback_acc)
            input_layout.addSpacing(20)
            input_layout.addWidget(amount_label)
            input_layout.addWidget(self.rollback_amount)
            input_layout.addStretch()

            input_container.setLayout(input_layout)
            layout.addWidget(input_container)

        elif "SAVEPOINT" in title:
            input_container = QtWidgets.QWidget()
            input_layout = QtWidgets.QHBoxLayout()
            input_layout.setContentsMargins(0, 10, 0, 0)
            input_layout.setSpacing(10)

            # First customer
            cust1_label = QtWidgets.QLabel("Customer 1:")
            cust1_label.setMinimumWidth(80)
            self.savepoint_name1 = QtWidgets.QLineEdit()
            self.savepoint_name1.setPlaceholderText("First Customer Name")
            self.savepoint_name1.setMinimumWidth(180)
            self.savepoint_name1.setMaximumWidth(250)

            # Second customer
            cust2_label = QtWidgets.QLabel("Customer 2:")
            cust2_label.setMinimumWidth(80)
            self.savepoint_name2 = QtWidgets.QLineEdit()
            self.savepoint_name2.setPlaceholderText("Second Customer Name")
            self.savepoint_name2.setMinimumWidth(180)
            self.savepoint_name2.setMaximumWidth(250)

            input_layout.addWidget(cust1_label)
            input_layout.addWidget(self.savepoint_name1)
            input_layout.addSpacing(20)
            input_layout.addWidget(cust2_label)
            input_layout.addWidget(self.savepoint_name2)
            input_layout.addStretch()

            input_container.setLayout(input_layout)
            layout.addWidget(input_container)

        elif "ATOMIC" in title:
            input_container = QtWidgets.QWidget()
            input_layout = QtWidgets.QGridLayout()
            input_layout.setContentsMargins(0, 10, 0, 0)
            input_layout.setHorizontalSpacing(15)
            input_layout.setVerticalSpacing(10)

            # From account
            from_label = QtWidgets.QLabel("From Account:")
            self.atomic_from = QtWidgets.QLineEdit()
            self.atomic_from.setPlaceholderText("Account Number")
            self.atomic_from.setMinimumWidth(200)

            # To account
            to_label = QtWidgets.QLabel("To Account:")
            self.atomic_to = QtWidgets.QLineEdit()
            self.atomic_to.setPlaceholderText("Account Number")
            self.atomic_to.setMinimumWidth(200)

            # Amount
            amount_label = QtWidgets.QLabel("Amount:")
            self.atomic_amount = QtWidgets.QLineEdit()
            self.atomic_amount.setPlaceholderText("Transfer Amount")
            self.atomic_amount.setMinimumWidth(200)

            input_layout.addWidget(from_label, 0, 0)
            input_layout.addWidget(self.atomic_from, 0, 1)
            input_layout.addWidget(to_label, 1, 0)
            input_layout.addWidget(self.atomic_to, 1, 1)
            input_layout.addWidget(amount_label, 2, 0)
            input_layout.addWidget(self.atomic_amount, 2, 1)

            input_container.setLayout(input_layout)
            layout.addWidget(input_container)

        # Button with proper styling
        button_container = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 15, 0, 0)

        btn = QtWidgets.QPushButton(button_text)
        btn.setMinimumHeight(45)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {color}, stop:1 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 150));
                border-radius: 10px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: 600;
                color: white;
                border: none;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 200),
                                            stop:1 {color});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 150),
                                            stop:1 {color});
                padding: 13px 24px 11px 26px;
            }}
        """)
        btn.clicked.connect(action)

        button_layout.addStretch()
        button_layout.addWidget(btn)
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        layout.addWidget(button_container)

        box.setLayout(layout)
        return box

    def demo_commit(self):
        account_no = self.commit_acc.text().strip()
        amount_str = self.commit_amount.text().strip()

        if not account_no or not amount_str:
            QtWidgets.QMessageBox.warning(self, "Validation", "Account number and amount are required")
            return

        try:
            amount = decimal.Decimal(amount_str)
            if amount <= 0:
                QtWidgets.QMessageBox.warning(self, "Validation", "Amount must be positive")
                return
        except (ValueError, decimal.InvalidOperation):
            QtWidgets.QMessageBox.warning(self, "Validation", "Invalid amount")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                self.tcl_results.append("🚀 BEGIN TRANSACTION executed")

                cur.execute("SELECT Balance FROM Account WHERE AccountNo=%s", (account_no,))
                result = cur.fetchone()
                if not result:
                    raise Exception("Account not found")

                old_balance = result[0]
                self.tcl_results.append(f"📊 Current balance: Rs {old_balance:,.2f}")

                new_balance = old_balance + amount
                cur.execute("UPDATE Account SET Balance=%s WHERE AccountNo=%s", (new_balance, account_no))
                self.tcl_results.append(f"💹 Balance updated to: Rs {new_balance:,.2f}")

                conn.commit()
                self.tcl_results.append("✅ COMMIT executed - Changes saved permanently")
                self.tcl_results.append("--- COMMIT Demo Completed Successfully ---\n")

                QtWidgets.QMessageBox.information(self, "COMMIT Demo", "Transaction committed successfully!")

            except Exception as e:
                conn.rollback()
                self.tcl_results.append(f"❌ Error: {str(e)}")
                self.tcl_results.append("🔄 ROLLBACK executed - No changes saved")
                QtWidgets.QMessageBox.critical(self, "Error", f"COMMIT demo failed:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def demo_rollback(self):
        account_no = self.rollback_acc.text().strip()
        amount_str = self.rollback_amount.text().strip()

        if not account_no or not amount_str:
            QtWidgets.QMessageBox.warning(self, "Validation", "Account number and amount are required")
            return

        try:
            amount = decimal.Decimal(amount_str)
            if amount <= 0:
                QtWidgets.QMessageBox.warning(self, "Validation", "Amount must be positive")
                return
        except (ValueError, decimal.InvalidOperation):
            QtWidgets.QMessageBox.warning(self, "Validation", "Invalid amount")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                self.tcl_results.append("🚀 BEGIN TRANSACTION executed")

                cur.execute("SELECT Balance FROM Account WHERE AccountNo=%s", (account_no,))
                result = cur.fetchone()
                if not result:
                    raise Exception("Account not found")

                old_balance = result[0]
                self.tcl_results.append(f"📊 Current balance: Rs {old_balance:,.2f}")

                if old_balance < amount * 10:
                    raise Exception(f"Simulated error: Cannot withdraw Rs {amount * 10:,.2f} - Insufficient funds")

                new_balance = old_balance - amount
                cur.execute("UPDATE Account SET Balance=%s WHERE AccountNo=%s", (new_balance, account_no))
                conn.commit()

            except Exception as e:
                conn.rollback()
                self.tcl_results.append(f"❌ Error occurred: {str(e)}")
                self.tcl_results.append("🔄 ROLLBACK executed - All changes reverted")
                self.tcl_results.append("--- ROLLBACK Demo Completed Successfully ---\n")

                cur.execute("SELECT Balance FROM Account WHERE AccountNo=%s", (account_no,))
                final_balance = cur.fetchone()[0]
                self.tcl_results.append(f"📊 Final balance after rollback: Rs {final_balance:,.2f} (unchanged)")

                QtWidgets.QMessageBox.information(self, "ROLLBACK Demo",
                                                  "Transaction rolled back successfully due to Invalid amount!")

            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def demo_savepoint(self):
        name1 = self.savepoint_name1.text().strip()
        name2 = self.savepoint_name2.text().strip()

        if not name1 or not name2:
            QtWidgets.QMessageBox.warning(self, "Validation", "Both customer names are required")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                self.tcl_results.append("🚀 BEGIN TRANSACTION executed")

                cur.execute("INSERT INTO Customer (Name, CNIC, Contact) VALUES (%s, %s, %s)",
                            (name1, f"CNIC_{datetime.now().strftime('%H%M%S')}_1", "0300-1111111"))
                customer_id_1 = cur.lastrowid
                self.tcl_results.append(f"👤 First customer inserted (ID: {customer_id_1})")

                cur.execute("SAVEPOINT after_first_insert")
                self.tcl_results.append("📍 SAVEPOINT 'after_first_insert' created")

                cur.execute("INSERT INTO Customer (Name, CNIC, Contact) VALUES (%s, %s, %s)",
                            (name2, f"CNIC_{datetime.now().strftime('%H%M%S')}_2", "0300-2222222"))
                customer_id_2 = cur.lastrowid
                self.tcl_results.append(f"👤 Second customer inserted (ID: {customer_id_2})")

                self.tcl_results.append("⚠️  Simulating error condition...")
                cur.execute("ROLLBACK TO SAVEPOINT after_first_insert")
                self.tcl_results.append("↩️  ROLLBACK TO SAVEPOINT executed - Second insert undone")

                conn.commit()
                self.tcl_results.append("✅ COMMIT executed - First customer saved permanently")
                self.tcl_results.append("--- SAVEPOINT Demo Completed Successfully ---\n")

                QtWidgets.QMessageBox.information(self, "SAVEPOINT Demo",
                                                  f"Savepoint demo completed!\n"
                                                  f"First customer '{name1}' was saved.\n"
                                                  f"Second customer '{name2}' was rolled back.")

                self.load_customers()

            except Exception as e:
                conn.rollback()
                self.tcl_results.append(f"❌ Error: {str(e)}")
                QtWidgets.QMessageBox.critical(self, "Error", f"SAVEPOINT demo failed:\n{str(e)}")
            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def demo_atomic_transfer(self):
        from_acc = self.atomic_from.text().strip()
        to_acc = self.atomic_to.text().strip()
        amount_str = self.atomic_amount.text().strip()

        if not from_acc or not to_acc or not amount_str:
            QtWidgets.QMessageBox.warning(self, "Validation", "From account, to account and amount are required")
            return

        try:
            amount = decimal.Decimal(amount_str)
            if amount <= 0:
                QtWidgets.QMessageBox.warning(self, "Validation", "Amount must be positive")
                return
        except (ValueError, decimal.InvalidOperation):
            QtWidgets.QMessageBox.warning(self, "Validation", "Invalid amount")
            return

        try:
            conn = db_connect()
            if conn is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Cannot connect to database")
                return

            cur = conn.cursor()
            try:
                cur.execute("START TRANSACTION")
                self.tcl_results.append("🚀 BEGIN TRANSACTION executed - Starting atomic transfer")

                cur.execute("SELECT Balance FROM Account WHERE AccountNo=%s", (from_acc,))
                from_balance = cur.fetchone()
                if not from_balance:
                    raise Exception("From account not found")

                cur.execute("SELECT Balance FROM Account WHERE AccountNo=%s", (to_acc,))
                to_balance = cur.fetchone()
                if not to_balance:
                    raise Exception("To account not found")

                self.tcl_results.append(f"📊 From account balance: Rs {from_balance[0]:,.2f}")
                self.tcl_results.append(f"📊 To account balance: Rs {to_balance[0]:,.2f}")

                if from_balance[0] < amount:
                    raise Exception("Insufficient funds - simulating atomic rollback")

                new_from_balance = from_balance[0] - amount
                cur.execute("UPDATE Account SET Balance=%s WHERE AccountNo=%s", (new_from_balance, from_acc))
                self.tcl_results.append(f"➖ Debited Rs {amount:,.2f} from account {from_acc}")

                new_to_balance = to_balance[0] + amount
                cur.execute("UPDATE Account SET Balance=%s WHERE AccountNo=%s", (new_to_balance, to_acc))
                self.tcl_results.append(f"➕ Credited Rs {amount:,.2f} to account {to_acc}")

                conn.commit()
                self.tcl_results.append("✅ COMMIT executed - Transfer completed atomically")
                self.tcl_results.append("--- Atomic Transfer Demo Completed Successfully ---\n")

                QtWidgets.QMessageBox.information(self, "Atomic Transfer",
                                                  f"Atomic transfer completed successfully!\n"
                                                  f"Rs {amount:,.2f} transferred from {from_acc} to {to_acc}")

                self.refresh_dashboard()

            except Exception as e:
                conn.rollback()
                self.tcl_results.append(f"❌ Error: {str(e)}")
                self.tcl_results.append("🔄 Automatic ROLLBACK - Both debit and credit reverted")
                self.tcl_results.append("--- Atomic Transfer Demo: All or Nothing Principle Demonstrated ---\n")

                QtWidgets.QMessageBox.information(self, "Atomic Transfer",
                                                  f"Transfer failed and was rolled back atomically!\n"
                                                  f"Error: {str(e)}")

            finally:
                cur.close()
                conn.close()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))

    def load_tcl_demo(self):
        self.tcl_results.clear()
        self.tcl_results.append("✨ TCL Commands Demonstration Ready...\n")
        self.tcl_results.append("This interactive demo shows:\n")
        self.tcl_results.append("• ✅ COMMIT - Permanent save of transaction\n")
        self.tcl_results.append("• ↩️ ROLLBACK - Revert changes on error\n")
        self.tcl_results.append("• 📍 SAVEPOINT - Partial rollback capability\n")
        self.tcl_results.append("• ⚡ ATOMICITY - All operations succeed or fail together\n")
        self.tcl_results.append("\n💡 Click on any demo button above to start...")

    def toggle_theme(self):
        if self.current_theme == 'dark':
            self.apply_light_theme()
        else:
            self.apply_dark_theme()

    def apply_light_theme(self):
        self.setStyleSheet(LIGHT_STYLE)
        self.current_theme = 'light'
        self.btn_theme.setText("🌙 Switch to Dark Mode")

        try:
            central = self.centralWidget()
            if central:
                main_layout = central.layout()
                if main_layout and main_layout.count() > 1:
                    main_content = main_layout.itemAt(1).widget()
                    if main_content:
                        content_layout = main_content.layout()
                        if content_layout and content_layout.count() > 2:
                            footer = content_layout.itemAt(2).widget()
                            if footer:
                                footer.setStyleSheet("""
                                    QFrame {
                                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                                    stop:0 #f0fdfa, stop:1 #0ea5a4);
                                        border-top: 3px solid #0d9488;
                                    }
                                """)
        except:
            pass

        self.refresh_dashboard()

    def apply_dark_theme(self):
        self.setStyleSheet(ENHANCED_STYLE)
        self.current_theme = 'dark'
        self.btn_theme.setText("☀️ Switch to Light Mode")

        try:
            central = self.centralWidget()
            if central:
                main_layout = central.layout()
                if main_layout and main_layout.count() > 1:
                    main_content = main_layout.itemAt(1).widget()
                    if main_content:
                        content_layout = main_content.layout()
                        if content_layout and content_layout.count() > 2:
                            footer = content_layout.itemAt(2).widget()
                            if footer:
                                footer.setStyleSheet("""
                                    QFrame {
                                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                                    stop:0 #042a2a, stop:1 #0ea5a4);
                                        border-top: 3px solid #7fe6d9;
                                    }
                                """)
        except:
            pass

        self.refresh_dashboard()

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.page_dash)
        self.refresh_dashboard()
        self.highlight_nav_button("📊 Dashboard")

    def show_customers(self):
        self.stack.setCurrentWidget(self.page_cust)
        self.load_customers()
        self.highlight_nav_button("👥 Customers")

    def show_accounts(self):
        self.stack.setCurrentWidget(self.page_acc)
        self.load_accounts()
        self.highlight_nav_button("💳 Accounts")

    def show_transactions(self):
        self.stack.setCurrentWidget(self.page_tx)
        self.load_transactions()
        self.highlight_nav_button("💸 Transactions")

    def show_tcl_demo(self):
        self.stack.setCurrentWidget(self.page_tcl)
        self.load_tcl_demo()
        self.highlight_nav_button("⚙️ TCL Demo")

    def highlight_nav_button(self, button_text):
        for btn in self.nav_buttons.values():
            btn.setStyleSheet(btn.styleSheet().replace("border-left: 4px solid", "border-left: 0px solid"))

        if button_text in self.nav_buttons:
            current_btn = self.nav_buttons[button_text]
            if "Dashboard" in button_text:
                color = "#0ea5a4"
            elif "Customers" in button_text:
                color = "#3b82f6"
            elif "Accounts" in button_text:
                color = "#8b5cf6"
            elif "Transactions" in button_text:
                color = "#10b981"
            elif "TCL Demo" in button_text:
                color = "#f59e0b"
            else:
                color = "#0ea5a4"

            if self.current_theme == 'dark':
                current_btn.setStyleSheet(f"""
                    QPushButton#sideBtn {{
                        text-align: left;
                        padding: 15px 25px;
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                    stop:0 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 100),
                                                    stop:1 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 50));
                        border: none;
                        font-size: 18px;
                        color: white;
                        font-weight: 600;
                        border-radius: 8px;
                        border-left: 4px solid {color};
                    }}
                """)
            else:
                current_btn.setStyleSheet(f"""
                    QPushButton#sideBtn {{
                        text-align: left;
                        padding: 15px 25px;
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                    stop:0 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 50),
                                                    stop:1 rgba({hex_to_rgb(color)[0]}, {hex_to_rgb(color)[1]}, {hex_to_rgb(color)[2]}, 20));
                        border: none;
                        font-size: 18px;
                        color: #0f766e;
                        font-weight: 600;
                        border-radius: 8px;
                        border-left: 4px solid {color};
                    }}
                """)


# ----------------------------
# Database Initialization Script - MODIFIED
def initialize_database():
    conn = db_connect()
    if not conn:
        print("Cannot connect to database for initialization")
        return False

    try:
        cur = conn.cursor()
        cur.execute("DROP DATABASE IF EXISTS cbs_dbs")
        cur.execute("CREATE DATABASE cbs_dbs")
        cur.execute("USE cbs_dbs")

        cur.execute("""
            CREATE TABLE BRANCH (
                BranchID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Address TEXT,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE EMPLOYEE (
                EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Role VARCHAR(50) NOT NULL,
                BranchID INT,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (BranchID) REFERENCES BRANCH(BranchID)
            )
        """)

        cur.execute("""
            CREATE TABLE CUSTOMER (
                CustomerID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                CNIC VARCHAR(15) UNIQUE NOT NULL,
                Contact VARCHAR(15),
                Type ENUM('Individual', 'Business') DEFAULT 'Individual',
                DOB DATE,
                Password VARCHAR(100) NOT NULL DEFAULT '123456',  -- Added password field
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE ACCOUNTTYPE (
                AccountTypeID INT AUTO_INCREMENT PRIMARY KEY,
                TypeName VARCHAR(50) NOT NULL,
                Description TEXT,
                MinBalance DECIMAL(15,2) DEFAULT 0
            )
        """)

        cur.execute("""
            CREATE TABLE ACCOUNT (
                AccountNo INT AUTO_INCREMENT PRIMARY KEY,
                CustomerID INT NOT NULL,
                Type VARCHAR(20) NOT NULL,
                Balance DECIMAL(15,2) DEFAULT 0,
                Status ENUM('Active', 'Closed', 'Suspended') DEFAULT 'Active',
                BranchID INT,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (CustomerID) REFERENCES CUSTOMER(CustomerID),
                FOREIGN KEY (BranchID) REFERENCES BRANCH(BranchID)
            )
        """)

        cur.execute("""
            CREATE TABLE TRANSACTION (
                TransID INT AUTO_INCREMENT PRIMARY KEY,
                FromAccount INT,
                ToAccount INT,
                Amount DECIMAL(15,2) NOT NULL,
                Type ENUM('Deposit', 'Withdrawal', 'Transfer') NOT NULL,
                Remark TEXT,
                DateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (FromAccount) REFERENCES ACCOUNT(AccountNo),
                FOREIGN KEY (ToAccount) REFERENCES ACCOUNT(AccountNo)
            )
        """)

        cur.execute("""
            CREATE TABLE AuditLog (
                LogID INT AUTO_INCREMENT PRIMARY KEY,
                Operation VARCHAR(50) NOT NULL,
                TableAffected VARCHAR(50) NOT NULL,
                UserName VARCHAR(50) NOT NULL,
                Details TEXT,
                DateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE AppUser (
                UserID INT AUTO_INCREMENT PRIMARY KEY,
                Username VARCHAR(50) UNIQUE NOT NULL,
                Password VARCHAR(100) NOT NULL,
                Role VARCHAR(20) DEFAULT 'admin',
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("INSERT INTO BRANCH (Name, Address) VALUES ('Main Branch', '123 Banking Street, City')")
        cur.execute("INSERT INTO EMPLOYEE (Name, Role, BranchID) VALUES ('Admin Manager', 'Manager', 1)")
        cur.execute(
            "INSERT INTO ACCOUNTTYPE (TypeName, Description, MinBalance) VALUES ('Savings', 'Regular Savings Account', 500)")
        cur.execute(
            "INSERT INTO ACCOUNTTYPE (TypeName, Description, MinBalance) VALUES ('Current', 'Business Current Account', 1000)")
        cur.execute(
            "INSERT INTO ACCOUNTTYPE (TypeName, Description, MinBalance) VALUES ('Basic Banking', 'Basic Banking Account', 0)")
        cur.execute("INSERT INTO AppUser (Username, Password, Role) VALUES ('admin', 'admin123', 'admin')")

        # Add sample customers with passwords
        cur.execute(
            "INSERT INTO CUSTOMER (Name, CNIC, Contact, Type, Password) VALUES ('John Doe', '4220112345678', '03001234567', 'Individual', 'john123')")
        cur.execute(
            "INSERT INTO CUSTOMER (Name, CNIC, Contact, Type, Password) VALUES ('Jane Smith', '4220176543210', '03009876543', 'Individual', 'jane123')")
        cur.execute(
            "INSERT INTO CUSTOMER (Name, CNIC, Contact, Type, Password) VALUES ('ABC Corporation', '4220155555555', '02112345678', 'Business', 'abc123')")

        # Add accounts for sample customers
        cur.execute("INSERT INTO ACCOUNT (CustomerID, Type, Balance, BranchID) VALUES (1, 'Savings', 50000.00, 1)")
        cur.execute("INSERT INTO ACCOUNT (CustomerID, Type, Balance, BranchID) VALUES (2, 'Current', 75000.00, 1)")
        cur.execute(
            "INSERT INTO ACCOUNT (CustomerID, Type, Balance, BranchID) VALUES (3, 'Basic Banking', 100000.00, 1)")

        conn.commit()
        print("Database initialized successfully!")
        print("\nSample login credentials:")
        print("Admin: username='admin', password='admin123'")
        print("Customer 1: name='John Doe', password='john123'")
        print("Customer 2: name='Jane Smith', password='jane123'")
        print("Customer 3: name='ABC Corporation', password='abc123'")
        return True

    except Exception as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


# ----------------------------
def main():
    try:
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("cbs.app.v2")
        except:
            pass

        app = QtWidgets.QApplication(sys.argv)
        app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        app.setStyle('Fusion')

        print("Enhanced Core Banking System Starting...")
        #print("Initializing database...")

        # Uncomment the next line if you need to reinitialize the database
        # initialize_database()

        login = LoginWindow()
        login.show()

        print("Login window displayed successfully")
        sys.exit(app.exec_())

    except Exception as e:
        print(f"Critical error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
