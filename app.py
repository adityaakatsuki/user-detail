from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "users.db"

app = Flask(__name__)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                address TEXT,
                role TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "phone": row["phone"],
        "address": row["address"] or "",
        "role": row["role"],
        "notes": row["notes"] or "",
        "created_at": row["created_at"],
    }


def validate_payload(data: dict[str, Any]) -> tuple[bool, str]:
    required_fields = ["full_name", "email", "phone", "role"]
    for field in required_fields:
        if not str(data.get(field, "")).strip():
            return False, f"{field.replace('_', ' ').title()} is required."

    if not EMAIL_PATTERN.match(str(data.get("email", "")).strip()):
        return False, "Please enter a valid email address."

    phone = str(data.get("phone", "")).strip()
    if len(phone) < 7 or len(phone) > 15 or not re.match(r"^[0-9+\-\s()]+$", phone):
        return False, "Please enter a valid phone number."

    return True, ""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/users", methods=["GET"])
def list_users():
    search = request.args.get("search", "").strip()
    with get_connection() as conn:
        if search:
            pattern = f"%{search}%"
            rows = conn.execute(
                """
                SELECT * FROM users
                WHERE full_name LIKE ? OR email LIKE ? OR phone LIKE ? OR role LIKE ?
                ORDER BY id DESC
                """,
                (pattern, pattern, pattern, pattern),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    return jsonify([row_to_dict(row) for row in rows])


@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}
    valid, message = validate_payload(data)
    if not valid:
        return jsonify({"error": message}), 400

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users (full_name, email, phone, address, role, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    data["full_name"].strip(),
                    data["email"].strip().lower(),
                    data["phone"].strip(),
                    str(data.get("address", "")).strip(),
                    data["role"].strip(),
                    str(data.get("notes", "")).strip(),
                ),
            )
            conn.commit()
            user_id = cursor.lastrowid
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return jsonify(row_to_dict(row)), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "A user with this email already exists."}), 409


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id: int):
    data = request.get_json(silent=True) or {}
    valid, message = validate_payload(data)
    if not valid:
        return jsonify({"error": message}), 400

    try:
        with get_connection() as conn:
            existing = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
            if not existing:
                return jsonify({"error": "User not found."}), 404

            conn.execute(
                """
                UPDATE users
                SET full_name = ?, email = ?, phone = ?, address = ?, role = ?, notes = ?
                WHERE id = ?
                """,
                (
                    data["full_name"].strip(),
                    data["email"].strip().lower(),
                    data["phone"].strip(),
                    str(data.get("address", "")).strip(),
                    data["role"].strip(),
                    str(data.get("notes", "")).strip(),
                    user_id,
                ),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return jsonify(row_to_dict(row))
    except sqlite3.IntegrityError:
        return jsonify({"error": "A user with this email already exists."}), 409


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    if cursor.rowcount == 0:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"message": "User deleted successfully."})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
