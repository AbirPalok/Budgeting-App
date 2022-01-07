try:
    # Necessary Imports 3rd Party imports.
    import stdiomask
except:
    # Installing required Packages.
    import install_requirements

# Built-in Imports
import re
import sys
import smtplib, ssl
from hashlib import pbkdf2_hmac
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Modules
from database_connection import *

# GLOBAL CONSTANTS
# These are mostly numbers that looks like just random in the code.
# So, I put them in meaningful names so that they make sense in the context and don't just appear to
# be random numbers. The way they are setup is: CATEGORY_COMMAND_SPECIFIC_DETAILS.

# Indices of different data after the fetch command
INDEX_FETCH_FIRST_NAME = 0
INDEX_FETCH_LAST_NAME = 1
INDEX_FETCH_EMAIL = 2
INDEX_FETCH_PWD = 3
INDEX_FETCH_DOB = 4
INDEX_FETCH_BAL = 5
INDEX_FETCH_ROWID = 6
INDEX_FETCH_LAST_TRXID = 0

INDEX_DATE_MONTH = 1
INDEX_DATE_YEAR = 0

INDEX_FETCH_TRANSACTION_TYPE = 2

# Hashing Constants
SIZE_SALT = 32
SIZE_KEY = 32
ITERATION_HASH = 100_000

# In the database, income is represented as 1, and expense is represented as 0
TYPE_INCOME = 1
TYPE_EXPENSE = 0

# Months and Types of statement is also put in constant forms
STATEMENT_PREV_MONTH = 0
STATEMENT_THIS_MONTH = 1
STATEMENT_TYPE_INCOME = 1
STATEMENT_TYPE_EXPENSE = 2
STATEMENT_TYPE_ALL = 3

# Information to send emails:
with open('email_info.config', 'r') as file:
    # Email
    tmp = file.readlines()
    sender_email = tmp[0].split('=')[1]

    # Password
    password = tmp[1].split('=')[1]

    # SMTP Server
    smtp_server = tmp[2].split('=')[1]

    # SSL Port
    port = int(tmp[3].split('=')[1])



