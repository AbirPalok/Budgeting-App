# Built-it Imports
import re
from datetime import date
import os
from hashlib import pbkdf2_hmac

# Module Imports
from database_connection import *


# GLOBAL CONSTANTS
# IND = INDEX
IND_YEAR = 0
IND_MONTH = 1
IND_DAY = 2
SIZE_SALT = 32
ITERATION_HASH = 100_000


# Function: Call this function to create a new account
# Calling this will take neccessary inputs from user and create an account in the database.
# Return Value: None
def create_new():
    print(f"{'*' * 6}", end=" ")
    print("Complete the following form.")

    print(f"{'*' * 6}", end=" ")
    first_name = input("First Name: ")

    print(f"{'*' * 6}", end=" ")
    last_name = input("Last Name: ")

    # Email Validation
    while True:
        # Checking the validity
        print(f"{'*' * 6}", end=" ")
        email = input("Email: ")
        if not re.search("^[a-z0-9]+[a-z0-9.]+@[a-z0-9]+\.[a-z]", email):
            print(f"{'*' * 6}", end=" ")
            print("Invalid email. Please Try Again.")
            continue

        # Duplication Check
        cursor.execute("SELECT COUNT(*) FROM user_info WHERE email = ?", (email,))
        if cursor.fetchone()[0] > 0:
            print(f"{'*' * 6}", end=" ")
            print("Email is already in use! Try again with a different one!")
        else:
            break

    # Password Validation
    while True:
        print(f"{'*' * 6}", end=" ")
        print("Password Requirements: ")

        print(f"{'*' * 6}", end=" ")
        print("1. Must be at least 8 characters long.")

        print(f"{'*' * 6}", end=" ")
        print("2. Must use a Lower case letter.")

        print(f"{'*' * 6}", end=" ")
        print("3. Must use an Upper Case letter.")

        print(f"{'*' * 6}", end=" ")
        print("4. Must use a digit")

        print(f"{'*' * 6}", end=" ")
        print("5. Must use a special character from these: (~ ! @ # $ % ^ & *)")

        print(f"{'*' * 6}", end=" ")
        pwd = input("Enter a password: ")
        if not re.search('^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[~!@#$%^&]).{8,}', pwd):
            print(f"{'*' * 6}", end=" ")
            print("Invalid Password! Please follow all the requirements")
            continue

        # Double checking password
        print(f"{'*' * 6}", end=" ")
        re_pwd = input("Confirm the password: ")
        if pwd != re_pwd:
            print(f"{'*' * 6}", end=" ")
            print("Passwords do not match. Try again!")

        else:
            break

    # Date of Birth Validation
    while True:
        print(f"{'*' * 6}", end=" ")
        dob = input("Enter your date of birth(YYYY-MM-DD): ")
        try:
            dob_list = dob.split('-')
            date(int(dob_list[IND_YEAR]), int(dob_list[IND_MONTH]),
                 int(dob_list[IND_DAY]))
        except:
            print(f"{'*' * 6}", end=" ")
            print("Invalid Date. Please make sure to put a "
                  "correct date in the shown format")
        else:
            break

    if create_new_account(first_name, last_name, email, pwd, dob):
        print(f"{'*' * 6}", end=" ")
        print("Account Successfully Created! You may login now")

    else:
        print(f"{'*' * 6}", end=" ")
        print("Error 404! Something went wrong. Try again later.")


# DO NOT CALL THIS FUNCTION DIRECTLY from a user-end perspective.
# This function creates the account in the database. But this does not interact with the user.
# This function has automatically been called in the "create_new()" function.
# Return Value: None
def create_new_account(first_name, last_name, email, input_pwd, dob):
    try:
        # HASHING the Password
        salt = os.urandom(SIZE_SALT)
        key = pbkdf2_hmac('sha256', input_pwd.encode('UTF-8'), salt, ITERATION_HASH)

        # Joining salt and key into one variable
        pwd = salt + key

        # Data insertion to the Database
        cursor.execute("INSERT INTO "
                       "user_info(first_name, last_name, email, pwd, date_of_birth, balance)"
                       " VALUES(?, ?, ?, ?, ?, ?)",
                       (first_name, last_name, email, pwd, dob, 0))

        # Committing the changes
        connection.commit()
    except:
        return False

    else:
        return True



def test():
    # Test Data
    first_name = "Abir"
    last_name = "Palok"
    email = "pal@gmail.com"
    pwd = "Palok@palok123"
    dob = "2000-01-01"
    bal = 0

    create_new_account(first_name, last_name, email, pwd, dob)



