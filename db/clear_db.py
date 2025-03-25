import os
from getpass import getpass
import psycopg2
from psycopg2 import sql


def clear_db():
    USERNAME = input("Enter your PostgreSQL username: ")
    PASSWORD = getpass("Enter your PostgreSQL password: ")

    os.environ["PGPASSWORD"] = PASSWORD

    db_name = input("Enter the name of the database to clear data from: ")

    conn = None

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=USERNAME,
            host="localhost",
            port="5432",
            password=PASSWORD,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)

        tables = cursor.fetchall()

        if not tables:
            print(f"No tables found in the database {db_name}.")
            return False

        cursor.execute("SET session_replication_role = replica;")

        print(f"Clearing data from all tables in {db_name}...")

        for table in tables:
            table_name = table[0]
            print(f"Clearing data from table: {table_name}")
            cursor.execute(
                sql.SQL("TRUNCATE TABLE {} CASCADE;").format(sql.Identifier(table_name))
            )

        cursor.execute("SET session_replication_role = DEFAULT;")

        print(f"Data cleared successfully from all tables in {db_name}.")

    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

    return True


if __name__ == "__main__":
    clear_db()