# This class maintains the active user. Any thing a user performs(Add expense, Add income, View Statement)
# will be performed through this class
class User:
    def __init__(self):
        # print()
        # print("****** Connecting to Database.")
        # # connection = sqlite3.connect('user_data.sqlite')
        # # cursor = connection.cursor()
        # print("****** Database Connected")
        # print()
        # print()

        # Keeps track of whether the person running the app is logged in or not.
        self.login_status = False

        # Basic User information
        self.user_id = None
        self.first_name = None
        self.last_name = None
        self.email = None
        self.dob = None
        self.balance = None

    # Methode: Login.
    # This method is used to log the user in.
    def login(self):
        print("Login: ")

        # Email Validation
        while True:
            print(f"{'*' * 6}", end=" ")
            login_email = input("Email: ")

            # Using Regular Expression to check whether the email is a valid email.
            if re.search("^[a-z0-9]+[a-z0-9.]+@[a-z0-9]+\.[a-z]", login_email):
                break

            print(f"{'*' * 6}", end=" ")
            print("Invalid email. Please Try Again.")

        # Masking the password with '*' so that the password is not visible when typing.
        # IDLE doesn't support the stdiomask function, so I had to make a logic statement to tell the program
        # not to mask when using IDLE.

        if sys.stdin.isatty():
            print(f"{'*' * 6}", end=" ")
            login_pwd = stdiomask.getpass("Password: ", mask="*")
        else:
            print(f"{'*' * 6}", end=" ")
            login_pwd = input("Password: ")

        # Looking for the email in the database.
        cursor.execute('SELECT *, rowid FROM user_info WHERE email = ?', (login_email,))
        res = cursor.fetchone()

        # If Email doesn't exist:
        if res is None:
            print(f"{'*' * 6}", end=" ")
            print("Login Failed! Incorrect Email or Password.")
            return False

        # Getting password key from Database
        # The format of the saved password: SaltKey
        pwd = res[INDEX_FETCH_PWD]

        # Extracting the salt and the key
        salt = pwd[:SIZE_SALT]
        key = pwd[SIZE_KEY:]

        # Making Key with same salt for the password that the user just input.
        login_key = pbkdf2_hmac('sha256', login_pwd.encode('UTF-8'),
                                salt, ITERATION_HASH)

        # Password Check
        if key != login_key:
            print(f"{'*' * 6}", end=" ")
            print("Login Failed! Incorrect Email or Password.")
            return False

        # Successful Login.
        # All the data from the database for the logged in user is assigned to the object.
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

    # Method: Add Income
    # This Method adds an income to the database and increases the balance accordingly.
    # This Method also sends an email to the user with the information
    def add_income(self):
        # Header Prints
        print(f"{'*' * 40}")
        print(f"{'*' * 6}{'ADD INCOME':^28}{'*' * 6}")
        print(f"{'*' * 40}")

        # Asking for information regarding the income and Validating them.
        print(f"{'*' * 6}", end=" ")
        print("Enter the following information.")
        while True:
            print(f"{'*' * 6}", end=" ")
            src = input("Source of Income: ")

            # Using Regular Expression to check if the input source is blank
            if re.search('.+', src):
                break
            print(f"{'*' * 6}", end=" ")
            print("Error! Source cannot be empty.")

        # Amount Validation
        while True:
            print(f"{'*' * 6}", end=" ")
            amnt = input("Amount: ")

            # Checking if the input is a number or not
            try:
                amnt = (float(amnt))
                # Negativity Check
                if amnt < 0:
                    raise ValueError
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

            # Adding the income to the database
            cursor.execute(
                "INSERT INTO ledger(user_info_rowid, trxid, type, name, category, amount, entry_date, description) "
                "VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                (self.user_id, trxid, TYPE_INCOME, src, src, amnt, date.today(), des))

            # Adjusting the balance
            self.balance += amnt
            cursor.execute("UPDATE user_info SET balance = ? WHERE rowid = ? ", (self.balance, self.user_id))

            # Commiting the changes made in the database
            connection.commit()

        except:
            # If something goes wrong.
            print(f"{'*' * 6}", end=" ")
            print("Failed to insert the transaction! Try Again Later.")
        else:
            print(f"{'*' * 6}", end=" ")
            print("Transaction Successfully Inserted!")

            # Sending Email:
            # Setting the email send/receive info
            message = MIMEMultipart("alternative")
            message["Subject"] = "Income Added"
            message["From"] = sender_email
            message["To"] = self.email

            months = [None, "January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                      "November", "December"]

            # Writing the email in HTML format
            html = f"""\
<!doctype html>
<html lang="en">
<body style="background-color: #e8e8e8">
    <div style="width: 50vw; height: 41.5rem; background-color: #ffffff;
    margin-left: auto; margin-right: auto; margin-top:25px">
            <!--Top Bar-->
        <div style="height: 5rem; width: 100%; background-color: #001524; margin-top: 100px;
        position: relative; top: 10%; vertical-align: middle; padding: 10px 0">
        <!-- logo image-->
            <div style="width: 16rem; margin: 0 auto;">
                <img src="./photos/email_logo.png" alt="Logo" style="width: 16rem;  border-radius: 10px">
            </div>
        </div>
        <div style="
            padding: 10px; display: block; float: left; font-family: 'Verdana', sans-serif;
            font-size: 15px;
            margin: 5rem 2rem 0;
            ">
                <p>Hi {self.first_name},</p>
                <p>Thank you for using our Budgeting App. Here is your Transaction details: </p>
            <div style="font-family: 'Verdana', sans-serif;">
                <h3 style="font-size: 15px; margin-bottom: 5px">
                    Transaction Details:
                </h3>

                <h3 style=" font-weight: lighter; font-size: 15px;
                 margin:0">
                    Account Name: {self.first_name + " " + self.last_name}
                </h3>

                <h3 style=" font-weight: lighter; font-size: 15px;
                 margin:0">
                    Month: {months[int(str(date.today()).split('-')[1])]}
                </h3>

                <h3 style=" font-weight: lighter; font-size: 15px;
                 margin: 0 0 10px 0;">
                    Transaction Type: Income
                </h3>
            </div>
            <table style="font-size: 15px; font-family: 'Arial', sans-serif;
                          border-collapse: collapse; width: 100%">
                <thead>
                    <tr>
                       <th style="padding: 0.3rem 0.1rem 0.3rem 0.8rem;
                                  border-style: solid;border-color: black white black black;
                                  border-width: 0 1px 0 1px;
                                  background-color: #001524; color:#FFF; text-align: left">
                            Transaction Number
                        </th>
                        <th style="border-style: solid;border-color: black white black black;
                                  border-width: 0 1px 0 0; padding: 0.3rem 0.1rem 0.3rem 0.8rem;
                                  background-color: #001524; color:#FFF">
                            Source
                        </th>
                        <th style="border-style: solid;border-color: black white black black;
                                  border-width: 0 1px 0 0; padding: 0.3rem 0.1rem 0.3rem 0.8rem;
                                  background-color: #001524; color:#FFF">
                            Amount
                        </th>
                        <th style="border-style: solid;border-color: black black black black;
                                  border-width: 0 1px 0 0; padding: 0.3rem 0.1rem 0.3rem 0.8rem;
                                  background-color: #001524; color:#FFF">
                            Date of Entry
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="border-style: solid;border-color: black black black black;
                                  border-width: 0 1px 1px 1px; padding: 0.3rem 0.1rem 0.3rem 0.8rem;
                                  background-color: #FFF; color:#001524;
                                  text-align: left">
                            {trxid}
                        </td>
                        <td style="border-style: solid;border-color: black black black black;
                                  border-width: 0 1px 1px 0; padding: 0.3rem 0.1rem 0.3rem 0.8rem;
                                  background-color: #FFF; color:#001524;
                                  text-align: left">
                            {src}
                        </td>
                        <td style="border-style: solid;border-color: black black black black;
                                  border-width: 0 1px 1px 0; padding: 0.3rem 0.1rem 0.3rem 0.8rem;
                                  background-color: #FFF; color:#001524;
                                  text-align: left">
                            {amnt}
                        </td>
                        <td style="border-style: solid;border-color: black black black black;
                                  border-width: 0 1px 1px 0; padding: 0.3rem 0.1rem 0.3rem 0.8rem;
                                  background-color: #FFF; color:#001524;
                                  text-align: left">
                            {str(date.today())}
                        </td>
                    </tr>
                </tbody>
            </table>

            <div style="text-align: left;
                        font-family: 'Arial',serif">


                <h2 style="font-family: 'Helvetica', sans-serif">Did you know?</h2>
                <ul>
                    <li>You can look up your transaction through the TrxID</li>
                    <li>You can view statement upto your previous month</li>
                    <li>You have the option to view income, and expense statements differently</li>
                </ul>
                <h2 style="font-family: 'Helvetica', sans-serif; color:#001524">Enjoying the App?</h2>
                <div style="height: 2.5rem; width: 7rem; border-radius: 0.5rem;
                    display: inline-block;
                    background-color:#ec5732; color: #001524;
                    line-height: 2.5rem;
                    cursor: pointer;
                    text-align: center;
                    font-weight: 700">
                    Rate Us
                </div>
            </div>
        </div>


    </div>
</body>
</html>
            """
            # Writing the email in plain text format
            text = f"""Budgeting App\n

                        Hi {self.first_name},\n
                        Thank you for using Budgeting App. Here is your Transaction details:\n\n
                        
                        Transaction Details:\n
                        Account Name: {self.first_name + " " + self.last_name}\n
                        Month: {months[int(str(date.today()).split('-')[1])]} \n
                        Transaction Type: Inocme \n
                        
                        Transaction Number: {trxid}\n
                        Source: {src}\n
                        Amount: {amnt}\n
                        Date of Entry: {str(date.today())}\n\n
                        
                        Did you know:\n
                        > You can look up your transaction through the TrxID\n
                        > You can view statement upto your previous month\n
                        > You have the option to view income, and expense statements differently\n\n
                        
                        
                        Enjoying the App?\n
                        Rate us at https://.../Rate\n"""

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)

            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, self.email, message.as_string()
                )

    # Method: Add Expense
    # This Method adds an expense to the database and reduces the balance accordingly.
    def add_expense(self):
        # The procedure is almost similar to the add_income() method.
        # So, I am not adding the redundant comments.

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
                # Accepting negative values, since expense is negative.
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
            cursor.execute(
                "INSERT INTO ledger(user_info_rowid, trxid, type, name, category, amount, entry_date, description) "
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

    # Utility Function: View Statements
    # This utility function collects info to print monthly statements for all incomes, and expenses.
    # Arguments (2): statement_time -> current month (represented as 1), previous month (represented as 0)
    #                statement_type -> Income (represented as 1),
    #                              Expense (represented as 2),
    #                              Both (represented as 3).
    # Return: Statement -> a List of dictonaries that hold transaction information.
    #         months -> a dictionary to help print when printing the statement.
    #         month -> the integer value of the month requested.
    def view_statement(self, statement_time, statement_type):

        # Numeric Value of this month, and year
        month = str(date.today()).split('-')[INDEX_DATE_MONTH]
        year = str(date.today()).split('-')[INDEX_DATE_YEAR]
        if statement_time == STATEMENT_PREV_MONTH:
            # Assigning the numeric value of the previous month to month variable
            month = "0" + str(int(month) - 1)

        # For Printing the Month
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                  "November", "December"]

        # Upper and lower bound of the date.
        date_lower_bound = str(year) + "-" + month + "-01"
        date_upper_bound = str(year) + "-" + month + "-31"

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

        # This list will contain all the transactions in a dictionary format. One dictionary per transaction.
        statement = []

        # Converting fetched statement into a readable dictionary format.
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

            # Adding the dictionary to the list.
            statement.append(temp_dict)

        # Reversing so that the order of transaction can be latest to oldest
        statement.reverse()

        return statement, months, month

    # Method: View Statement All
    # This method prints out all the transactions (both income and expense) in a month
    # Argument: month (current/previous)
    def view_statement_all(self, month):
        # Checking whether the user is logged in.
        if not self.login_status:
            print("Error! It looks like your not logged in.")
            return False

        # Calling the utility function according to the needs.
        if month == STATEMENT_THIS_MONTH:
            statement, months, month_num = self.view_statement(STATEMENT_THIS_MONTH, STATEMENT_TYPE_ALL)
        elif month == STATEMENT_PREV_MONTH:
            statement, months, month_num = self.view_statement(STATEMENT_PREV_MONTH, STATEMENT_TYPE_ALL)

        if len(statement) == 0:
            print("No Transaction Found!")

        else:
            # Printing Statement
            print(f"{'*' * 40}")
            print(f"{'*' * 6}{'MONTHLY STATEMENT':^28}{'*' * 6}")
            print(f"{'*' * 40}")
            print(f"Statement Type: All Transactions")
            print(f"Name: {self.first_name} {self.last_name}")
            print(f"Month: {months[int(month_num) - 1]}")
            print(f"{'=' * 95}")
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

            print(f"{'=' * 95}")
            print(f"Total{' ' * 79}  {total:>8.2f}")

            print()
            print()
        return True

    # Similar to view_statement_all() method
    def view_statement_income(self, month):
        if self.login_status == False:
            print("Error! It looks like your not logged in.")
            return False
        if month == STATEMENT_THIS_MONTH:
            statement, months, month_num = self.view_statement(STATEMENT_THIS_MONTH, STATEMENT_TYPE_INCOME)
        elif month == STATEMENT_PREV_MONTH:
            statement, months, month_num = self.view_statement(STATEMENT_PREV_MONTH, STATEMENT_TYPE_INCOME)

        if len(statement) == 0:
            print("No Transaction Found!")

        else:
            # Printing Statement
            print(f"{'*' * 40}")
            print(f"{'*' * 6}{'MONTHLY STATEMENT':^28}{'*' * 6}")
            print(f"{'*' * 40}")
            print(f"Name: {self.first_name} {self.last_name}")
            print(f"Month: {months[int(month_num) - 1]}")
            print(f"Statement Type: Income")
            print(f"{'=' * 63}")
            print(f"{'Transaction ID':<18}  {'Source: ':<15}  {'Date':<15}  {'Amount':>8}")
            total = 0
            for item in statement:
                print(f"{item['TrxID']:<18}  {item['Source']:<15}  "
                      f"{item['Date']:<15}  {item['Amount']:>8.2f}")
                total += float(item['Amount'])

            print(f"{'=' * 63}")
            print(f"Total{' ' * 47}  {total:>8.2f}")

            print()
            print()
        return True

    # Similar to view_statement_all() method
    def view_statement_expense(self, month):
        if not self.login_status:
            print("Error! It looks like your not logged in.")
            return False

        if month == STATEMENT_THIS_MONTH:
            statement, months, month_num = self.view_statement(STATEMENT_THIS_MONTH, STATEMENT_TYPE_EXPENSE)
        elif month == STATEMENT_PREV_MONTH:
            statement, months, month_num = self.view_statement(STATEMENT_PREV_MONTH, STATEMENT_TYPE_EXPENSE)

        if len(statement) == 0:
            print("No Transaction Found!")

        else:
            # Printing Statement
            print(f"{'*' * 40}")
            print(f"{'*' * 6}{'MONTHLY STATEMENT':^28}{'*' * 6}")
            print(f"{'*' * 40}")
            print(f"Name: {self.first_name} {self.last_name}")
            print(f"Month: {months[int(month_num) - 1]}")
            print(f"Statement Type: Expense")
            print(f"{'=' * 78}")
            print(f"{'Transaction ID':<18}{'Name':<15}  {'Category':<15}  {'Date':<15}  {'Amount':>8}")
            total = 0
            for item in statement:
                print(f"{item['TrxID']:<18}{item['Name']:<15}  {item['Type']:<15}  "
                      f"{item['Date']:<15}  {item['Amount']:>8.2f}")
                total += float(item['Amount'])

            print(f"{'=' * 78}")
            print(f"Total{' ' * 62}  {total:>8.2f}")

            print()
            print()
        return True

    # Method: Transaction Lookup
    # This method Looks up transactions using the TrxID, and prints the data.
    def transition_lookup(self):
        if not self.login_status:
            print("Error! It looks like your not logged in.")
            return False

        # Input and Validation
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
        # If there is no transaction assign to the input id
        if transaction is None:
            print("Transaction could not be found. Try again with a different Transaction ID")
            return False

        # If the transaction of the given id is assigned to a different user.
        elif transaction[0] != self.user_id:
            print("Transaction could not be found. Try again with a different Transaction ID")
            return False

        # Printing
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
