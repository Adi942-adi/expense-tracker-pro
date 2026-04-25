import csv
import os
import uuid
from datetime import datetime, timedelta
import xlsxwriter
from fpdf import FPDF

# Common Constants
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
CSV_HEADER = ["ID", "Date", "Category", "Amount", "Description", "Type"]
BUDGET_FILE = "budgets.csv"
BUDGET_HEADER = ["Category", "Limit"]
RECURRING_FILE = "recurring.csv"
RECURRING_HEADER = ["ID", "Category", "Amount", "Description", "Type", "DayOfMonth"]

def ensure_recurring_exists():
    """Ensure the recurring CSV file exists."""
    if not os.path.exists(RECURRING_FILE):
        with open(RECURRING_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(RECURRING_HEADER)

def add_recurring_transaction(category, amount, description, trans_type, day):
    """Save a recurring transaction template."""
    ensure_recurring_exists()
    new_id = str(uuid.uuid4())
    with open(RECURRING_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([new_id, category, amount, description, trans_type, day])
    return new_id

def load_recurring_transactions():
    """Load all recurring transaction templates."""
    ensure_recurring_exists()
    recurring = []
    with open(RECURRING_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            recurring.append(row)
    return recurring

def process_recurring(file_name):
    """Check and add recurring transactions for the current month if they haven't been added."""
    recurring = load_recurring_transactions()
    if not recurring:
        return 0
        
    transactions = load_all_transactions(file_name)
    current_month = datetime.now().strftime("%Y-%m")
    added_count = 0
    
    for rec in recurring:
        rec_id, cat, amt, desc, t_type, day = rec
        # Check if this recurring item was already added this month
        # We look for a transaction with same category, amount, type and description containing "Recurring"
        already_added = False
        for t in transactions:
            if t[1].startswith(current_month) and t[2] == cat and t[5] == t_type and f"(Recurring: {rec_id})" in t[4]:
                already_added = True
                break
        
        if not already_added:
            # BUG-04: Only add if the target day has been reached in the current month
            target_day = int(day)
            if target_day > datetime.now().day:
                continue # Not due yet this month
                
            # Add it for the current month
            today = datetime.now()
            # If the day has passed or is today, add it with the current date or the specified day
            # For simplicity, we add it with the current month and the specified day
            try:
                # Ensure the day is valid for the current month
                target_day = min(int(day), 28) # Simple guard for Feb
                date_str = f"{current_month}-{target_day:02d}"
                save_transaction(file_name, date_str, cat, amt, f"{desc} (Recurring: {rec_id})", t_type)
                added_count += 1
            except Exception:
                continue
                
    return added_count

def export_to_excel(file_name, output_path):
    """Export transactions to an Excel file."""
    transactions = load_all_transactions(file_name)
    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet("Transactions")
    
    # Add formats
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
    money_format = workbook.add_format({'num_format': '₹#,##0.00'})
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    
    # Write Header
    for col_num, header in enumerate(CSV_HEADER):
        worksheet.write(0, col_num, header, header_format)
    
    # Write Data
    for row_num, row_data in enumerate(transactions, start=1):
        for col_num, cell_data in enumerate(row_data):
            if col_num == 3: # Amount
                worksheet.write(row_num, col_num, float(cell_data), money_format)
            elif col_num == 1: # Date
                worksheet.write(row_num, col_num, cell_data, date_format)
            else:
                worksheet.write(row_num, col_num, cell_data)
                
    worksheet.set_column('A:A', 36) # ID
    worksheet.set_column('B:B', 12) # Date
    worksheet.set_column('C:C', 15) # Category
    worksheet.set_column('D:D', 12) # Amount
    worksheet.set_column('E:E', 30) # Description
    worksheet.set_column('F:F', 10) # Type
    
    workbook.close()
    return True

def export_to_pdf(file_name, output_path):
    """Export transactions to a PDF file."""
    transactions = load_all_transactions(file_name)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Transaction Report", ln=True, align="C")
    pdf.ln(10)
    
    # Header
    pdf.set_font("Arial", "B", 10)
    col_widths = [10, 25, 30, 25, 70, 25] # ID is shortened
    headers = ["#", "Date", "Category", "Amount", "Description", "Type"]
    
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1, 0, "C")
    pdf.ln()
    
    # Data
    pdf.set_font("Arial", "", 9)
    for i, row in enumerate(transactions, start=1):
        # We'll use index i instead of long UUID for PDF readability
        data = [str(i), row[1], row[2], f"Rs. {row[3]}", row[4][:35], row[5]]
        for j, cell in enumerate(data):
            pdf.cell(col_widths[j], 10, str(cell), 1)
        pdf.ln()
        
    pdf.output(output_path)
    return True

def get_period_summary(file_name, period="Monthly"):
    """Get a summary of income and expenses grouped by period (Monthly/Weekly)."""
    transactions = load_all_transactions(file_name)
    summary = {} # Key: Period string, Value: [Income, Expenses]
    
    for row in transactions:
        try:
            date_str = row[1]
            amount = float(row[3])
            trans_type = row[5]
        except (ValueError, IndexError):
            continue
        
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            if period == "Monthly":
                key = dt.strftime("%Y-%m")
            else: # Weekly
                # Get the start of the week (Monday)
                week_start = dt.date() - timedelta(days=dt.weekday())
                key = f"Week of {week_start}"
        except Exception:
            continue
            
        if key not in summary:
            summary[key] = [0.0, 0.0]
            
        if trans_type == "Income":
            summary[key][0] += amount
        else:
            summary[key][1] += amount
            
    # Sort keys chronologically
    sorted_keys = sorted(summary.keys(), reverse=True)
    return {k: summary[k] for k in sorted_keys}

def ensure_budget_exists():
    """Ensure the budgets CSV file exists."""
    if not os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(BUDGET_HEADER)
            # Initialize with 0 for all categories
            for cat in CATEGORIES:
                writer.writerow([cat, "0.00"])

def load_budgets():
    """Load category budgets from CSV."""
    ensure_budget_exists()
    budgets = {}
    with open(BUDGET_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) == 2:
                budgets[row[0]] = float(row[1])
    return budgets

def save_budget(category, limit):
    """Save/Update a budget for a category."""
    budgets = load_budgets()
    budgets[category] = float(limit)
    
    with open(BUDGET_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(BUDGET_HEADER)
        for cat, lim in budgets.items():
            writer.writerow([cat, f"{lim:.2f}"])

def check_budget_warning(category, amount, transactions):
    """Check if adding an amount to a category exceeds its budget."""
    budgets = load_budgets()
    limit = budgets.get(category, 0)
    if limit <= 0:
        return None # No budget set
        
    # Calculate current spending for this category (this month)
    current_month = datetime.now().strftime("%Y-%m")
    current_spending = 0
    for row in transactions:
        try:
            row_date = row[1]
            row_cat = row[2]
            row_amount = float(row[3])
            row_type = row[5]
        except (ValueError, IndexError):
            continue
        
        if row_type == "Expense" and row_cat == category and row_date.startswith(current_month):
            current_spending += row_amount
            
    total_after = current_spending + float(amount)
    if total_after > limit:
        return f"Warning: This will exceed your ₹{limit:.2f} budget for {category}!\nCurrent: ₹{current_spending:.2f}, New Total: ₹{total_after:.2f}"
    elif total_after > limit * 0.9:
        return f"Note: You are approaching your ₹{limit:.2f} budget for {category} (90% reached)."
    return None

def sanitize_input(text):
    """Prevent CSV injection by removing commas and newlines."""
    if not isinstance(text, str):
        return text
    return text.replace(",", " ").replace("\n", " ").replace("\r", " ").strip()

def validate_date(date_str):
    """Validate date format YYYY-MM-DD."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_amount(amount_str):
    """Validate amount is a positive number."""
    try:
        amount = float(amount_str)
        return amount > 0
    except ValueError:
        return False

def ensure_csv_exists(file_name):
    """Ensure the CSV file exists with the correct header and migration."""
    if not os.path.exists(file_name):
        with open(file_name, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
    else:
        # Migration check
        with open(file_name, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
                if header != CSV_HEADER:
                    _migrate_csv(file_name, header)
            except StopIteration:
                # Empty file
                with open(file_name, "w", newline="", encoding="utf-8") as fw:
                    writer = csv.writer(fw)
                    writer.writerow(CSV_HEADER)

def _migrate_csv(file_name, old_header):
    """Internal helper to migrate CSV to new header format."""
    rows = []
    with open(file_name, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            next(reader) # Skip the old header
        except StopIteration:
            return
            
        for row in reader:
            if not row or row == old_header or row == CSV_HEADER:
                continue
                
            new_row = [str(uuid.uuid4())] # Default ID
            
            # Map columns based on old header content
            # This is a simplified migration. In a real app, you'd match by header names.
            # Assuming old formats were either 4 or 5 columns.
            if len(row) == 4: # Date, Category, Amount, Description
                new_row.extend(row)
                new_row.append("Expense") # Default Type
            elif len(row) == 5:
                if "ID" not in old_header: # Date, Category, Amount, Description, Type
                    new_row.extend(row)
                else: # ID, Date, Category, Amount, Description (Missing Type)
                    new_row = row + ["Expense"]
            elif len(row) == 6: # Likely correct but check order or missing ID
                if old_header[0] != "ID":
                     # BUG-05: Don't drop row[5]. If it has 6 columns, just prepend a new ID and keep all original data
                     new_row = [str(uuid.uuid4())] + row
                else:
                     new_row = row
            rows.append(new_row)

    with open(file_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        writer.writerows(rows)

def load_all_transactions(file_name):
    """Load all transactions from CSV."""
    transactions = []
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                next(reader) # skip header
                for row in reader:
                    if len(row) == len(CSV_HEADER):
                        try:
                            # Verify amount is a number to filter out corrupted header rows
                            float(row[3])
                            transactions.append(row)
                        except ValueError:
                            continue
            except StopIteration:
                pass
    return transactions

def save_transaction(file_name, date, category, amount, description, trans_type):
    """Save a single transaction to CSV with sanitization and unique ID."""
    ensure_csv_exists(file_name)
    new_id = str(uuid.uuid4())
    sanitized_desc = sanitize_input(description)
    sanitized_cat = sanitize_input(category)
    
    with open(file_name, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([new_id, date, sanitized_cat, f"{float(amount):.2f}", sanitized_desc, trans_type])
    return new_id

def delete_transaction_by_id(file_name, item_id):
    """Delete a transaction from the CSV by its unique ID."""
    rows = load_all_transactions(file_name)
    new_rows = [row for row in rows if row[0] != item_id]
    
    if len(rows) == len(new_rows):
        return False
        
    with open(file_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        writer.writerows(new_rows)
    return True

def update_transaction(file_name, item_id, date, category, amount, description, trans_type):
    """Update an existing transaction in the CSV by its unique ID."""
    rows = load_all_transactions(file_name)
    updated = False
    
    sanitized_desc = sanitize_input(description)
    sanitized_cat = sanitize_input(category)
    
    for i, row in enumerate(rows):
        if row[0] == item_id:
            rows[i] = [item_id, date, sanitized_cat, f"{float(amount):.2f}", sanitized_desc, trans_type]
            updated = True
            break
            
    if updated:
        with open(file_name, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
            writer.writerows(rows)
    return updated

def filter_transactions(transactions, query=None, category=None, trans_type=None):
    """Filter a list of transactions based on multiple criteria."""
    filtered = transactions
    
    if query:
        query = query.lower()
        filtered = [row for row in filtered if any(query in str(cell).lower() for cell in row)]
        
    if category and category != "All":
        filtered = [row for row in filtered if row[2] == category]
        
    if trans_type and trans_type != "All":
        filtered = [row for row in filtered if row[5] == trans_type]
        
    return filtered

def calculate_totals(transactions):
    """Calculate income, expenses, and balance from a list of transaction rows."""
    income = 0.0
    expenses = 0.0
    for row in transactions:
        try:
            amount = float(row[3])
            t_type = row[5]
            if t_type == "Income":
                income += amount
            else:
                expenses += amount
        except (ValueError, IndexError):
            continue
    return income, expenses, income - expenses
