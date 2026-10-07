import sqlite3
from datetime import datetime

DATABASE = "attendance.db"


def connect_database():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():

    connection = connect_database()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(student_id, date)
        )
    """)

    connection.commit()
    connection.close()


def add_student(name, roll_no):

    connection = connect_database()

    connection.execute(
        """
        INSERT INTO students (name, roll_no)
        VALUES (?, ?)
        """,
        (name, roll_no)
    )

    connection.commit()
    connection.close()


def get_students():

    connection = connect_database()

    students = connection.execute(
        "SELECT * FROM students ORDER BY name"
    ).fetchall()

    connection.close()

    return students


def get_student_by_roll(roll_no):

    connection = connect_database()

    student = connection.execute(
        """
        SELECT * FROM students
        WHERE roll_no = ?
        """,
        (roll_no,)
    ).fetchone()

    connection.close()

    return student


def mark_attendance(student_id):

    current_time = datetime.now()

    date = current_time.strftime("%Y-%m-%d")
    time = current_time.strftime("%H:%M:%S")

    connection = connect_database()

    connection.execute(
        """
        INSERT OR IGNORE INTO attendance
        (student_id, date, time, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            student_id,
            date,
            time,
            "Present"
        )
    )

    connection.commit()
    connection.close()


def get_attendance():

    connection = connect_database()

    records = connection.execute(
        """
        SELECT
            students.name,
            students.roll_no,
            attendance.date,
            attendance.time,
            attendance.status

        FROM attendance

        JOIN students
        ON attendance.student_id = students.id

        ORDER BY
            attendance.date DESC,
            attendance.time DESC
        """
    ).fetchall()

    connection.close()

    return records


create_tables()

