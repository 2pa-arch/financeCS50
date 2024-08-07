import mysql.connector

PATH_TO_FILE = "create_db.sql"


def check_create_db():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="my-secret-pw"
    )

    mycursor = mydb.cursor()
    with open('create_db.sql', 'r') as sql_file:
        sql_script = sql_file.read()

    sql_commands = sql_script.split(';')

    for command in sql_commands:
        if command.strip():
            try:
                mycursor.execute(command)
            except Exception as e:
                print(f"Помилка при виконанні команди: {command}")
                print(e)

    mydb.commit()
    mydb.close()

if __name__ == "__main__":
    check_create_db()