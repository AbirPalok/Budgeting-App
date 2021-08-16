import stdiomask
import re
import sys
import sqlite3
from hashlib import pbkdf2_hmac
from datetime import date

# Modules
from database_connection import *

# GLOBAL CONSTANTS
INDEX_FETCH_FIRST_NAME = 0
INDEX_FETCH_LAST_NAME = 1
INDEX_FETCH_EMAIL = 2
INDEX_FETCH_PWD = 3
INDEX_FETCH_DOB = 4
INDEX_FETCH_BAL = 5
INDEX_FETCH_ROWID = 6
INDEX_FETCH_LAST_TRXID = 0
INDEX_MONTH = 1

INDEX_FETCH_TRANSACTION_TYPE = 2

SIZE_SALT = 32
SIZE_KEY = 32
ITERATION_HASH = 100_000

# In the database, income is represented as 1 and expense is represented as 0
TYPE_INCOME = 1
TYPE_EXPENSE = 0

STATEMENT_PREV_MONTH = 0
STATEMENT_THIS_MONTH = 1
STATEMENT_TYPE_INCOME = 1
STATEMENT_TYPE_EXPENSE = 2
STATEMENT_TYPE_ALL = 3




class User:
    def __init__(self):
        print()
        print("****** Connecting to Database.")
        connection = sqlite3.connect('user_data.sqlite')
        cursor = connection.cursor()
        print("****** Database Connected")
        print()
        print()

        self.login_status = False
        self.user_id = None
        self.first_name = None
        self.last_name = None
        self.email = None
        self.dob = None
        self.balance = None

    def login(self):
        print("Login: ")

        # Email Validation
        while True:
            print(f"{'*' * 6}", end=" ")
            login_email = input("Email: ")
            if re.search("^[a-z0-9]+[a-z0-9.]+@[a-z0-9]+\.[a-z]", login_email):
                break

            print(f"{'*' * 6}", end=" ")
            print("Invalid email. Please Try Again.")

        if sys.stdin.isatty():
            print(f"{'*' * 6}", end=" ")
            login_pwd = stdiomask.getpass("Password: ", mask="*")
        else:
            print(f"{'*' * 6}", end=" ")
            login_pwd = input("Password: ")

        cursor.execute('SELECT *, rowid FROM user_info WHERE email = ?', (login_email,))
        res = cursor.fetchone()

        # Email Existence Lookup
        if type(res) == type(None):
            print(f"{'*' * 6}", end=" ")
            print("Login Failed! Incorrect Email or Password.")
            return False

        # Getting password key from Database
        pwd = res[INDEX_FETCH_PWD]
        salt = pwd[:SIZE_SALT]
        key = pwd[SIZE_KEY:]

        # Making Key with same salt for the login password
        login_key = pbkdf2_hmac('sha256', login_pwd.encode('UTF-8'),
                                salt, ITERATION_HASH)

        # Password Check
        if key != login_key:
            print(f"{'*' * 6}", end=" ")
            print("Login Failed! Incorrect Email or Password.")
            return False

        print(f"{'*' * 6}", end=" ")
        print("Login was Successful")
        self.user_id = res[INDEX_FETCH_ROWID]
        self.first_name = res[INDEX_FETCH_FIRST_NAME]
        self.last_name = res[INDEX_FETCH_LAST_NAME]
        self.email = res[INDEX_FETCH_EMAIL]
        self.dob = res[INDEX_FETCH_DOB]
        self.balance = res[INDEX_FETCH_BAL]
        self.login_status = True
        return True

    def add_income(self):
        print(f"{'*' * 40}")
        print(f"{'*'*6}{'ADD INCOME':^28}{'*'*6}")
        print(f"{'*' * 40}")

        print(f"{'*' * 6}", end=" ")
        print("Enter the following information.")
        while True:
            print(f"{'*' * 6}", end=" ")
            src = input("Source of Income: ")
            if re.search('.+', src):
                break
            print(f"{'*' * 6}", end=" ")
            print("Error! Source cannot be empty.")


        # Amount Validation
        while True:
            print(f"{'*' * 6}", end=" ")
            amnt = input("Amount: ")
            try:
                amnt = abs(float(amnt))
            except ValueError:
                print(f"{'*' * 6}", end=" ")
                print("Invalid Amount! Please try again with a valid amount.")
            else:
                break

        print(f"{'*' * 6}", end=" ")
        des = input("Description (Optional! Hit Enter to Continue): ")

        try:
            cursor.execute("SELECT trxid FROM ledger ORDER BY trxid DESC LIMIT 1")

            # Generating the new TrxID by adding one to the last TrxID
            trxid = cursor.fetchone()[INDEX_FETCH_LAST_TRXID] + 1

            cursor.execute("INSERT INTO ledger(user_info_rowid, trxid, type, name, category, amount, entry_date, description) "
                           "VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                           (self.user_id, trxid, TYPE_INCOME, src, src, amnt, date.today(), des))

            self.balance += amnt

            cursor.execute("UPDATE user_info SET balance = ? WHERE rowid = ? ", (self.balance, self.user_id))

            connection.commit()

        except:
            print(f"{'*' * 6}", end=" ")
            print("Failed to insert the transaction! Try Again Later.")
        else:
            print(f"{'*' * 6}", end=" ")
            print("Transaction Successfully Inserted!")

    def add_expense(self):
        print(f"{'*' * 40}")
        print(f"{'*' * 6}{'ADD EXPENSE':^28}{'*' * 6}")
        print(f"{'*' * 40}")

        print(f"{'*' * 6}", end=" ")
        print("Enter the following information.")
        while True:
            print(f"{'*' * 6}", end=" ")
            name = input("Name of Expense: ")

            if re.search('.+', name):
                break

            print(f"{'*' * 6}", end=" ")
            print("Error! Name cannot be empty.")

        while True:
            print(f"{'*' * 6}", end=" ")
            category = input("Category of Expense: ")
            if re.search('.+', category):
                break

            print(f"{'*' * 6}", end=" ")
            print("Error! Category cannot be empty.")

        # Amount Validation
        while True:
            print(f"{'*' * 6}", end=" ")
            amnt = input("Amount: ")
            try:
                amnt = abs(float(amnt))
            except ValueError:
                print(f"{'*' * 6}", end=" ")
                print("Invalid Amount! Please try again with a valid amount.")
            else:
                break

        print(f"{'*' * 6}", end=" ")
        des = input("Description (Optional! Hit Enter to Continue): ")

        try:
            # Generating the new TrxID by adding one to the last TrxID
            cursor.execute("SELECT trxid FROM ledger ORDER BY trxid DESC LIMIT 1")
            trxid = cursor.fetchone()[INDEX_FETCH_LAST_TRXID] + 1

            # Inserting data into the Database
            cursor.execute("INSERT INTO ledger(user_info_rowid, trxid, type, name, category, amount, entry_date, description) "
                           "VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                           (self.user_id, trxid, TYPE_EXPENSE, name, category, amnt, date.today(), des))

            # Changing the balance of the user
            self.balance -= amnt
            cursor.execute("UPDATE user_info SET balance = ? WHERE rowid = ? ", (self.balance, self.user_id))
            connection.commit()

        except:
            print(f"{'*' * 6}", end=" ")
            print("Failed to insert the transaction! Try Again Later.")
        else:
            print(f"{'*' * 6}", end=" ")
            print("Transaction Successfully Inserted!")


    def view_statement(self, statement_time, statement_type):

        # Numeric Value of this month
        month = str(date.today()).split('-')[INDEX_MONTH]
        if statement_time == STATEMENT_PREV_MONTH:
            month = "0" + str(int(month)-1)

        # For Printing the Month
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                  "November", "December"]

        # Upper and lower bound of the date.
        date_lower_bound = "2021-" + month + "-01"
        date_upper_bound = "2021-" + month + "-31"

        # Getting the Statement data from the database
        if statement_type == STATEMENT_TYPE_ALL:
            # Statement for all transactions
            cursor.execute("SELECT * "
                           "FROM ledger "
                           "WHERE (user_info_rowid = ?) AND "
                           "(entry_date >= ? AND  entry_date <= ?)",
                           (self.user_id, date_lower_bound, date_upper_bound))
        elif statement_type == STATEMENT_TYPE_INCOME:
            # Statement for only income
            cursor.execute("SELECT * "
                           "FROM ledger "
                           "WHERE (user_info_rowid = ?) AND"
                           "(type = ?) AND"
                           "(entry_date >= ? AND  entry_date <= ?)",
                           (self.user_id, TYPE_INCOME, date_lower_bound, date_upper_bound))
        elif statement_type == STATEMENT_TYPE_EXPENSE:
            # Statement for only expense
            cursor.execute("SELECT * "
                           "FROM ledger "
                           "WHERE (user_info_rowid = ?) AND"
                           "(type = ?) AND"
                           "(entry_date >= ? AND  entry_date <= ?)",
                           (self.user_id, TYPE_EXPENSE, date_lower_bound, date_upper_bound))


        # Converting statement to a readable dictionary format
        statement = []
        for item in cursor.fetchall():
            temp_dict = {}
            temp_dict['TrxID'] = item[1]
            temp_dict['Transaction_Type'] = item[2]
            if item[2] == TYPE_INCOME:
                temp_dict['Name'] = "N/A"
                temp_dict['Type'] = "N/A"
                temp_dict['Source'] = item[3]
            elif item[2] == TYPE_EXPENSE:
                temp_dict['Name'] = item[3]
                temp_dict['Type'] = item[4]
                temp_dict['Source'] = "N/A"
            temp_dict['Amount'] = item[5]
            temp_dict['Date'] = item[6]
            temp_dict['Description'] = item[7]

            statement.append(temp_dict)

        # Reversing so that the order of transaction can be latest to oldest
        statement.reverse()

        return statement, months, month

    def view_statement_all(self, month):
        if self.login_status == False:
            print("Error! It looks like your not logged in.")
            return False
        if month == STATEMENT_THIS_MONTH:
            statement, months, month_num = self.view_statement(STATEMENT_THIS_MONTH, STATEMENT_TYPE_ALL)
        elif month == STATEMENT_PREV_MONTH:
            statement, months, month_num = self.view_statement(STATEMENT_PREV_MONTH, STATEMENT_TYPE_ALL)


        # Printing Statement
        print(f"{'*'*40}")
        print(f"{'*' * 6}{'MONTHLY STATEMENT':^28}{'*' * 6}")
        print(f"{'*'*40}")
        print(f"Statement Type: All Transactions")
        print(f"Name: {self.first_name} {self.last_name}")
        print(f"Month: {months[int(month_num)-1]}")
        print(f"{'='*95}")
        print(f"{'Transaction ID':<18}{'Name':<15}  {'Category':<15}  {'Source: ':<15}  {'Date':<15}  {'Amount':>8}")
        total = 0
        for item in statement:
            print(f"{item['TrxID']:<18}{item['Name']:<15}  {item['Type']:<15}  {item['Source']:<15}  "
                  f"{item['Date']:<15}  "
                  f"{-1 * item['Amount'] if item['Transaction_Type'] == TYPE_EXPENSE else item['Amount']:>8.2f}")
            if item['Transaction_Type'] == TYPE_INCOME:
                total += float(item['Amount'])
            elif item['Transaction_Type'] == TYPE_EXPENSE:
                total -= float(item['Amount'])

        print(f"{'='*95}")
        print(f"Total{' '*79}  {total:>8.2f}")

        print()
        print()
        return True

    def view_statement_income(self, month):
        if self.login_status == False:
            print("Error! It looks like your not logged in.")
            return False
        if month == STATEMENT_THIS_MONTH:
            statement, months, month_num = self.view_statement(STATEMENT_THIS_MONTH, STATEMENT_TYPE_INCOME)
        elif month == STATEMENT_PREV_MONTH:
            statement, months, month_num = self.view_statement(STATEMENT_PREV_MONTH, STATEMENT_TYPE_INCOME)


        # Printing Statement
        print(f"{'*'*40}")
        print(f"{'*' * 6}{'MONTHLY STATEMENT':^28}{'*' * 6}")
        print(f"{'*'*40}")
        print(f"Name: {self.first_name} {self.last_name}")
        print(f"Month: {months[int(month_num)-1]}")
        print(f"Statement Type: Income")
        print(f"{'='*63}")
        print(f"{'Transaction ID':<18}  {'Source: ':<15}  {'Date':<15}  {'Amount':>8}")
        total = 0
        for item in statement:
            print(f"{item['TrxID']:<18}  {item['Source']:<15}  "
                  f"{item['Date']:<15}  {item['Amount']:>8.2f}")
            total += float(item['Amount'])

        print(f"{'='*63}")
        print(f"Total{' '*47}  {total:>8.2f}")

        print()
        print()
        return True

    def view_statement_expense(self, month):
        if not self.login_status:
            print("Error! It looks like your not logged in.")
            return False

        if month == STATEMENT_THIS_MONTH:
            statement, months, month_num = self.view_statement(STATEMENT_THIS_MONTH, STATEMENT_TYPE_EXPENSE)
        elif month == STATEMENT_PREV_MONTH:
            statement, months, month_num = self.view_statement(STATEMENT_PREV_MONTH, STATEMENT_TYPE_EXPENSE)

        # Printing Statement
        print(f"{'*'*40}")
        print(f"{'*' * 6}{'MONTHLY STATEMENT':^28}{'*' * 6}")
        print(f"{'*'*40}")
        print(f"Name: {self.first_name} {self.last_name}")
        print(f"Month: {months[int(month_num)-1]}")
        print(f"Statement Type: Expense")
        print(f"{'='*78}")
        print(f"{'Transaction ID':<18}{'Name':<15}  {'Category':<15}  {'Date':<15}  {'Amount':>8}")
        total = 0
        for item in statement:
            print(f"{item['TrxID']:<18}{item['Name']:<15}  {item['Type']:<15}  "
                  f"{item['Date']:<15}  {item['Amount']:>8.2f}")
            total += float(item['Amount'])

        print(f"{'='*78}")
        print(f"Total{' '*62}  {total:>8.2f}")

        print()
        print()
        return True

    def transition_lookup(self):
        if not self.login_status:
            print("Error! It looks like your not logged in.")
            return False

        TrxID = input("Enter Transaction ID: ")
        try:
            TrxID = int(TrxID)

        except ValueError:
            print("Enter a Valid TrxID")
            return False
        else:
            if len(str(TrxID)) != 9:
                print("Enter a Valid TrxID")
                return False
            TrxID = int(TrxID)

        cursor.execute("SELECT * FROM ledger WHERE trxid = ?", (TrxID,))

        transaction = cursor.fetchone()
        if transaction == None:
            print("Transaction could not be found. Try again with a different Transaction ID")
            return False

        elif transaction[0] != self.user_id:
            print("Transaction could not be found. Try again with a different Transaction ID")
            return False

        if transaction[INDEX_FETCH_TRANSACTION_TYPE] == TYPE_INCOME:
            print()
            print()
            print(f"{'*' * 40}")
            print(f"{'*' * 6}{'TRANSACTION LOOKUP':^28}{'*' * 6}")
            print(f"{'*' * 40}")
            print(f"Name: {self.first_name} {self.last_name}")
            print(f"Statement Type: Income")
            print(f"{'=' * 63}")
            print(f"{'Transaction ID':<18}  {'Source: ':<15}  {'Date':<15}  {'Amount':>8}")
            print(f"{transaction[1]:<18}  {transaction[3]:<15}  "
                  f"{transaction[6]:<15}  {transaction[5]:>8.2f}")
            print(f"{'=' * 63}")

        else:
            print(f"{'*' * 40}")
            print(f"{'*' * 6}{'TRANSACTION LOOKUP':^28}{'*' * 6}")
            print(f"{'*' * 40}")
            print(f"Name: {self.first_name} {self.last_name}")
            print(f"Statement Type: Expense")
            print(f"{'=' * 78}")
            print(f"{'Transaction ID':<18}{'Name':<15}  {'Category':<15}  {'Date':<15}  {'Amount':>8}")
            print(f"{transaction[1]:<18}{transaction[3]:<15}  {transaction[4]:<15}  "
                  f"{transaction[6]:<15}  {transaction[5]:>8.2f}")
            print(f"{'=' * 78}")

        return True






# # Test Data
# demo = User()
# demo.user_id = 3
# demo.first_name = "Abir"
# demo.last_name = "Palok"
# demo.email = "pal@gmail.com"
# demo.dob ="2000-04-05"
# demo.balance = 0
# demo.login_status = True
#
# demo.view_statement_all(STATEMENT_THIS_MONTH)
# demo.view_statement_income(STATEMENT_THIS_MONTH)
# demo.view_statement_expense(STATEMENT_THIS_MONTH)



