import pandas as pd
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog


class CSV:
    CSV_FILE = "finance_data.csv"
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
        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        messagebox.showinfo("Success", "Entry added successfully")
        
    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)
        start_date = datetime.strptime(start_date, CSV.FORMAT)
        end_date = datetime.strptime(end_date, CSV.FORMAT)
        
        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]
        
        if filtered_df.empty:
            messagebox.showinfo("Info", "No transactions found in the given date range")
        else:
            total_income = filtered_df[filtered_df["category"] == "Income"]["amount"].sum()
            total_expense = filtered_df[filtered_df["category"] == "Expense"]["amount"].sum()
            net_savings = total_income - total_expense

            summary = (
                f"Total Income: ${total_income:.2f}\n"
                f"Total Expense: ${total_expense:.2f}\n"
                f"Net Savings: ${net_savings:.2f}"
            )
            messagebox.showinfo("Summary", summary)
        
        return filtered_df

def plot_transactions(df):
    df.set_index('date', inplace=True)
    
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
    
    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
    plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title('Income and Expenses Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

def add_transaction():
    CSV.initialize_csv()
    date = simpledialog.askstring("Input", "Enter the date of the transaction (dd-mm-yyyy): or leave blank for today's date")
    if not date:
        date = datetime.today().strftime(CSV.FORMAT)
    amount = simpledialog.askfloat("Input", "Enter the amount:")
    category = simpledialog.askstring("Input", "Enter the category (Income/Expense):")
    description = simpledialog.askstring("Input", "Enter the description:")
    
    CSV.add_entry(date, amount, category, description)

def view_transactions():
    start_date = simpledialog.askstring("Input", "Enter the start date (dd-mm-yyyy):")
    end_date = simpledialog.askstring("Input", "Enter the end date (dd-mm-yyyy):")
    df = CSV.get_transactions(start_date, end_date)
    
    if not df.empty:
        if messagebox.askyesno("Plot", "Do you want to see a plot of the transactions?"):
            plot_transactions(df)

def main():
    root = tk.Tk()
    root.title("Finance Tracker")
    
    frame = tk.Frame(root)
    frame.pack(pady=20)
    
    add_button = tk.Button(frame, text="Add Transaction", command=add_transaction)
    add_button.pack(side="left", padx=10)
    
    view_button = tk.Button(frame, text="View Transactions", command=view_transactions)
    view_button.pack(side="left", padx=10)
    
    exit_button = tk.Button(frame, text="Exit", command=root.quit)
    exit_button.pack(side="left", padx=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()
