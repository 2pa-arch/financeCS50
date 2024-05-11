import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="my-secret-pw",
    database="test_db"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM test_table")

myresult = mycursor.fetchall()

for x in myresult:
    print(x)