# 💰 Personal Finance Advisor

A full-stack **AI-powered personal finance dashboard** that helps users track transactions, set budgets, visualize spending trends, and receive intelligent financial recommendations — all in one sleek interface.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Setup Guide](#-setup-guide)
  - [Step 1 — Clone the Repository](#step-1--clone-the-repository)
  - [Step 2 — Set Up MySQL Database](#step-2--set-up-mysql-database)
  - [Step 3 — Configure Environment Variables](#step-3--configure-environment-variables)
  - [Step 4 — Set Up the Backend (Python/Flask)](#step-4--set-up-the-backend-pythonflask)
  - [Step 5 — Set Up the Frontend (React/Vite)](#step-5--set-up-the-frontend-reactvite)
  - [Step 6 — Run the Application](#step-6--run-the-application)
- [API Reference](#-api-reference)
- [CSV Import Format](#-csv-import-format)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Dashboard** | Live summary of income, expenses, net balance, and savings rate |
| 💳 **Transactions** | Add, view, delete, and filter financial transactions manually or via CSV import |
| 🤖 **AI Categorization** | Dual-engine system (Rule-based + Naive Bayes ML) auto-categorizes transactions |
| 📈 **Analytics** | Interactive Recharts visualizations — trends (area/line chart) and category distribution |
| 💡 **AI Insights** | Actionable financial recommendations based on your spending patterns |
| 🎯 **Budgets** | Set monthly budget limits per category, track spend vs budget, receive alerts |
| 💬 **AI Chatbot** | Conversational LLM (Groq/Llama 3) with Context Injection to answer natural language questions about your data |
| 📤 **CSV Upload** | Bulk import transactions from a structured CSV file |

---

## 🛠 Tech Stack

### Backend
- **Python 3.10+** + **Flask** — REST API
- **MySQL** — Relational database
- **scikit-learn** — Naive Bayes ML categorizer (TF-IDF + MultinomialNB)
- **Groq API** — Extremely fast LLM inference for the Chatbot (Llama 3.3)
- **NLTK** — Text processing utilities
- **pandas / numpy** — Data processing for analytics

### Frontend
- **React 19** + **Vite 8** — Modern SPA framework
- **React Router v7** — Client-side routing
- **Recharts** — Data visualization (Area, Bar, Pie charts)
- **Tailwind CSS v4** — Utility-first styling
- **Lucide React** — Icon library
- **Axios** — HTTP client

---

## 📁 Project Structure

```
financial-advisor/
├── backend/
│   ├── app.py                  # Flask entry point — registers all blueprints
│   ├── config.py               # DB connection config (reads from database/.env)
│   ├── requirements.txt        # Python dependencies
│   ├── ml/
│   │   ├── categorizer.py      # Dual-mode categorization engine (rules + Naive Bayes)
│   │   ├── training_data.csv   # Seed training data for the ML model
│   │   └── model_store/        # Auto-generated — saved trained model (.pkl)
│   ├── routes/
│   │   ├── analytics.py        # GET /api/analytics/* — trends, distribution, metrics
│   │   ├── budgets.py          # GET/POST/DELETE /api/budgets/*
│   │   ├── categories.py       # GET/POST /api/categories
│   │   ├── categorize.py       # POST /api/categorize — ML categorization endpoint
│   │   ├── chatbot.py          # POST /api/chat — NLP chatbot
│   │   ├── recommendations.py  # GET /api/recommendations — AI insights
│   │   ├── transactions.py     # GET/POST/DELETE /api/transactions
│   │   └── upload.py           # POST /api/upload/csv — bulk CSV import
│   ├── tests/                  # Test scripts
│   └── utils/
│       ├── csv_parser.py       # CSV parsing & validation logic
│       └── db_helper.py        # Reusable database utility functions
│
├── database/
│   ├── .env                    # ⚠️ DB credentials — NOT committed to git
│   ├── schema.sql              # Full database schema (tables, FK constraints)
│   ├── init_mysql.py           # Script to initialize DB + seed default data
│   ├── seed_mysql.py           # Optional script to seed sample transactions
│   └── reset_data.py           # Script to wipe all transaction data (keep schema)
│
└── frontend/
    ├── index.html
    ├── vite.config.js          # Vite config — proxies /api/* to localhost:5000
    ├── package.json
    └── src/
        ├── main.jsx
        ├── App.jsx             # Root component with routing
        └── components/
            ├── Dashboard.jsx       # Overview cards + quick stats
            ├── Transactions.jsx    # Transaction list, add form, CSV upload
            ├── Analytics.jsx       # Charts + AI insights section
            ├── Budgets.jsx         # Budget management + progress bars
            ├── Chatbot.jsx         # Chat interface
            ├── Settings.jsx        # App settings page
            └── TopNavbar.jsx       # Navigation bar
```

---

## ✅ Prerequisites

Make sure the following are installed on your machine **before** starting:

| Requirement | Version | Download |
|---|---|---|
| **Python** | 3.10 or higher | https://www.python.org/downloads/ |
| **Node.js** | 18 or higher | https://nodejs.org/ |
| **MySQL Server** | 8.0 or higher | https://dev.mysql.com/downloads/mysql/ |
| **Git** | Any recent version | https://git-scm.com/ |

> **Tip:** To verify installations, run: `python --version`, `node --version`, `mysql --version`

---

## 🚀 Setup Guide

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Madhesh21/personal-finance-advisor.git
cd personal-finance-advisor
```

---

### Step 2 — Set Up MySQL Database

1. **Start your MySQL server** and open the MySQL shell (or use MySQL Workbench):

   ```bash
   mysql -u root -p
   ```

2. **Verify MySQL is running.** You should see the `mysql>` prompt. Then exit:

   ```sql
   exit;
   ```

> The database and tables will be created automatically in the next steps via the init script — you do **not** need to run `schema.sql` manually.

---

### Step 3 — Configure Environment Variables

The backend reads database credentials from `database/.env`. This file is **not committed to Git** (it's in `.gitignore`), so you must create it yourself.

1. Navigate to the `database/` folder and create a `.env` file:

   ```bash
   # On Windows (PowerShell)
   cd database
   New-Item -Name ".env" -ItemType "file"
   ```

2. Open the file and add your MySQL credentials and LLM configuration:

   ```env
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_password_here
   DB_NAME=personal_finance

   # ── LLM Chatbot Configuration ──
   # LLM_PROVIDER can be 'groq', 'gemini', or 'ollama'
   LLM_PROVIDER=groq
   # Get a free API key from https://console.groq.com/keys
   LLM_API_KEY=gsk_your_groq_api_key_here
   LLM_MODEL=llama-3.3-70b-versatile
   ```

   > Replace `your_mysql_password_here` with your actual MySQL root password, and grab a free API key from Groq to enable the conversational chatbot.

---

### Step 4 — Set Up the Backend (Python/Flask)

> All backend commands should be run from the **`backend/`** directory unless specified.

**4a. Create and activate a Python virtual environment:**

```bash
# Windows (PowerShell)
cd backend
python -m venv venv
venv\Scripts\Activate.ps1

# macOS / Linux
cd backend
python3 -m venv venv
source venv/bin/activate
```

> Your terminal prompt should now show `(venv)` at the beginning.

**4b. Install Python dependencies:**

```bash
pip install -r requirements.txt
```

**4c. Initialize the database** (creates DB, tables, and seeds default categories + a default user):

```bash
# Run from the project root
cd ..
python database/init_mysql.py
```

Expected output:
```
Connecting to MySQL server at 127.0.0.1:3306 as root...
Creating database `personal_finance` if it does not exist...
Inserting default categories...
Inserting default user...
Database initialization completed effectively!
```

> **Optional:** Seed the database with sample transaction data for testing:
> ```bash
> python database/seed_mysql.py
> ```

---

### Step 5 — Set Up the Frontend (React/Vite)

> All frontend commands should be run from the **`frontend/`** directory.

**5a. Install Node.js dependencies:**

```bash
cd frontend
npm install
```

This installs all packages listed in `package.json` (React, Recharts, Tailwind CSS, Axios, etc.).

---

### Step 6 — Run the Application

You need **two terminal windows** running simultaneously — one for the backend and one for the frontend.

**Terminal 1 — Start the Flask Backend:**

```bash
# From the project root, with venv activated
cd backend
venv\Scripts\Activate.ps1   # Windows  (skip if already activated)
# source venv/bin/activate  # macOS/Linux

python app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

**Terminal 2 — Start the React Frontend:**

```bash
cd frontend
npm run dev
```

Expected output:
```
  VITE ready in XXXms
  ➜  Local:   http://localhost:5173/
```

**Open your browser and navigate to: [http://localhost:5173](http://localhost:5173)**

> The Vite dev server automatically proxies all `/api/*` requests to the Flask backend at `http://127.0.0.1:5000`, so no CORS configuration is needed during development.

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/transactions` | List all transactions |
| `POST` | `/api/transactions` | Add a new transaction |
| `DELETE` | `/api/transactions/<id>` | Delete a transaction |
| `GET` | `/api/transactions/summary` | Income/expense totals |
| `GET` | `/api/categories` | List all categories |
| `POST` | `/api/categories` | Add a new category |
| `GET` | `/api/budgets` | List all budgets |
| `POST` | `/api/budgets` | Set a budget limit |
| `DELETE` | `/api/budgets/<id>` | Delete a budget |
| `GET` | `/api/budgets/summary` | Budget vs actual spending |
| `GET` | `/api/budgets/alerts` | Categories exceeding budget |
| `GET` | `/api/recommendations` | AI financial recommendations |
| `GET` | `/api/analytics/trends` | Monthly income/expense trends |
| `GET` | `/api/analytics/distribution` | Spending by category |
| `GET` | `/api/analytics/metrics` | Key financial metrics |
| `POST` | `/api/upload/csv` | Bulk import transactions from CSV |
| `GET` | `/api/upload/template` | Download a CSV template |
| `POST` | `/api/categorize` | Auto-categorize a transaction description |
| `POST` | `/api/chat` | NLP chatbot query |

---

## 📄 CSV Import Format

To bulk import transactions, your CSV file must follow this structure:

| Column | Type | Required | Example |
|---|---|---|---|
| `date` | `YYYY-MM-DD` | ✅ | `2026-04-15` |
| `description` | Text | ✅ | `Grocery shopping at Walmart` |
| `amount` | Decimal | ✅ | `85.50` |
| `type` | `INCOME` or `EXPENSE` | ❌ (auto-detected) | `EXPENSE` |
| `category` | Category name | ❌ (auto-categorized) | `Food` |

> **Tip:** Download a pre-formatted template via `GET /api/upload/template` or use the **Upload** button in the Transactions page.

---

## 🔧 Troubleshooting

### ❌ `Access denied for user 'root'@'localhost'`
Your MySQL password in `database/.env` is incorrect. Double-check `DB_PASSWORD`.

### ❌ `ModuleNotFoundError: No module named 'flask'`
Your virtual environment is not activated. Run `venv\Scripts\Activate.ps1` (Windows) or `source venv/bin/activate` (macOS/Linux) from the `backend/` directory.

### ❌ `OSError: [E050] Can't find model 'en_core_web_sm'`
The spaCy language model is missing. Run:
```bash
python -m spacy download en_core_web_sm
```

### ❌ `npm install` fails or hangs
Make sure Node.js 18+ is installed. Try clearing the npm cache:
```bash
npm cache clean --force
npm install
```

### ❌ Frontend shows blank page or network errors
- Confirm the Flask backend is running on port `5000`.
- Check the browser console (F12) for specific error messages.
- Make sure `vite.config.js` proxy target is `http://127.0.0.1:5000`.

### ❌ ML Model errors on first run
The Naive Bayes model (`backend/ml/model_store/nb_model.pkl`) is auto-generated on first startup from `training_data.csv`. If it fails, ensure `scikit-learn` and `joblib` are installed correctly.

---

## 👥 Default Credentials

After running `init_mysql.py`, a default user is created automatically:

| Field | Value |
|---|---|
| **User ID** | `1` |
| **Name** | `Default User` |
| **Email** | `user@example.com` |

All API calls default to `user_id=1` unless specified otherwise.

---

## 🗄️ Database Schema Overview

```
users ──< transactions >── categories
users ──< budgets >──────── categories
users ──< user_corrections >── categories
```

| Table | Purpose |
|---|---|
| `users` | User accounts |
| `categories` | Income/Expense categories (e.g., Salary, Food, Rent) |
| `transactions` | All financial transactions linked to user + category |
| `budgets` | Monthly budget limits per category per user |
| `user_corrections` | ML reinforcement — stores user corrections to improve auto-categorization |

---

> Built with ❤️ by Madhesh21
