from flask import Flask, render_template, request, redirect

from database import (
    add_student,
    get_students,
    get_attendance
)

from face_model import create_face_encoding

import cv2
import os


app = Flask(__name__)


@app.route("/")
def home():

    students = get_students()

    return render_template(
        "index.html",
        students=students
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]

        roll_no = request.form["roll_no"]


        try:

            add_student(
                name,
                roll_no
            )

            capture_face(
                roll_no
            )

            create_face_encoding(
                roll_no
            )

            return redirect("/")


        except Exception as error:

            return f"Error: {error}"


    return render_template(
        "register.html"
    )


@app.route("/attendance")
def attendance():

    records = get_attendance()

    return render_template(
        "attendance.html",
        records=records
    )


@app.route("/start")
def start_attendance():

    from attendance import start_attendance

    start_attendance()

    return redirect("/attendance")


def capture_face(roll_no):

    folder = os.path.join(
        "dataset",
        roll_no
    )


    os.makedirs(
        folder,
        exist_ok=True
    )


    camera = cv2.VideoCapture(0)


    if not camera.isOpened():

        raise Exception(
            "Camera could not be opened."
        )


    count = 0


    print("Face capture started.")

    print("Press S to capture photo.")

    print("Press Q to stop.")


    while count < 5:

        success, frame = camera.read()


        if not success:

            break


        cv2.imshow(
            "Capture Student Face",
            frame
        )


        key = cv2.waitKey(1) & 0xFF


        if key == ord("s"):

            file_path = os.path.join(
                folder,
                f"{count + 1}.jpg"
            )


            cv2.imwrite(
                file_path,
                frame
            )


            count += 1


            print(
                f"Photo {count}/5 saved."
            )


        elif key == ord("q"):

            break


    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":

    app.run(
        debug=True
    )
