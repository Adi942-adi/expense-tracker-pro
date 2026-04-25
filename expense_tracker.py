import finance_manager as fm

file_name = "expenses_cli.csv" 

def add_expense(): 
    date = input("Enter Date (YYYY-MM-DD): ") 
    if not fm.validate_date(date):
        print("Invalid date format. Use YYYY-MM-DD.")
        return

    category = input("Enter Category: ") 
    if not category:
        print("Category cannot be empty.")
        return

    amount = input("Enter Amount: ") 
    if not fm.validate_amount(amount):
        print("Invalid amount. Must be a number greater than zero.")
        return

    desc = input("Enter Description: ") 
    
    print("1. Expense")
    print("2. Income")
    while True:
        type_choice = input("Enter type (1/2): ")
        if type_choice in ["1", "2"]:
            break
        print("Invalid choice. Please enter 1 for Expense or 2 for Income.")
        
    trans_type = "Income" if type_choice == "2" else "Expense"

    fm.save_transaction(file_name, date, category, amount, desc, trans_type)
    print(f"{trans_type} Added!\n") 


def view_expenses(): 
    print("\n--- All Transactions ---") 
    transactions = fm.load_all_transactions(file_name)
    if not transactions:
        print("No transactions found.")
        return

    for row in transactions: 
        # ID, Date, Category, Amount, Description, Type
        print(f"ID: {row[0][:8]}... | Date: {row[1]} | Category: {row[2]} | Amount: {row[3]} | Desc: {row[4]} | Type: {row[5]}") 
    print() 


def total_expense(): 
    transactions = fm.load_all_transactions(file_name)
    total_income, total_expenses, balance = fm.calculate_totals(transactions)
    
    print(f"Total Income: ₹{total_income:,.2f}")
    print(f"Total Expenses: ₹{total_expenses:,.2f}")
    print(f"Balance: ₹{balance:,.2f}\n") 


# Menu 
if __name__ == "__main__":
    fm.ensure_csv_exists(file_name)
    while True: 
        print("1. Add Transaction") 
        print("2. View Transactions") 
        print("3. Show Summary") 
        print("4. Exit") 

        choice = input("Enter choice: ") 

        if choice == "1": 
            add_expense() 
        elif choice == "2": 
            view_expenses() 
        elif choice == "3": 
            total_expense() 
        elif choice == "4": 
            break 
        else: 
            print("Invalid choice\n") 
