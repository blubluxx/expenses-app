# Personal Expense Tracker

## Description

A personal expense tracker app where users can add, categorize, and analyze their spending habits. This project is designed for intermediate developers and provides a hands-on opportunity to work with Python for data handling, visualization, and web development.

---

## Features

### 1. User Management

- Sign up and log in functionality.
- Password hashing using libraries like `bcrypt`.
- Session management with Flask-Login or Django's authentication system.

### 2. Expense Tracking

- Users can:
  - Add expenses with details like amount, date, category, and optional notes.
  - View a list of all their expenses.

### 3. Data Storage

- Use a SQLite database (or PostgreSQL/MySQL for scalability).
- Store user info, expense records, and categories.

### 4. Expense Analytics

- Summarize spending habits:
  - Total expenses for a specific period.
  - Most expensive categories.
  - Monthly trends.
- Create charts using `matplotlib` or `plotly`.

### 5. Export Data

- Export expense data to a CSV file for external use.

### 6. Optional: Integration with APIs

- Currency conversion APIs to support multiple currencies.
- Email API (e.g., SendGrid) to send monthly summaries to users.

---

## Tools and Technologies

### Backend

- Flask or Django

### Frontend (Optional)

- Jinja2 templates (for Flask/Django) or React frontend.

### Database

- SQLite (or PostgreSQL/MySQL for advanced features).

### Libraries

- `pandas`: For data manipulation.
- `matplotlib` or `plotly`: For visualizations.
- `flask_sqlalchemy` or `django_orm`: For database management.
- `requests`: For API calls.

### Testing

- Use `pytest` for unit testing.

---

## Stretch Goals

1. **Mobile-Friendly Web App**:
   - Responsive design using Bootstrap or Tailwind CSS.
2. **Budget Alerts**:
   - Notify users when they exceed predefined spending limits.
3. **AI Insights**:
   - Predict future expenses using machine learning (e.g., `scikit-learn`).

---

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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Contributions

Contributions are welcome! Feel free to submit a pull request or open an issue.
