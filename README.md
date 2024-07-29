Here is the converted documentation in Markdown format:

**Expense Sharing Application Documentation**
==========================================

Overview
--------

The Expense Sharing Application is a Django-based RESTful API that allows users to create and manage expenses, split costs among participants, and generate balance sheets.

Setup and Installation Instructions
-----------------------------------

### Prerequisites

* Python 3.8 or higher
* Django 5.0 or higher
* SQLite (default database)

### Installation Steps

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/expsensesharings.git
cd expsensesharings
```
2. **Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. **Install Dependencies**
```bash
pip install -r requirements.txt
```
4. **Apply Migrations**
```bash
python manage.py migrate
```
5. **Run the Development Server**
```bash
python manage.py runserver
```
6. **Access the API**
Open your browser and navigate to http://localhost:8000/api/ to access the API endpoints.

API Endpoints
-------------

### User Management

1. **Create User**
* **URL**: `/api/users/create/`
* **Method**: `POST`
* **Request Body**:
```json
{
    "email": "user1@example.com",
    "password": "password123",
    "name": "User One",
    "mobile_number": "1234567890"
}
```
2. **Get User**
* **URL**: `/api/users/<user_id>/`
* **Method**: `GET`
* **Example**: Replace `<user_id>` with the actual user ID (e.g., 1).

### Expense Management

3. **Create Expense**
* **URL**: `/api/expenses/create/`
* **Method**: `POST`
* **Request Body (EQUAL Split)**:
```json
{
    "description": "Lunch with colleagues",
    "amount": "1500.00",
    "split_type": "EQUAL",
    "paid_by": 1,
    "participants": [1, 2]
}
```
* **Request Body (EXACT Split)**:
```json
{
    "description": "Office supplies",
    "amount": "500.00",
    "split_type": "EXACT",
    "paid_by": 1,
    "participants": [1, 2],
    "splits": [
        {"user": 1, "amount": "200.00"},
        {"user": 2, "amount": "300.00"}
    ]
}
```
* **Request Body (PERCENT Split)**:
```json
{
    "description": "Team building activity",
    "amount": "3000.00",
    "split_type": "PERCENT",
    "paid_by": 3,
    "participants": [1, 2, 3],
    "splits": [
        {"user": 1, "percent": 50},
        {"user": 2, "percent": 30},
        {"user": 3, "percent": 20}
    ]
}
```
4. **Get Expense**
* **URL**: `/api/expenses/<expense_id>/`
* **Method**: `GET`
* **Example**: Replace `<expense_id>` with the actual expense ID (e.g., 1).

### User Expense Overview

5. **Get User Expenses**
* **URL**: `/api/users/<user_id>/expenses/`
* **Method**: `GET`
* **Example**: Replace `<user_id>` with the actual user ID (e.g., 1).

### Overall Expense Management

6. **Get Overall Expenses**
* **URL**: `/api/expenses/`
* **Method**: `GET`
7. **Download Balance Sheet**
* **URL**: `/api/balance-sheet/`
* **Method**: `GET`
8. **Get Balance Details**
* **URL**: `/api/balance-details/`
* **Method**: `GET`

Conclusion
----------

This documentation provides a comprehensive guide to setting up and using the Expense Sharing Application. For further assistance, please refer to the code comments or reach out to the project maintainers.
