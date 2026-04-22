# 💰 Expense Tracker Pro

A feature-rich, professional Python application to manage and track your daily expenses with ease. Built with a sleek dark-themed GUI and persistent storage.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## ✨ Features

- **Intuitive Dashboard**: Real-time calculation of total spending.
- **Dark Mode UI**: Professional aesthetic using a custom color palette (inspired by Catppuccin).
- **Comprehensive Tracking**: Log expenses with Date, Category, Amount, and Description.
- **Data Persistence**: All data is automatically saved to a local `expenses.csv` file.
- **Management Tools**: 
  - Add new expenses with validation.
  - Delete selected expenses from the record.
  - Refresh view to sync data.

## 🚀 Getting Started

### Prerequisites
- Python 3.x installed on your system.
- Standard libraries: `tkinter`, `csv`, `os`, `datetime`.

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
Run the main script:
```bash
python expense_tracker_pro.py
```

## 📂 Project Structure
- `expense_tracker_pro.py`: Main application script (Pro version with GUI).
- `expense_gui.py`: Basic GUI version.
- `expense_tracker.py`: Core logic/CLI version.
- `expenses.csv`: Local database (automatically generated).
- `.gitignore`: Standard Python ignore rules.

## 🛠️ Built With
- **Python** - Core logic.
- **Tkinter** - GUI framework.
- **CSV** - Data storage.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
