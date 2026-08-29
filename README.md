# Canteen Coupon Management System

A simple Flask web application for generating and managing canteen coupons. It allows users to create coupon numbers, view the latest coupon, mark coupons as served, and delete pending entries.

## Features

- Generate a new coupon with a unique ID-based number such as `C00001`
- View the latest issued coupon on the home page
- Manage pending and served coupons
- Mark a coupon as served
- Delete a coupon from the queue
- Store data in SQLite using Flask-SQLAlchemy

## Tech Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- SQLite

## Project Structure

```text
Management/
├── test.py
├── templates/
│   ├── index.html
│   ├── created.html
│   └── manage.html
├── canteen.db
└── README.md
```

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd Management
```

2. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install flask flask-sqlalchemy
```

## Running the App

From the project folder, run:

```bash
python test.py
```

Then open the browser at:

```text
http://127.0.0.1:5000/
```

## How It Works

- The app creates a SQLite database file named `canteen.db` automatically.
- The `Coupon` model stores:
  - `id`
  - `number`
  - `status`
  - `created_at`
- A new coupon is generated and assigned a number in the format `C00001`.
- The management page lets staff mark coupons as served or delete them.

## Routes

- `GET /` - Home page showing the latest coupon
- `POST /create` - Create a new coupon
- `GET /manage` - View pending and served coupons
- `POST /manage` - Serve or delete a coupon

## Notes

This project is intended for local development and is not configured for production deployment. The Flask debug server is used for convenience during development.

## License

This project is provided as-is for educational and development use.
