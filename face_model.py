import os
import pickle
import face_recognition


# Folder where student photos are stored
DATASET_FOLDER = "dataset"

# File where face encodings will be saved
ENCODING_FILE = "encodings/face_encodings.pkl"


def create_face_encoding(roll_no):

    student_folder = os.path.join(
        DATASET_FOLDER,
        roll_no
    )

    # Check student folder
    if not os.path.exists(student_folder):

        print("Student folder not found.")

        return False


    face_encoding = None


    # Read student images
    for file_name in os.listdir(student_folder):

        image_path = os.path.join(
            student_folder,
            file_name
        )

        try:

            image = face_recognition.load_image_file(
                image_path
            )

            face_locations = face_recognition.face_locations(
                image
            )

            # No face detected
            if len(face_locations) == 0:

                continue


            encodings = face_recognition.face_encodings(
                image,
                face_locations
            )


            if encodings:

                face_encoding = encodings[0]

                break


        except Exception as error:

            print(
                "Error reading image:",
                error
            )


    # Face not found
    if face_encoding is None:

        print("No face detected.")

        return False


    # Create encodings folder
    os.makedirs(
        "encodings",
        exist_ok=True
    )


    # Load existing encodings
    data = {}

    if os.path.exists(ENCODING_FILE):

        with open(
            ENCODING_FILE,
            "rb"
        ) as file:

            data = pickle.load(file)


    # Save face encoding
    data[roll_no] = face_encoding


    with open(
        ENCODING_FILE,
        "wb"
    ) as file:

        pickle.dump(
            data,
            file
        )


    print(
        "Face encoding created successfully for:",
        roll_no
    )

    return True


def load_face_encodings():

    # If encoding file doesn't exist
    if not os.path.exists(ENCODING_FILE):

        return {}


    with open(
        ENCODING_FILE,
        "rb"
    ) as file:

        data = pickle.load(file)


    return data
