import tkinter as tk 
from tkinter import ttk, messagebox 
import finance_manager as fm

file_name = "expenses_gui.csv" 

# -------- Functions -------- 
def add_expense(): 
    date = entry_date.get() 
    category = entry_category.get() 
    amount = entry_amount.get() 
    desc = entry_desc.get() 
    trans_type = combo_type.get()

    if date == "" or category == "" or amount == "": 
        messagebox.showerror("Error", "Please fill all required fields") 
        return 

    if not fm.validate_date(date):
        messagebox.showerror("Error", "Please check date format (YYYY-MM-DD)")
        return
        
    if not fm.validate_amount(amount):
        messagebox.showerror("Error", "Amount must be a number greater than zero")
        return

    fm.save_transaction(file_name, date, category, amount, desc, trans_type)

    messagebox.showinfo("Success", f"{trans_type} Added") 

    clear_fields() 
    load_data() 


def load_data(): 
    for row in tree.get_children(): 
        tree.delete(row) 

    transactions = fm.load_all_transactions(file_name)
    for row in transactions: 
        tree.insert("", "end", values=row) 


def show_total(): 
    transactions = fm.load_all_transactions(file_name)
    total_income, total_expenses, balance = fm.calculate_totals(transactions)

    summary = (f"Total Income: ₹{total_income:,.2f}\n"
               f"Total Expenses: ₹{total_expenses:,.2f}\n"
               f"Balance: ₹{balance:,.2f}")
    messagebox.showinfo("Finance Summary", summary) 


def clear_fields(): 
    entry_date.delete(0, tk.END) 
    entry_category.delete(0, tk.END) 
    entry_amount.delete(0, tk.END) 
    entry_desc.delete(0, tk.END) 
    combo_type.set("Expense")


# -------- UI -------- 
root = tk.Tk() 
root.title("Expense Tracker") 
root.geometry("700x500") 

# Labels & Entries 
tk.Label(root, text="Date").grid(row=0, column=0, padx=10, pady=5) 
entry_date = tk.Entry(root) 
entry_date.grid(row=0, column=1) 

tk.Label(root, text="Category").grid(row=1, column=0, padx=10, pady=5) 
entry_category = tk.Entry(root) 
entry_category.grid(row=1, column=1) 

tk.Label(root, text="Amount (₹)").grid(row=2, column=0, padx=10, pady=5) 
entry_amount = tk.Entry(root) 
entry_amount.grid(row=2, column=1) 
tk.Label(root, text="Description").grid(row=3, column=0, padx=10, pady=5) 
entry_desc = tk.Entry(root) 
entry_desc.grid(row=3, column=1) 

tk.Label(root, text="Type").grid(row=4, column=0, padx=10, pady=5)
combo_type = ttk.Combobox(root, values=["Expense", "Income"], state="readonly")
combo_type.grid(row=4, column=1)
combo_type.set("Expense")

# Buttons 
tk.Button(root, text="Add Transaction", command=add_expense).grid(row=5, column=0, pady=10) 
tk.Button(root, text="Show Summary", command=show_total).grid(row=5, column=1) 
tk.Button(root, text="Refresh", command=load_data).grid(row=5, column=2) 

# Table 
tree_frame = tk.Frame(root)
tree_frame.grid(row=6, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

tree = ttk.Treeview(tree_frame, columns=fm.CSV_HEADER, show="headings") 

# Add scrollbar (Bug-06)
scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

for col in fm.CSV_HEADER:
    tree.heading(col, text=col)
    tree.column(col, width=100)

# Hide ID column
tree.column("ID", width=0, stretch=tk.NO)

tree.pack(side="left", fill="both", expand=True) 

# Configure grid to expand
root.grid_rowconfigure(6, weight=1)
root.grid_columnconfigure(0, weight=1)

fm.ensure_csv_exists(file_name)
load_data() 

if __name__ == "__main__":
    root.mainloop() 
