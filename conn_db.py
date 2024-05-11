import mysql.connector

PATH_TO_FILE = "create_db.sql"

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="my-secret-pw",
    database="test_db"
)

mycursor = mydb.cursor()

for line in open(PATH_TO_FILE):
    mycursor.execute(line)

mydb.commit()
