import unittest
import os
import csv
import uuid
import finance_manager as fm

class TestFinanceManager(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_expenses.csv"
        # Ensure a clean state for each test
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_sanitize_input(self):
        self.assertEqual(fm.sanitize_input("hello,world"), "hello world")
        self.assertEqual(fm.sanitize_input("line1\nline2"), "line1 line2")
        self.assertEqual(fm.sanitize_input("  clean text  "), "clean text")
        self.assertEqual(fm.sanitize_input(123), 123)

    def test_validate_date(self):
        self.assertTrue(fm.validate_date("2023-01-01"))
        self.assertFalse(fm.validate_date("01-01-2023"))
        self.assertFalse(fm.validate_date("2023/01/01"))
        self.assertFalse(fm.validate_date("not-a-date"))

    def test_validate_amount(self):
        self.assertTrue(fm.validate_amount("10.50"))
        self.assertTrue(fm.validate_amount(100))
        self.assertFalse(fm.validate_amount("-10"))
        self.assertFalse(fm.validate_amount("0"))
        self.assertFalse(fm.validate_amount("abc"))

    def test_ensure_csv_exists(self):
        fm.ensure_csv_exists(self.test_file)
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header, fm.CSV_HEADER)

    def test_save_and_load_transaction(self):
        fm.save_transaction(self.test_file, "2023-10-25", "Food", "50.00", "Lunch", "Expense")
        transactions = fm.load_all_transactions(self.test_file)
        self.assertEqual(len(transactions), 1)
        # Check values (skipping ID at index 0)
        self.assertEqual(transactions[0][1], "2023-10-25")
        self.assertEqual(transactions[0][2], "Food")
        self.assertEqual(transactions[0][3], "50.00")
        self.assertEqual(transactions[0][4], "Lunch")
        self.assertEqual(transactions[0][5], "Expense")

    def test_delete_transaction(self):
        tid = fm.save_transaction(self.test_file, "2023-10-25", "Food", "50.00", "Lunch", "Expense")
        fm.save_transaction(self.test_file, "2023-10-26", "Bills", "100.00", "Internet", "Expense")
        
        self.assertTrue(fm.delete_transaction_by_id(self.test_file, tid))
        transactions = fm.load_all_transactions(self.test_file)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0][2], "Bills")

    def test_update_transaction(self):
        tid = fm.save_transaction(self.test_file, "2023-10-25", "Food", "50.00", "Lunch", "Expense")
        fm.update_transaction(self.test_file, tid, "2023-10-25", "Food", "60.00", "Lunch Update", "Expense")
        
        transactions = fm.load_all_transactions(self.test_file)
        self.assertEqual(transactions[0][3], "60.00")
        self.assertEqual(transactions[0][4], "Lunch Update")

    def test_filter_transactions(self):
        transactions = [
            ["1", "2023-10-25", "Food", "50.00", "Lunch", "Expense"],
            ["2", "2023-10-26", "Bills", "100.00", "Internet", "Expense"],
            ["3", "2023-10-27", "Salary", "1000.00", "Salary", "Income"]
        ]
        
        # Search query
        res = fm.filter_transactions(transactions, query="Internet")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], "2")
        
        # Category filter
        res = fm.filter_transactions(transactions, category="Food")
        self.assertEqual(len(res), 1)
        
        # Type filter
        res = fm.filter_transactions(transactions, trans_type="Income")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][5], "Income")

    def test_calculate_totals(self):
        transactions = [
            [str(uuid.uuid4()), "2023-10-25", "Salary", "1000.00", "Oct Salary", "Income"],
            [str(uuid.uuid4()), "2023-10-26", "Food", "50.00", "Lunch", "Expense"],
            [str(uuid.uuid4()), "2023-10-27", "Rent", "500.00", "Oct Rent", "Expense"]
        ]
        income, expenses, balance = fm.calculate_totals(transactions)
        self.assertEqual(income, 1000.0)
        self.assertEqual(expenses, 550.0)
        self.assertEqual(balance, 450.0)

if __name__ == "__main__":
    unittest.main()
