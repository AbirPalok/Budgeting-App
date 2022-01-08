import sqlite3

# Making the connection to the database.
print()
print("****** Connecting to Database.")
connection = sqlite3.connect('user_data.sqlite')
cursor = connection.cursor()
print("****** Database Connected")
print()
print()

