# Canteen Coupon Management System

A Flask web application for generating and managing canteen coupons. Customers enter their name to get a coupon, staff manage the queue, and a live display board shows the name of the customer being served.

## Features

- Generate a coupon for a customer by name; each coupon also gets an internal number such as `C00001`
- The customer name and coupon number are shown together everywhere (name large, number as a tag)
- Printable coupon page showing how many people are ahead in the queue
- Home page with "Now Serving", queue statistics and the latest coupon
- Staff queue manager: serve, undo (move back to queue), delete, and search coupons
- Live display board (`/display`) that refreshes every 5 seconds, for a TV or monitor
- JSON API (`/api/queue`) for the current queue state
- Responsive layout for phones and desktops, with automatic dark mode
- Store data in SQLite using Flask-SQLAlchemy

## Tech Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- SQLite

## Project Structure

```text
Canteen-Management/
├── app.py               # Flask application, models and routes
├── templates/
│   ├── base.html        # Shared layout (header, nav, flash messages)
│   ├── index.html       # Home page
│   ├── created.html     # Coupon / ticket page
│   ├── manage.html      # Staff queue manager
│   ├── display.html     # Live "Now Serving" board
│   └── 404.html
├── static/
│   ├── css/style.css
│   └── js/main.js
├── tests/test_app.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd Canteen-Management
```

2. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS / Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the App

From the project folder, run:

```bash
python app.py
```

Then open the browser at:

```text
http://127.0.0.1:5000/
```

## Running Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | `dev-secret-key` | Flask session signing key — set this in production |
| `DATABASE_URL` | `sqlite:///canteen.db` | SQLAlchemy database URL |
| `FLASK_DEBUG` | `1` | Set to `0` to disable debug mode |

## How It Works

- The app creates a SQLite database file named `canteen.db` automatically.
- The `Coupon` model stores:
  - `id`
  - `number`
  - `customer_name`
  - `status`
  - `created_at`
- A new coupon stores the customer's name and is assigned a number in the format `C00001`.
- Coupons created before names were added have no name and fall back to showing their number.
- Existing `canteen.db` files are upgraded automatically on startup (the `customer_name` column is added).
- The management page lets staff mark coupons as served, undo a serve, or delete them.
- The display board polls `/api/queue` every 5 seconds.

## Routes

- `GET /` - Home page with now serving, stats and the latest coupon
- `POST /create` - Create a new coupon (form field `customer_name`), then redirect to its page
- `GET /coupon/<id>` - View (and print) a coupon
- `GET /manage` - View pending and served coupons
- `POST /manage` - Serve, requeue or delete a coupon
- `GET /display` - Live display board
- `GET /api/queue` - Queue state as JSON

## Notes

This project is intended for local development and is not configured for production deployment. The Flask debug server is used for convenience during development.

## License

This project is provided as-is for educational and development use.
