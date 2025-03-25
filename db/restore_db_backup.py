import subprocess
import os
from getpass import getpass


def restore_database():
    USERNAME = input("Enter your PostgreSQL username: ")
    PASSWORD = getpass("Enter your PostgreSQL password: ")

    os.environ["PGPASSWORD"] = PASSWORD

    backup_folder = os.path.join(os.getcwd(), "db", "backups")
    backup_filename = input(
        f"Enter the name of the backup file to restore (from {backup_folder}): "
    )
    backup_filepath = os.path.join(backup_folder, backup_filename)

    if not os.path.exists(backup_filepath):
        print(f"Backup file not found: {backup_filepath}")
        return False

    db_name = input("Enter the name of the database to restore to: ")

    print(f"Restoring backup from: {backup_filepath} to database: {db_name}")

    pg_restore_command = [
        "pg_restore",
        "--username",
        USERNAME,
        "--host",
        "localhost",
        "--port",
        "5432",
        "--dbname",
        db_name,
        "--clean",
        "--format=c",
        backup_filepath,
    ]

    try:
        subprocess.run(pg_restore_command, check=True)
        print(f"Restore completed successfully! Database {db_name} has been restored.")
    except subprocess.CalledProcessError as e:
        print(f"Error during restore: {e}")
        return False

    return True


if __name__ == "__main__":
    restore_database()
