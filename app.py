from flask import Flask, render_template, request, redirect, url_for, flash
import cv2
import os
import sqlite3

from database import (
    add_student,
    get_students,
    get_attendance,
    get_student_by_roll,
)

app = Flask(__name__)
app.secret_key = "attendance-project-local-key"


# ---------------- HOME / DASHBOARD ----------------

@app.route("/")
def home():
    students = get_students()
    return render_template("index.html", students=students)


# ---------------- STUDENT REGISTRATION ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        roll_no = request.form.get("roll_no", "").strip()

        if not name or not roll_no:
            flash(
                "Please enter both student name and roll number.",
                "error"
            )
            return redirect(url_for("register"))

        # Check if roll number already exists
        try:
            existing_student = get_student_by_roll(roll_no)

            if existing_student is not None:
                flash(
                    f"Roll number '{roll_no}' is already registered.",
                    "error"
                )
                return redirect(url_for("register"))

        except sqlite3.Error:
            app.logger.exception("Could not check student record")

            flash(
                "Database error while checking the roll number.",
                "error"
            )
            return redirect(url_for("register"))

        # Capture face and create encoding
        try:
            capture_face(roll_no)

            from face_model import create_face_encoding

            success = create_face_encoding(roll_no)

            if not success:
                raise RuntimeError(
                    "Face encoding failed. Please capture clear face photos."
                )

        except Exception:
            app.logger.exception(
                "Face capture or encoding failed for %s",
                roll_no
            )

            flash(
                "Face capture or encoding failed. "
                "Please check the VS Code terminal for details.",
                "error"
            )
            return redirect(url_for("register"))

        # Save student after successful encoding
        try:
            add_student(name, roll_no)

        except sqlite3.IntegrityError:
            flash(
                f"Roll number '{roll_no}' is already registered.",
                "error"
            )
            return redirect(url_for("register"))

        except sqlite3.Error:
            app.logger.exception("Could not save student")

            flash(
                "Student could not be saved because of a database error.",
                "error"
            )
            return redirect(url_for("register"))

        flash(
            f"Registration successful! Student: {name}, "
            f"Roll No: {roll_no}",
            "success"
        )

        return redirect(url_for("home"))

    return render_template("register.html")


# ---------------- ATTENDANCE RECORDS ----------------

@app.route("/attendance")
def attendance():

    records = get_attendance()

    return render_template(
        "attendance.html",
        records=records
    )


# ---------------- START AI ATTENDANCE ----------------

@app.route("/start")
def start_attendance_route():

    try:
        from attendance import start_attendance

        start_attendance()

    except Exception:
        app.logger.exception("Could not start AI attendance")

        return (
            "Unable to start AI attendance. "
            "Please check the VS Code terminal for details."
        ), 500

    return redirect(url_for("attendance"))


# ---------------- FACE CAPTURE FUNCTION ----------------

def capture_face(roll_no):

    folder = os.path.join("dataset", roll_no)
    os.makedirs(folder, exist_ok=True)

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        camera.release()

        raise RuntimeError(
            "Camera could not be opened. Please check camera permissions."
        )

    count = 0

    try:
        print("\nFace capture started.")
        print("Click the camera window, then press S to save a photo.")
        print("Press Q to stop capturing.")
        print("Please capture 5 photos.\n")

        while count < 5:

            success, frame = camera.read()

            if not success:
                raise RuntimeError(
                    "Could not read a frame from the camera."
                )

            cv2.imshow("Capture Student Face", frame)

            key = cv2.waitKey(1) & 0xFF

            if key in (ord("s"), ord("S")):

                file_path = os.path.join(
                    folder,
                    f"{count + 1}.jpg"
                )

                saved = cv2.imwrite(file_path, frame)

                if saved:
                    count += 1
                    print(f"Photo {count}/5 saved successfully.")

                else:
                    raise RuntimeError(
                        "Could not save the captured photo."
                    )

            elif key in (ord("q"), ord("Q")):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

    if count < 5:
        raise RuntimeError(
            f"Only {count} photo(s) captured. "
            "Please register again and capture all 5 photos."
        )

    print("All 5 face photos captured successfully.")


# ---------------- RUN FLASK APPLICATION ----------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )