import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

# Configuration
FILE_NAME = "expenses.csv"
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
BG_COLOR = "#1e1e2e"  # Dark blue-ish background
FG_COLOR = "#cdd6f4"  # Light text
ACCENT_COLOR = "#89b4fa"  # Accent blue
SUCCESS_COLOR = "#a6e3a1"  # Success green
DANGER_COLOR = "#f38ba8"  # Danger red
ENTRY_BG = "#313244"  # Darker entry background

# Ensure CSV exists
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Category", "Amount", "Description"])

class ExpenseTrackerPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker Pro")
        self.root.geometry("850x600")
        self.root.configure(bg=BG_COLOR)

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure Treeview style
        self.style.configure("Treeview", 
                           background=ENTRY_BG, 
                           foreground=FG_COLOR, 
                           fieldbackground=ENTRY_BG,
                           rowheight=30)
        self.style.map("Treeview", background=[('selected', ACCENT_COLOR)])
        self.style.configure("Treeview.Heading", 
                           background="#45475a", 
                           foreground=FG_COLOR, 
                           relief="flat")

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Header / Dashboard
        header_frame = tk.Frame(self.root, bg=BG_COLOR, pady=20)
        header_frame.pack(fill="x")

        tk.Label(header_frame, text="💰 Expense Tracker Pro", font=("Helvetica", 24, "bold"), 
                 bg=BG_COLOR, fg=ACCENT_COLOR).pack()
        
        self.total_label = tk.Label(header_frame, text="Total Spending: ₹0.00", 
                 font=("Helvetica", 14), bg=BG_COLOR, fg=SUCCESS_COLOR)
        self.total_label.pack(pady=5)

        # Main Content Container
        main_container = tk.Frame(self.root, bg=BG_COLOR, padx=20)
        main_container.pack(fill="both", expand=True)

        # Input Form (Left Side)
        form_frame = tk.LabelFrame(main_container, text=" Add New Expense ", 
                                  bg=BG_COLOR, fg=FG_COLOR, font=("Helvetica", 10, "bold"),
                                  padx=15, pady=15)
        form_frame.pack(side="left", fill="y", padx=(0, 20))

        # Inputs
        tk.Label(form_frame, text="Date (YYYY-MM-DD)", bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.entry_date = tk.Entry(form_frame, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, border=0)
        self.entry_date.pack(fill="x", pady=(0, 10), ipady=5)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(form_frame, text="Category", bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.combo_category = ttk.Combobox(form_frame, values=CATEGORIES)
        self.combo_category.pack(fill="x", pady=(0, 10), ipady=3)
        self.combo_category.set(CATEGORIES[0])

        tk.Label(form_frame, text="Amount (₹)", bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.entry_amount = tk.Entry(form_frame, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, border=0)
        self.entry_amount.pack(fill="x", pady=(0, 10), ipady=5)

        tk.Label(form_frame, text="Description", bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.entry_desc = tk.Entry(form_frame, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, border=0)
        self.entry_desc.pack(fill="x", pady=(0, 20), ipady=5)

        # Buttons
        add_btn = tk.Button(form_frame, text="Add Expense", command=self.add_expense,
                          bg=ACCENT_COLOR, fg=BG_COLOR, font=("Helvetica", 10, "bold"),
                          relief="flat", cursor="hand2")
        add_btn.pack(fill="x", pady=5)

        clear_btn = tk.Button(form_frame, text="Clear Fields", command=self.clear_fields,
                            bg="#45475a", fg=FG_COLOR, relief="flat", cursor="hand2")
        clear_btn.pack(fill="x", pady=5)

        # Data View (Right Side)
        view_frame = tk.Frame(main_container, bg=BG_COLOR)
        view_frame.pack(side="right", fill="both", expand=True)

        # Treeview for Table
        columns = ("Date", "Category", "Amount", "Description")
        self.tree = ttk.Treeview(view_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill="both", expand=True)

        # Bottom Actions
        actions_frame = tk.Frame(view_frame, bg=BG_COLOR, pady=10)
        actions_frame.pack(fill="x")

        delete_btn = tk.Button(actions_frame, text="Delete Selected", command=self.delete_expense,
                             bg=DANGER_COLOR, fg=BG_COLOR, font=("Helvetica", 9, "bold"),
                             relief="flat", cursor="hand2")
        delete_btn.pack(side="left")

        refresh_btn = tk.Button(actions_frame, text="Refresh", command=self.load_data,
                              bg="#45475a", fg=FG_COLOR, relief="flat", cursor="hand2")
        refresh_btn.pack(side="right")

    def add_expense(self):
        date = self.entry_date.get()
        category = self.combo_category.get()
        amount = self.entry_amount.get()
        desc = self.entry_desc.get()

        if not all([date, category, amount]):
            messagebox.showwarning("Incomplete Data", "Date, Category and Amount are required.")
            return

        try:
            # Basic date validation
            datetime.strptime(date, "%Y-%m-%d")
            float_amount = float(amount)
        except ValueError as e:
            messagebox.showerror("Invalid Input", "Please check date format (YYYY-MM-DD) and amount (number).")
            return

        with open(FILE_NAME, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([date, category, float_amount, desc])

        self.load_data()
        self.clear_fields()
        # Keep the date for convenience
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select an item to delete.")
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            return

        item_values = self.tree.item(selected_item)['values']
        # Convert to strings for comparison (as they come from CSV)
        item_values = [str(v) for v in item_values]

        all_expenses = []
        with open(FILE_NAME, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                # Basic check to skip the row we want to delete
                if row != item_values:
                    all_expenses.append(row)

        with open(FILE_NAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(all_expenses)

        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        total = 0
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r") as f:
                reader = csv.reader(f)
                try:
                    next(reader)
                    for row in reader:
                        self.tree.insert("", "end", values=row)
                        try:
                            total += float(row[2])
                        except (ValueError, IndexError):
                            continue
                except StopIteration:
                    pass
        
        self.total_label.config(text=f"Total Spending: ₹{total:,.2f}")

    def clear_fields(self):
        self.entry_date.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.combo_category.set(CATEGORIES[0])

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerPro(root)
    root.mainloop()
