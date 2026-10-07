import cv2
import face_recognition

from face_model import load_face_encodings
from database import get_student_by_roll, mark_attendance


def start_attendance():

    # Load saved face encodings
    known_faces = load_face_encodings()

    if not known_faces:

        print("No registered faces found.")

        return


    # Roll numbers and face encodings
    known_roll_numbers = list(known_faces.keys())

    known_encodings = list(known_faces.values())


    # Start laptop camera
    camera = cv2.VideoCapture(0)


    if not camera.isOpened():

        print("Camera could not be opened.")

        return


    print("AI Attendance System Started")
    print("Press Q to stop the camera.")


    while True:

        success, frame = camera.read()


        if not success:

            print("Could not read camera.")

            break


        # Reduce image size for faster processing
        small_frame = cv2.resize(
            frame,
            (0, 0),
            fx=0.25,
            fy=0.25
        )


        # OpenCV uses BGR
        # face_recognition uses RGB
        rgb_frame = cv2.cvtColor(
            small_frame,
            cv2.COLOR_BGR2RGB
        )


        # Detect faces
        face_locations = face_recognition.face_locations(
            rgb_frame
        )


        # Create encodings for detected faces
        face_encodings = face_recognition.face_encodings(
            rgb_frame,
            face_locations
        )


        # Check every detected face
        for face_encoding, location in zip(
            face_encodings,
            face_locations
        ):


            matches = face_recognition.compare_faces(
                known_encodings,
                face_encoding,
                tolerance=0.5
            )


            name = "Unknown"


            if True in matches:

                face_distances = face_recognition.face_distance(
                    known_encodings,
                    face_encoding
                )


                best_match_index = face_distances.argmin()


                if matches[best_match_index]:

                    roll_number = known_roll_numbers[
                        best_match_index
                    ]

                    name = roll_number


                    # Find student in database
                    student = get_student_by_roll(
                        roll_number
                    )


                    if student:

                        # Mark attendance
                        mark_attendance(
                            student["id"]
                        )

                        print(
                            "Attendance marked for:",
                            student["name"]
                        )


            # Face coordinates
            top, right, bottom, left = location


            # Scale coordinates back
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4


            # Draw rectangle
            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                (0, 255, 0),
                2
            )


            # Display name / roll number
            cv2.putText(
                frame,
                name,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )


        # Show camera window
        cv2.imshow(
            "AI Smart Attendance",
            frame
        )


        # Press Q to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":

    start_attendance()
