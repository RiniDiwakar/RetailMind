from database.db import get_db_connection


def save_dataset(filename):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO datasets (filename) VALUES (?)",
        (filename,)
    )

    connection.commit()

    dataset_id = cursor.lastrowid

    connection.close()

    return dataset_id