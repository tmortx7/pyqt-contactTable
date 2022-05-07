import sys
from stylesheet import styles
from PyQt5.QtWidgets import (QApplication, QFormLayout, QHBoxLayout,
                             QHeaderView, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QDialogButtonBox, QPushButton,
                             QVBoxLayout, QWidget, QTableView, QDialog,
                             QAbstractItemView)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtCore import Qt, QSortFilterProxyModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.createConnection()  # create database connection

        self.setWindowTitle("Control Systems")
        self.setMinimumSize(500, 500)

        centralWidget = QWidget()

        # =========== LAYOUT SETUP FOR UI ============
        self.overall_layout = QVBoxLayout()
        self.overall_layout.setSpacing(10)

        self.title = QLabel("Contact Book")
        self.title.setObjectName("AppTitle")

        self.search_pane = QHBoxLayout()  # search feature layout

        self.table_view = QTableView()  # table view
        self.table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.action_btn_pane = QVBoxLayout()  # db manipulation features layout
        self.action_btn_pane.setAlignment(Qt.AlignTop)

        self.table_and_manipulate_actions_layout = QHBoxLayout()
        self.table_and_manipulate_actions_layout.addWidget(self.table_view)
        self.table_and_manipulate_actions_layout.addLayout(
            self.action_btn_pane)

        self.overall_layout.addWidget(self.title)
        self.overall_layout.addLayout(self.search_pane)
        self.overall_layout.addLayout(
            self.table_and_manipulate_actions_layout
        )

        self.initializeUI()  # Create the UI

        centralWidget.setLayout(self.overall_layout)
        self.setCentralWidget(centralWidget)

        self.show()

    def createConnection(self):
        database = QSqlDatabase.addDatabase('QSQLITE')
        database.setDatabaseName("db/contacts.sql")

        if not database.open():
            print("Unable to create datbase ojbect")
            print("Connection failed:", database.lastError().text())
            sys.exit()

        self.query = QSqlQuery()
        # self.query.exec_("DROP TABLE IF EXISTS users")

        self.query.exec_("""CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL,
            phone_number INTEGER NOT NULL
        )""")

    def initializeUI(self):
        # ========= SETUP FOR TABLE VIEW ==========
        self.model = QSqlTableModel()
        self.model.setTable("users")
        self.model.select()
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)

        self.table_view.setModel(self.model)
        self.table_view.hideColumn(0)

        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.model)
        self.filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filter_proxy_model.setFilterKeyColumn(1)
        self.table_view.setModel(self.filter_proxy_model)

        # =========== SETUP FOR FEATURES  ==============
        search_input = QLineEdit()
        search_input.textChanged.connect(
            self.filter_proxy_model.setFilterRegExp)
        search_input.setObjectName("SearchInputBox")
        self.search_pane.addWidget(search_input)

        self.button_new_contact = QPushButton("Create New Contact")
        self.button_new_contact.setObjectName("ButtonCreateNewContact")
        self.button_new_contact.clicked.connect(self.createNewContactDialog)

        self.button_delete_contact = QPushButton("Delete Contact(s)")
        self.button_delete_contact.clicked.connect(self.deleteSelectedContact)

        self.action_btn_pane.addWidget(self.button_new_contact)
        self.action_btn_pane.addWidget(self.button_delete_contact)

    def createNewContactDialog(self):
        self.new_contact_dialog = QDialog(self)
        self.new_contact_dialog.setObjectName("CreateNewContactDialog")
        self.new_contact_dialog.setWindowTitle("Create New Contact")
        self.new_contact_dialog.setModal(True)
        self.new_contact_dialog.setMinimumSize(250, 100)
        self.new_contact_dialog.show()

        new_contact_username = QLineEdit()
        new_contact_number = QLineEdit()

        dialog_ovr_layout = QFormLayout(self.new_contact_dialog)
        dialog_ovr_layout.addRow("USERNAME:", new_contact_username)
        dialog_ovr_layout.addRow("PHONE NUMBER:", new_contact_number)

        buttons_box = QDialogButtonBox(self)
        buttons_box.setOrientation(Qt.Horizontal)
        buttons_box.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok
        )
        buttons_box.accepted.connect(lambda cu=new_contact_username,
                                     cn=new_contact_number:
                                     self.addNewContact(cu, cn))
        buttons_box.rejected.connect(self.new_contact_dialog.reject)
        dialog_ovr_layout.addWidget(buttons_box)

    def addNewContact(self, username, number):
        try:
            username, number = username.text().strip(),\
                int(number.text().strip())
            if username == '' or number == '':
                QMessageBox.warning(self.new_contact_dialog, 'Warning',
                                    "Please input valid username!")
                return
            if len(str(number)) < 9:
                QMessageBox.warning(self.new_contact_dialog, 'Warning - Min 9',
                                    "The phone number is too short!")
                return

            self.query.exec_(f"INSERT INTO users (username, phone_number)\
                VALUES ('{username}', {number})")
            self.table_view.setModel(self.model)
            self.model.select()
            self.table_view.setModel(self.filter_proxy_model)
        except ValueError:
            # Error handles non-integer error in number field
            QMessageBox.warning(self.new_contact_dialog, 'Error',
                                "Invalid Phone number")

    def deleteSelectedContact(self):
        try:
            rows = self.table_view.selectionModel().selectedRows()
            if not rows:
                return
            messageBox = QMessageBox.warning(
                self,
                "Warning!",
                "Do you want to remove the selected contact(s)?",
                QMessageBox.Ok | QMessageBox.Cancel,
            )
            if messageBox == QMessageBox.Ok:
                for item in rows:
                    self.model.removeRow(item.row())
                self.model.select()
        except Exception as e:
            raise e


app = QApplication([])
app.setStyle('Fusion')
window = MainWindow()
window.setStyleSheet(styles)
app.exec_()
