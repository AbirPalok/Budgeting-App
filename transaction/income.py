from database_connection import *
from datetime import date

# GLOBAL CONSTANT
INDEX_LAST_TRXID = 0


"""
FUNCTION: Takes input from user for information of an income transaction and enters the data into the database.
"""
def add_income(user_id):
    ## Format here
    print("******** ADD INCOME ************")
    print("** Enter the following information.")
    src = input("** Source of Income: ")

    # Amount Validation
    while True:
        amnt = input("** Amount: ")
        try:
            amnt = abs(float(amnt))
        except ValueError:
            print("** Invalid Amount! Please try again with a valid amount.")
        else:
            break

    if add_income_backend(user_id, src, amnt):
        print("** Transaction Successfully Inserted!")
    else:
        print("** Failed to insert the transaction! Try Again Later.")


"""
Function: Backend functionality for the add_income function.
NOTE: DO NOT CALL THIS FUNCTION FROM A USER-END PERSPECTIVE. THIS FUNCTION DOES NOT INTERACT WITH USERS.
"""
def add_income_backend(user_id, src, amnt):
    try:
        cursor.execute("SELECT trxid FROM ledger ORDER BY trxid DESC LIMIT 1")

        # Generating the new TrxID by adding one to the last TrxID
        trxid = cursor.fetchone()[INDEX_LAST_TRXID] + 1

        cursor.execute("INSERT INTO ledger(user_info_rowid, trxid, name, category, amount, entry_date) VALUES(?, ? , ?, ?, ?, ?)",
                       (user_id, trxid, src, src, amnt, date.today()))


        cursor.execute("SELECT balance FROM user_info WHERE rowid = ?", (user_id, ))
        bal = cursor.fetchone()[0]
        bal += amnt

        cursor.execute("UPDATE user_info SET balance = ? WHERE rowid = ? ", (bal, user_id))

        connection.commit()

    except:
        return False

    else:
        return True


