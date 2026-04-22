import tkinter as tk 
from tkinter import ttk, messagebox 
import csv 
import os 

file_name = "expenses.csv" 

# Create file if not exists 
if not os.path.exists(file_name): 
    with open(file_name, "w", newline="") as f: 
        writer = csv.writer(f) 
        writer.writerow(["Date", "Category", "Amount", "Description"]) 


# -------- Functions -------- 
def add_expense(): 
    date = entry_date.get() 
    category = entry_category.get() 
    amount = entry_amount.get() 
    desc = entry_desc.get() 

    if date == "" or category == "" or amount == "": 
        messagebox.showerror("Error", "Please fill all required fields") 
        return 

    try:
        float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number")
        return

    with open(file_name, "a", newline="") as f: 
        writer = csv.writer(f) 
        writer.writerow([date, category, amount, desc]) 

    messagebox.showinfo("Success", "Expense Added") 

    clear_fields() 
    load_data() 


def load_data(): 
    for row in tree.get_children(): 
        tree.delete(row) 

    if not os.path.exists(file_name):
        return

    with open(file_name, "r") as f: 
        reader = csv.reader(f) 
        try:
            next(reader) 
        except StopIteration:
            return

        for row in reader: 
            tree.insert("", "end", values=row) 


def show_total(): 
    total = 0 
    if not os.path.exists(file_name):
        messagebox.showinfo("Total Expense", "Total: ₹0")
        return

    with open(file_name, "r") as f: 
        reader = csv.reader(f) 
        try:
            next(reader) 
        except StopIteration:
            messagebox.showinfo("Total Expense", "Total: ₹0")
            return

        for row in reader: 
            try:
                total += float(row[2]) 
            except (ValueError, IndexError):
                continue

    messagebox.showinfo("Total Expense", "Total: ₹" + str(total)) 


def clear_fields(): 
    entry_date.delete(0, tk.END) 
    entry_category.delete(0, tk.END) 
    entry_amount.delete(0, tk.END) 
    entry_desc.delete(0, tk.END) 


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

# Buttons 
tk.Button(root, text="Add Expense", command=add_expense).grid(row=4, column=0, pady=10) 
tk.Button(root, text="Show Total", command=show_total).grid(row=4, column=1) 
tk.Button(root, text="Refresh", command=load_data).grid(row=4, column=2) 

# Table 
tree = ttk.Treeview(root, columns=("Date", "Category", "Amount", "Description"), show="headings") 

tree.heading("Date", text="Date") 
tree.heading("Category", text="Category") 
tree.heading("Amount", text="Amount") 
tree.heading("Description", text="Description") 

tree.grid(row=5, column=0, columnspan=4, padx=10, pady=10) 

# Load data initially 
load_data() 

if __name__ == "__main__":
    root.mainloop() 
