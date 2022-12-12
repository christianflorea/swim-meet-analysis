import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="SQL_Password_123",
    database="swimming_rankings"
)


# create_table = """CREATE TABLE OUA_2022_events (
#     Event varchar(255),
#     Gender varchar(255),
#     Place varchar(255),
#     Name varchar(255),
#     YOB varchar(255),
#     Country varchar(255),
#     Team varchar(255),
#     Time varchar(255),
#     FINAPoints varchar(255)
# );
# """

cursor = db.cursor()
print(cursor)


# def add_to_db(data: list):
#     insert = f"INSERT INTO table_name VALUES ({data[0]}, {data[1]}, {data[2]}, {data[3]}, {data[4]}, {data[5]}, {data[6]}, {data[7]}, {data[8]});"
#     try:
#         cursor.execute(insert)
#     except Exception as exc:
#         print(f"Database write error:: {type(exc).__name__} error - {exc}")
