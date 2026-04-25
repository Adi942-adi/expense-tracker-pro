import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
from tkinter import filedialog
import finance_manager as fm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configuration
FILE_NAME = "expenses_pro.csv"
BG_COLOR = "#1e1e2e"  # Dark blue-ish background
FG_COLOR = "#cdd6f4"  # Light text
ACCENT_COLOR = "#89b4fa"  # Accent blue
SUCCESS_COLOR = "#a6e3a1"  # Success green
DANGER_COLOR = "#f38ba8"  # Danger red
ENTRY_BG = "#313244"  # Darker entry background

class ExpenseTrackerPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker Pro")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG_COLOR)

        self.editing_id = None # Track if we are editing an existing transaction

        # Ensure CSV exists
        fm.ensure_csv_exists(FILE_NAME)

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
        
        # Process recurring transactions on startup
        added = fm.process_recurring(FILE_NAME)
        if added > 0:
            messagebox.showinfo("Recurring Transactions", f"Added {added} recurring transactions for this month.")
            
        self.load_data()

    def setup_ui(self):
        # Header / Dashboard
        header_frame = tk.Frame(self.root, bg=BG_COLOR, pady=10)
        header_frame.pack(fill="x")

        tk.Label(header_frame, text="💰 Personal Finance Tracker", font=("Helvetica", 20, "bold"), 
                 bg=BG_COLOR, fg=ACCENT_COLOR).pack()
        
        stats_frame = tk.Frame(header_frame, bg=BG_COLOR)
        stats_frame.pack(pady=5)

        self.income_label = tk.Label(stats_frame, text="Total Income: ₹0.00", 
                 font=("Helvetica", 11), bg=BG_COLOR, fg=SUCCESS_COLOR)
        self.income_label.pack(side="left", padx=15)

        self.expense_label = tk.Label(stats_frame, text="Total Expenses: ₹0.00", 
                 font=("Helvetica", 11), bg=BG_COLOR, fg=DANGER_COLOR)
        self.expense_label.pack(side="left", padx=15)

        self.balance_label = tk.Label(stats_frame, text="Balance: ₹0.00", 
                 font=("Helvetica", 11, "bold"), bg=BG_COLOR, fg=FG_COLOR)
        self.balance_label.pack(side="left", padx=15)

        # Search & Filter Bar
        filter_frame = tk.Frame(self.root, bg="#313244", padx=10, pady=5)
        filter_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(filter_frame, text="🔍 Search:", bg="#313244", fg=FG_COLOR).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_data())
        self.search_entry = tk.Entry(filter_frame, textvariable=self.search_var, bg=ENTRY_BG, fg=FG_COLOR, border=0)
        self.search_entry.pack(side="left", padx=5, ipady=3)

        tk.Label(filter_frame, text="Category:", bg="#313244", fg=FG_COLOR).pack(side="left", padx=5)
        self.filter_cat = ttk.Combobox(filter_frame, values=["All"] + fm.CATEGORIES, state="readonly", width=12)
        self.filter_cat.set("All")
        self.filter_cat.pack(side="left", padx=5)
        self.filter_cat.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        tk.Label(filter_frame, text="Type:", bg="#313244", fg=FG_COLOR).pack(side="left", padx=5)
        self.filter_type = ttk.Combobox(filter_frame, values=["All", "Expense", "Income"], state="readonly", width=10)
        self.filter_type.set("All")
        self.filter_type.pack(side="left", padx=5)
        self.filter_type.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        self.chart_btn = tk.Button(filter_frame, text="📊 View Charts", command=self.show_charts,
                                bg=ACCENT_COLOR, fg=BG_COLOR, relief="flat", padx=10)
        self.chart_btn.pack(side="right", padx=5)

        self.budget_btn = tk.Button(filter_frame, text="🎯 Manage Budgets", command=self.manage_budgets,
                                 bg="#f9e2af", fg=BG_COLOR, relief="flat", padx=10)
        self.budget_btn.pack(side="right", padx=5)

        self.summary_btn = tk.Button(filter_frame, text="📅 Summary View", command=self.show_summary,
                                  bg="#94e2d5", fg=BG_COLOR, relief="flat", padx=10)
        self.summary_btn.pack(side="right", padx=5)

        # Main Content Container
        main_container = tk.Frame(self.root, bg=BG_COLOR, padx=20)
        main_container.pack(fill="both", expand=True)

        # Input Form (Left Side)
        self.form_frame = tk.LabelFrame(main_container, text=" Add New Transaction ", 
                                  bg=BG_COLOR, fg=FG_COLOR, font=("Helvetica", 10, "bold"),
                                  padx=15, pady=15)
        self.form_frame.pack(side="left", fill="y", padx=(0, 20))

        # Inputs
        tk.Label(self.form_frame, text="Date (YYYY-MM-DD)", bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.entry_date = tk.Entry(self.form_frame, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, border=0)
        self.entry_date.pack(fill="x", pady=(0, 10), ipady=5)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(self.form_frame, text="Category", bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.combo_category = ttk.Combobox(self.form_frame, values=fm.CATEGORIES, state="readonly")
        self.combo_category.pack(fill="x", pady=(0, 10), ipady=3)
        self.combo_category.set(fm.CATEGORIES[0])

        tk.Label(self.form_frame, text="Type", bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.combo_type = ttk.Combobox(self.form_frame, values=["Expense", "Income"], state="readonly")
        self.combo_type.pack(fill="x", pady=(0, 10), ipady=3)
        self.combo_type.set("Expense")
        self.combo_type.bind("<<ComboboxSelected>>", self.on_type_change)

        tk.Label(self.form_frame, text="Amount (₹)", bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.entry_amount = tk.Entry(self.form_frame, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, border=0)
        self.entry_amount.pack(fill="x", pady=(0, 10), ipady=5)

        tk.Label(self.form_frame, text="Description", bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.entry_desc = tk.Entry(self.form_frame, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, border=0)
        self.entry_desc.pack(fill="x", pady=(0, 10), ipady=5)

        self.is_recurring = tk.BooleanVar()
        self.check_recurring = tk.Checkbutton(self.form_frame, text="Recurring Monthly", 
                                            variable=self.is_recurring, bg=BG_COLOR, fg=FG_COLOR,
                                            selectcolor=ENTRY_BG, activebackground=BG_COLOR, activeforeground=FG_COLOR)
        self.check_recurring.pack(anchor="w", pady=(0, 10))

        # Buttons
        self.add_btn = tk.Button(self.form_frame, text="Add Transaction", command=self.save_transaction,
                          bg=ACCENT_COLOR, fg=BG_COLOR, font=("Helvetica", 10, "bold"),
                          relief="flat", cursor="hand2")
        self.add_btn.pack(fill="x", pady=5)

        self.cancel_btn = tk.Button(self.form_frame, text="Cancel Edit", command=self.clear_fields,
                            bg="#45475a", fg=FG_COLOR, relief="flat", cursor="hand2")
        # Hidden by default
        
        clear_btn = tk.Button(self.form_frame, text="Clear Fields", command=self.clear_fields,
                            bg="#45475a", fg=FG_COLOR, relief="flat", cursor="hand2")
        clear_btn.pack(fill="x", pady=5)

        # Data View (Right Side)
        view_frame = tk.Frame(main_container, bg=BG_COLOR)
        view_frame.pack(side="right", fill="both", expand=True)

        # Treeview for Table
        self.tree = ttk.Treeview(view_frame, columns=fm.CSV_HEADER, show="headings")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(view_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        for col in fm.CSV_HEADER:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=100)
        
        # Hide ID column but keep it in data
        self.tree.column("ID", width=0, stretch=tk.NO)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)

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

        export_excel_btn = tk.Button(actions_frame, text="📗 Export Excel", command=self.export_excel,
                                  bg="#2ecc71", fg=BG_COLOR, font=("Helvetica", 9),
                                  relief="flat", cursor="hand2")
        export_excel_btn.pack(side="right", padx=10)

        export_pdf_btn = tk.Button(actions_frame, text="📕 Export PDF", command=self.export_pdf,
                                bg="#e74c3c", fg=FG_COLOR, font=("Helvetica", 9),
                                relief="flat", cursor="hand2")
        export_pdf_btn.pack(side="right", padx=5)

    def sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        
        # Try to sort numerically if it's the Amount column
        if col == "Amount":
            try:
                l.sort(key=lambda t: float(t[0]), reverse=reverse)
            except ValueError:
                l.sort(reverse=reverse)
        else:
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def on_double_click(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        values = self.tree.item(selected_item)['values']
        # ID, Date, Category, Amount, Description, Type
        self.editing_id = str(values[0])
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, values[1])
        self.combo_category.set(values[2])
        self.entry_amount.delete(0, tk.END)
        self.entry_amount.insert(0, values[3])
        self.entry_desc.delete(0, tk.END)
        self.entry_desc.insert(0, values[4])
        self.combo_type.set(values[5])
        
        self.on_type_change(None)
        self.add_btn.config(text=f"Update {values[5]}", bg=SUCCESS_COLOR)
        self.cancel_btn.pack(fill="x", pady=5, after=self.add_btn)
        self.check_recurring.pack_forget()

    def save_transaction(self):
        date = self.entry_date.get()
        category = self.combo_category.get()
        amount = self.entry_amount.get()
        desc = self.entry_desc.get()
        trans_type = self.combo_type.get()

        if not all([date, category, amount, trans_type]):
            messagebox.showwarning("Incomplete Data", "Date, Category, Amount and Type are required.")
            return

        if not fm.validate_date(date):
            messagebox.showerror("Invalid Input", "Please check date format (YYYY-MM-DD).")
            return
        
        if not fm.validate_amount(amount):
            messagebox.showerror("Invalid Input", "Amount must be a number greater than zero.")
            return

        # Budget Check
        if trans_type == "Expense":
            all_transactions = fm.load_all_transactions(FILE_NAME)
            warning = fm.check_budget_warning(category, amount, all_transactions)
            if warning:
                if "exceed" in warning:
                    if not messagebox.askyesno("Budget Exceeded", f"{warning}\n\nDo you still want to add this transaction?"):
                        return
                else:
                    messagebox.showinfo("Budget Note", warning)

        if self.editing_id:
            if fm.update_transaction(FILE_NAME, self.editing_id, date, category, amount, desc, trans_type):
                messagebox.showinfo("Success", "Transaction updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update transaction.")
        else:
            fm.save_transaction(FILE_NAME, date, category, amount, desc, trans_type)
            if self.is_recurring.get():
                day = datetime.strptime(date, "%Y-%m-%d").day
                fm.add_recurring_transaction(category, amount, desc, trans_type, day)
                messagebox.showinfo("Recurring", "Recurring transaction template saved!")

        self.load_data()
        self.clear_fields()
        # Set today's date as default
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select an item to delete.")
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?"):
            return

        item_values = self.tree.item(selected_item)['values']
        item_id = str(item_values[0]) # ID is the first column

        if fm.delete_transaction_by_id(FILE_NAME, item_id):
            self.load_data()
            self.clear_fields() # BUG-07: Always clear fields after deletion
        else:
            messagebox.showerror("Error", "Could not delete transaction.")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        all_transactions = fm.load_all_transactions(FILE_NAME)
        
        # Apply Filters
        query = self.search_var.get()
        cat = self.filter_cat.get()
        t_type = self.filter_type.get()
        
        filtered_transactions = fm.filter_transactions(all_transactions, query, cat, t_type)
        
        for row in filtered_transactions:
            self.tree.insert("", "end", values=row)
            
        # Stats are always based on ALL data or filtered data? 
        # Usually, stats should reflect what's on screen if filtering, or total. 
        # Let's show totals for ALL transactions for the dashboard.
        total_income, total_expenses, balance = fm.calculate_totals(all_transactions)
        
        self.income_label.config(text=f"Total Income: ₹{total_income:,.2f}")
        self.expense_label.config(text=f"Total Expenses: ₹{total_expenses:,.2f}")
        self.balance_label.config(text=f"Balance: ₹{balance:,.2f}")
        
        if balance >= 0:
            self.balance_label.config(fg=SUCCESS_COLOR)
        else:
            self.balance_label.config(fg=DANGER_COLOR)

    def show_charts(self):
        all_transactions = fm.load_all_transactions(FILE_NAME)
        if not all_transactions:
            messagebox.showwarning("No Data", "Add some transactions first to see charts.")
            return

        # Prepare data for pie chart (Expenses by Category)
        expense_cats = {}
        total_income = 0
        total_expenses = 0
        
        for row in all_transactions:
            amount = float(row[3])
            t_type = row[5]
            cat = row[2]
            if t_type == "Expense":
                expense_cats[cat] = expense_cats.get(cat, 0) + amount
                total_expenses += amount
            else:
                total_income += amount

        # Create Chart Window
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Financial Analysis")
        chart_window.geometry("800x600")
        chart_window.configure(bg=BG_COLOR)

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
        fig.patch.set_facecolor(BG_COLOR)

        # Pie Chart (Expenses by Category)
        if expense_cats:
            labels = list(expense_cats.keys())
            sizes = list(expense_cats.values())
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
                   textprops={'color': FG_COLOR})
            ax1.set_title("Expenses by Category", color=FG_COLOR, pad=20)
        else:
            ax1.text(0.5, 0.5, "No Expenses", color=FG_COLOR, ha='center')

        # Bar Chart (Income vs Expenses)
        ax2.bar(["Income", "Expenses"], [total_income, total_expenses], color=[SUCCESS_COLOR, DANGER_COLOR])
        ax2.set_title("Income vs Expenses", color=FG_COLOR, pad=20)
        ax2.tick_params(colors=FG_COLOR)
        for i, v in enumerate([total_income, total_expenses]):
            ax2.text(i, v + (v * 0.05), f"₹{v:,.0f}", color=FG_COLOR, ha='center')

        # Line Chart (Balance over time)
        # Sort transactions by date
        sorted_trans = sorted(all_transactions, key=lambda x: x[1])
        dates = []
        balances = []
        current_balance = 0
        
        for row in sorted_trans:
            date = row[1]
            amount = float(row[3])
            t_type = row[5]
            if t_type == "Income":
                current_balance += amount
            else:
                current_balance -= amount
            
            if not dates or dates[-1] != date:
                dates.append(date)
                balances.append(current_balance)
            else:
                balances[-1] = current_balance # Update balance for the same day
        
        if dates:
            ax3.plot(dates, balances, marker='o', color=ACCENT_COLOR, linewidth=2)
            ax3.set_title("Balance Trend", color=FG_COLOR, pad=20)
            ax3.tick_params(colors=FG_COLOR, rotation=45)
            ax3.fill_between(dates, balances, alpha=0.2, color=ACCENT_COLOR)
            ax3.grid(True, linestyle='--', alpha=0.3, color=FG_COLOR)
        else:
            ax3.text(0.5, 0.5, "No Data for Trend", color=FG_COLOR, ha='center')

        plt.tight_layout()
        
        # BUG-06: Bind window close to plt.close(fig) to prevent memory leak
        chart_window.protocol("WM_DELETE_WINDOW", lambda: (plt.close(fig), chart_window.destroy()))
        
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def manage_budgets(self):
        budget_window = tk.Toplevel(self.root)
        budget_window.title("Manage Monthly Budgets")
        budget_window.geometry("400x500")
        budget_window.configure(bg=BG_COLOR)

        tk.Label(budget_window, text="Set Monthly Category Budgets", font=("Helvetica", 14, "bold"),
                 bg=BG_COLOR, fg=ACCENT_COLOR, pady=15).pack()

        budgets = fm.load_budgets()
        entries = {}

        scroll_frame = tk.Frame(budget_window, bg=BG_COLOR)
        scroll_frame.pack(fill="both", expand=True, padx=20)

        for cat in fm.CATEGORIES:
            row = tk.Frame(scroll_frame, bg=BG_COLOR, pady=5)
            row.pack(fill="x")
            
            tk.Label(row, text=cat, bg=BG_COLOR, fg=FG_COLOR, width=15, anchor="w").pack(side="left")
            
            ent = tk.Entry(row, bg=ENTRY_BG, fg=FG_COLOR, border=0, width=15)
            ent.insert(0, f"{budgets.get(cat, 0):.2f}")
            ent.pack(side="right", ipady=3)
            entries[cat] = ent

        def save_all_budgets():
            try:
                for cat, ent in entries.items():
                    val = ent.get()
                    # Allow "0", "0.0", etc. but reject non-numeric or negative
                    if val != "0" and not fm.validate_amount(val):
                        try:
                            if float(val) != 0:
                                raise ValueError
                        except ValueError:
                            raise ValueError(f"Invalid amount for {cat}")
                    fm.save_budget(cat, val)
                messagebox.showinfo("Success", "Budgets updated successfully!")
                budget_window.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        tk.Button(budget_window, text="Save Budgets", command=save_all_budgets,
                  bg=SUCCESS_COLOR, fg=BG_COLOR, font=("Helvetica", 10, "bold"),
                  relief="flat", pady=10).pack(fill="x", padx=20, pady=20)

    def export_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                               filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if file_path:
            try:
                fm.export_to_excel(FILE_NAME, file_path)
                messagebox.showinfo("Export Successful", f"Data exported to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def export_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                               filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if file_path:
            try:
                fm.export_to_pdf(FILE_NAME, file_path)
                messagebox.showinfo("Export Successful", f"Data exported to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def show_summary(self):
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Financial Summary")
        summary_window.geometry("500x400")
        summary_window.configure(bg=BG_COLOR)

        tk.Label(summary_window, text="Periodic Financial Summary", font=("Helvetica", 14, "bold"),
                 bg=BG_COLOR, fg=ACCENT_COLOR, pady=15).pack()

        # Period Selector
        period_var = tk.StringVar(value="Monthly")
        selector_frame = tk.Frame(summary_window, bg=BG_COLOR)
        selector_frame.pack(pady=5)
        
        tk.Radiobutton(selector_frame, text="Monthly", variable=period_var, value="Monthly",
                      bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR, command=lambda: refresh_summary()).pack(side="left", padx=10)
        tk.Radiobutton(selector_frame, text="Weekly", variable=period_var, value="Weekly",
                      bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR, command=lambda: refresh_summary()).pack(side="left", padx=10)

        # Summary Table
        table_frame = tk.Frame(summary_window, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("Period", "Income", "Expenses", "Net")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        tree.pack(fill="both", expand=True)

        def refresh_summary():
            for row in tree.get_children():
                tree.delete(row)
            
            period = period_var.get()
            summary_data = fm.get_period_summary(FILE_NAME, period)
            
            for period_label, values in summary_data.items():
                income, expense = values
                net = income - expense
                tree.insert("", "end", values=(period_label, f"₹{income:,.2f}", f"₹{expense:,.2f}", f"₹{net:,.2f}"))

        refresh_summary()

    def clear_fields(self):
        self.editing_id = None
        self.entry_date.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.combo_category.set(fm.CATEGORIES[0])
        self.combo_type.set("Expense")
        self.is_recurring.set(False)
        self.on_type_change(None)
        self.add_btn.config(text="Add Transaction", bg=ACCENT_COLOR)
        self.cancel_btn.pack_forget()
        self.check_recurring.pack(anchor="w", pady=(0, 10), before=self.add_btn)

    def on_type_change(self, event):
        t_type = self.combo_type.get()
        self.form_frame.config(text=f" {'Edit' if self.editing_id else 'Add'} {t_type} ")
        btn_text = f"{'Update' if self.editing_id else 'Add'} {t_type}"
        self.add_btn.config(text=btn_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerPro(root)
    root.mainloop()
