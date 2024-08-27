from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QInputDialog, QMessageBox, QDialog, QFormLayout, QDateEdit, 
                             QLabel, QDialogButtonBox, QTableView, QAbstractItemView)
from PyQt5.QtCore import QDate, Qt, QAbstractTableModel
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import sys
import os

class CSV:
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    CSV_FILE = os.path.join(BASE_DIR, "finance_data.csv")
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description
        }
        df = pd.read_csv(cls.CSV_FILE)
        new_df = pd.DataFrame([new_entry], columns=cls.COLUMNS)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(cls.CSV_FILE, index=False)
        QMessageBox.information(None, "Success", "Entry added successfully")


    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)
        start_date = datetime.strptime(start_date, CSV.FORMAT)
        end_date = datetime.strptime(end_date, CSV.FORMAT)
        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            QMessageBox.information(None, "Info", "No transactions found in the given date range")
        else:
            total_income = filtered_df[filtered_df["category"] == "Income"]["amount"].sum()
            total_expense = filtered_df[filtered_df["category"] == "Expense"]["amount"].sum()
            net_savings = total_income - total_expense
            summary = (
                f"Total Income: ${total_income:.2f}\n"
                f"Total Expense: ${total_expense:.2f}\n"
                f"Net Savings: ${net_savings:.2f}"
            )
            QMessageBox.information(None, "Summary", summary)

        return filtered_df

    @classmethod
    def get_all_transactions(cls):
        df = pd.read_csv(cls.CSV_FILE)
        return df

def plot_transactions(df):
    # Convert 'date' column to datetime format
    df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)
    df.set_index("date", inplace=True)
    
    # Resample data by day and sum up the income and expenses
    income_df = (
        df[df["category"] == "Income"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )
    expense_df = (
        df[df["category"] == "Expense"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )
    
    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
    plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income and Expenses Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()

class TransactionTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data.columns)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            else:
                return str(section + 1)
        return None

class DatePickerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pick a Date")

        layout = QFormLayout(self)
        self.date_edit = QDateEdit(self)
        self.date_edit.setDate(QDate.currentDate())
        layout.addRow(QLabel("Select Date:"), self.date_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_date(self):
        return self.date_edit.date().toString('dd-MM-yyyy')

class TransactionDialog(QDialog):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("All Transactions")
        self.setGeometry(100, 100, 800, 600)

        # Create a table view and set the model
        model = TransactionTableModel(data)
        table_view = QTableView()
        table_view.setModel(model)
        table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set layout and add table view to dialog
        layout = QVBoxLayout(self)
        layout.addWidget(table_view)
        self.setLayout(layout)

class FinanceTracker(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Finance Tracker')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.add_button = QPushButton('Add Transaction')
        self.add_button.clicked.connect(self.add_transaction)
        self.layout.addWidget(self.add_button)

        self.view_button = QPushButton('View Transactions')
        self.view_button.clicked.connect(self.view_transactions)
        self.layout.addWidget(self.view_button)

        self.view_all_button = QPushButton('View All Transactions')
        self.view_all_button.clicked.connect(self.view_all_transactions)
        self.layout.addWidget(self.view_all_button)

        self.exit_button = QPushButton('Exit')
        self.exit_button.clicked.connect(self.close)
        self.layout.addWidget(self.exit_button)

    def add_transaction(self):
        date = self.get_date()
        if date is None:
            return

        amount = self.get_amount()
        if amount is None:
            return

        category = self.get_category()
        if category is None:
            return

        description = self.get_description()
        if description is None:
            return

        CSV.add_entry(date, amount, category, description)

    def view_transactions(self):
        start_date = self.get_date('Start Date')
        if start_date is None:
            return

        end_date = self.get_date('End Date')
        if end_date is None:
            return

        df = CSV.get_transactions(start_date, end_date)

        if not df.empty:
            reply = QMessageBox.question(self, 'Plot', 'Do you want to see a plot of the transactions?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                plot_transactions(df)

    def view_all_transactions(self):
        df = CSV.get_all_transactions()
        if df.empty:
            QMessageBox.information(self, "Info", "No transactions found")
            return

        dialog = TransactionDialog(df)
        dialog.exec_()  # This will open the dialog and block until it is closed

    def get_date(self, title='Date'):
        dialog = DatePickerDialog()
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_date()
        return None

    def get_amount(self):
        amount, ok = QInputDialog.getDouble(self, 'Enter Amount', 'Enter the amount:')
        if ok:
            return amount
        return None

    def get_category(self):
        items = ['Income', 'Expense']
        category, ok = QInputDialog.getItem(self, 'Enter Category', 'Enter the category (Income/Expense):', items)
        if ok:
            return category
        return None

    def get_description(self):
        description, ok = QInputDialog.getText(self, 'Enter Description', 'Enter the description:')
        if ok:
            return description
        return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FinanceTracker()
    window.show()
    sys.exit(app.exec_())
