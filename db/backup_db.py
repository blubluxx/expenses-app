from getpass import getpass
import subprocess
import os
from datetime import datetime


def backup_database():
    backup_folder = os.path.join(os.getcwd(), "db", "backups")
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_filename = f"expenses_app_backup_{timestamp}.sql"

    backup_filepath = os.path.join(backup_folder, backup_filename)

    print(f"Backup file will be created at: {backup_filepath}")

    USERNAME = input("Enter your PostgreSQL username: ")
    PASSWORD = getpass("Enter your PostgreSQL password: ")

    os.environ["PGPASSWORD"] = PASSWORD

    pg_dump_command = [
        "pg_dump",
        "--format=c",
        "--file",
        backup_filepath,
        "--username",
        USERNAME,
        "--host",
        "localhost",
        "--port",
        "5432",
        "expenses-app",
    ]

    try:
        subprocess.run(pg_dump_command, check=True)
        print(f"Backup completed successfully! Backup file: {backup_filepath}")
    except subprocess.CalledProcessError as e:
        print(f"Error during backup: {e}")
        return False

    return True


if __name__ == "__main__":
    backup_database()
