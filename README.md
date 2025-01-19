# Personal Expense Tracker

## Description

A personal expense tracker app where users can add, categorize, and analyze their spending habits. This project provides a hands-on opportunity to work with Python for data handling, visualization, and web development.

---

## Features in development

### 1. User Management

- Sign up and log in functionality.
- Password hashing using libraries like `passlib`.
- Session management using cookies.

### 2. Expense Tracking

- Users can:
  - Add expenses with details like amount, date, category, and optional notes.
  - View a list of all their expenses.

### 3. Data Storage

- Store user info, expense records, and categories.
- PostgreSQL and SQLAlchemy.
- Alembic for database migrations and versioning.

### 4. Expense Analytics

- Summarize spending habits:
  - Total expenses for a specific period.
  - Most expensive categories.
  - Monthly trends.
<!-- - Create charts using `matplotlib` or `plotly`. -->

### 5. Export Data

- Export expense data to a CSV file for external use.

### 6. Integration with APIs

- Currency conversion APIs to support multiple currencies.
- Email API to send monthly summaries to users. <!-- (e.g., SendGrid) -->

---

## Tools and Technologies

### Backend

- FastAPI

<!--
### Frontend (Optional)

- Jinja2 templates (for Flask/Django) or React frontend.
-->
### Database

- PostgreSQL.

### Libraries
<!--
- `pandas`: For data manipulation.
- `matplotlib` or `plotly`: For visualizations. -->
- `SQLAlchemy` and `Alembic` For database management.

### Package management
- `Astral UV`


### Testing

- `pytest` for unit testing.

---

## Stretch Goals

1. **Budget Alerts**:
   - Notify users when they exceed predefined spending limits.
3. **AI Insights**:
   - Predict future expenses using machine learning. <!-- (e.g., `scikit-learn`) -->

---
<!--
## Project Structure

### CLI Version Example

```bash
Welcome to Expense Tracker
1. Add Expense
2. View Report
3. Export Data
4. Exit
```

### Web Version

1. **Homepage**: Dashboard with spending summaries and visualizations.
2. **Add Expense**: A form to input details of a new expense.
3. **Reports**: Interactive charts to analyze spending trends.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Virtual environment (`venv` or `virtualenv`)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd personal-expense-tracker
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

- **For CLI**:
  ```bash
  python app.py
  ```
- **For Web**:
  ```bash
  flask run  # Or `python manage.py runserver` for Django
  ```

---

## Example Screenshots

### Dashboard (Web Version)

- Spending summary with charts.

### Add Expense Form

- User-friendly form for inputting expenses.

---
-->

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

