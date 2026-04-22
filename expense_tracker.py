import csv 
import os 

file_name = "expenses.csv" 

# Create file if not exists 
if not os.path.exists(file_name): 
    with open(file_name, "w", newline="") as f: 
        writer = csv.writer(f) 
        writer.writerow(["Date", "Category", "Amount", "Description"]) 


def add_expense(): 
    date = input("Enter Date: ") 
    category = input("Enter Category: ") 
    amount = input("Enter Amount: ") 
    desc = input("Enter Description: ") 

    with open(file_name, "a", newline="") as f: 
        writer = csv.writer(f) 
        writer.writerow([date, category, amount, desc]) 

    print("Expense Added!\n") 


def view_expenses(): 
    print("\n--- All Expenses ---") 
    with open(file_name, "r") as f: 
        reader = csv.reader(f) 
        next(reader)  # skip header 

        for row in reader: 
            print("Date:", row[0], 
                  "| Category:", row[1], 
                  "| Amount:", row[2], 
                  "| Desc:", row[3]) 
    print() 


def total_expense(): 
    total = 0 
    with open(file_name, "r") as f: 
        reader = csv.reader(f) 
        next(reader) 

        for row in reader: 
            total += float(row[2]) 

    print("Total Expense: ₹", total, "\n") 


# Menu 
if __name__ == "__main__":
    while True: 
        print("1. Add Expense") 
        print("2. View Expenses") 
        print("3. Total Expense") 
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
