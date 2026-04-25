# 💰 Personal Finance Tracker Pro

A feature-rich, professional Python application to manage and track your daily expenses and income with ease. Built with a sleek dark-themed GUI, CLI support, and shared core logic for data integrity.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## ✨ Features

- **Intuitive Dashboard**: Real-time calculation of total income, expenses, and current balance.
- **Dark Mode UI**: Professional aesthetic using a custom color palette (inspired by Catppuccin) in the Pro version.
- **Comprehensive Tracking**: Log transactions with Date, Category, Amount, Description, and Type (Income/Expense).
- **Data Persistence**: Data is automatically saved to local CSV files with unique IDs for each transaction.
- **Management Tools**: 
  - Add, edit, and delete transactions with validation.
  - Real-time search and filtering by keyword, category, or type.
  - Sortable data table (click headers to sort).
  - Visual analysis with Pie, Bar, and Line charts using Matplotlib.
  - **Category Budgets**: Set monthly limits per category with visual warnings.
  - **Recurring Transactions**: Mark entries as monthly to have them auto-added.
  - **Data Export**: Export your transactions to professional Excel (.xlsx) or PDF (.pdf) formats.
  - **Summary View**: Grouped financial reports by month or week.
  - Automatic CSV migration and data sanitization to prevent injection.
- **Modular Design**: Shared core logic via `finance_manager.py` for consistent behavior across all versions.

## 🚀 Getting Started

### Prerequisites
- Python 3.x installed on your system.
- Required Libraries:
  ```bash
  pip install matplotlib xlsxwriter fpdf2
  ```

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Adi942-adi/expense-tracker-pro.git
   ```
2. Navigate to the project directory:
   ```bash
   cd expense-tracker-pro
   ```

### Running the App
There are three ways to run the tracker:

**1. Pro GUI Version (Recommended)**
```bash
python expense_tracker_pro.py
```

**2. Basic GUI Version**
```bash
python expense_gui.py
```

**3. CLI Version**
```bash
python expense_tracker.py
```

## 📂 Project Structure
- `expense_tracker_pro.py`: Advanced GUI application with real-time dashboard.
- `expense_gui.py`: Lightweight GUI version for basic tracking.
- `expense_tracker.py`: Command-line interface version.
- `finance_manager.py`: Shared core logic for validation, sanitization, and data handling.
- `expenses_pro.csv`: Data storage for the Pro version.
- `expenses_gui.csv`: Data storage for the basic GUI version.
- `expenses_cli.csv`: Data storage for the CLI version.

## 🛠️ Built With
- **Python** - Core logic.
- **Tkinter** - GUI framework.
- **CSV** - Data storage.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
