# User Details Manager

A simple full-stack application to store user details in a database using a frontend form.

## Features

- Add user details from a frontend form
- Store records in a SQLite database
- View all stored users in a table
- Search users by name, email, phone, or role
- Edit existing user records
- Delete user records
- Basic client-side and server-side validation
- Responsive UI

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python Flask
- Database: SQLite

## Project Structure

```text
user_details_app/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## How to Run

### 1. Open terminal in the project folder

```bash
cd user_details_app
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

On Windows:

```bash
venv\Scripts\activate
```

On Linux/macOS:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

### 6. Open in browser

```text
http://127.0.0.1:5000
```

The `users.db` SQLite database file will be created automatically when the application starts.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/users` | Get all users |
| GET | `/api/users?search=text` | Search users |
| POST | `/api/users` | Create a user |
| PUT | `/api/users/<id>` | Update a user |
| DELETE | `/api/users/<id>` | Delete a user |

## Sample User Fields

- Full Name
- Email
- Phone
- Role
- Address
- Notes
