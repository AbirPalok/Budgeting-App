# Imports
from create_new_account import create_new
from user import User


# GLOBAL CONSTANTS
STATEMENT_PREV_MONTH = 0
STATEMENT_THIS_MONTH = 1


# Function: Choice Validator.
# This function validates whether an integer is within a range.
# Input: the choice (can be a number of string type), lower bound of the range (int), upper bound of the range (int)
# Output: prints if the integer is invalid
# Return: a boolean value
def choice_validation(choice, lowerBound, upperBound):
    try:
        choice = int(choice)
    except ValueError:
        print(f"{'*' * 6}", end=" ")
        print("Invalid choice! Try Again.")
        return False
    else:
        if choice > upperBound or choice < lowerBound:
            print(f"{'*' * 6}", end=" ")
            print("Invalid choice! Try Again.")
            return False
        else:
            return True

# Main Function
def main():
    user = User()
    print(f"{'*' * 40}")
    print(f"******{'Budget App':^28}******")
    print(f"{'*' * 40}")

    # The infinite loop
    while True:
        # Checking if the user is already logged in
        if not user.login_status:
            print(f"{'*' * 6} Welcome to Budgeting App")
            print(f"{'*' * 6} Choose an Option: ")
            print(f"{'*' * 6} 1. Login")
            print(f"{'*' * 6} 2. Register")
            print(f"{'*' * 6} 3. Quit")

            while True:
                choice = input(f"{'*' * 6} Enter an option number: ")
                if choice_validation(choice, 1, 3):
                    choice = int(choice)
                    break

            # Calling the Create New user function
            if choice == 2:
                create_new()
                print()
                print()

            # Calling the Login function
            elif choice == 1:
                user.login()
                print()
                print()
            elif choice == 3:
                # Ends the program
                return 0

        # If the user is already Logged in:
        else:
            # Header Prints
            # Printing Full name of the user.
            print(f"{'*' * 6}", end=" ")
            print(f"Welcome {user.first_name} {user.last_name},")

            # Printing the balance of the user.
            print(f"{'*' * 6}", end=" ")
            print(f"Your Current Balance: {user.balance}")

            print()
            print()

            # Infinite loop for options
            while True:
                # Printing the available options of operations for the user.
                print(f"{'*' * 6}", end=" ")
                print(f"Choose an option from below: ")

                print(f"{'*' * 6}", end=" ")
                print("1. Add Income")

                print(f"{'*' * 6}", end=" ")
                print("2. Add Expense")

                print(f"{'*' * 6}", end=" ")
                print("3. View Statement (This month)")

                print(f"{'*' * 6}", end=" ")
                print("4. View Statement (Previous month)")

                print(f"{'*' * 6}", end=" ")
                print("5. Transaction Look up")

                print(f"{'*' * 6}", end=" ")
                print("6. Exit")

                print()
                print()

                while True:
                    # Asking for an input
                    print(f"{'*' * 6}", end=" ")
                    choice = input("Enter an option: ")
                    # Validating the input
                    if choice_validation(choice, 1, 6):
                        choice = int(choice)
                        print()
                        print()
                        break

                # Calling the corresponding function according to the user's choice
                if choice == 1:
                    user.add_income()
                    print()
                    print()
                elif choice == 2:
                    user.add_expense()
                    print()
                    print()
                elif choice == 3:
                    # Printing available choices.
                    print(f"{'*' * 6}** Choose an Option: ")
                    print(f"{'*' * 6}** 1. Statement of All Income")
                    print(f"{'*' * 6}** 2. Statement of All Expenses")
                    print(f"{'*' * 6}** 3. Statement of All Transaction")
                    print(f"{'*' * 6}** 4. Go Back to the Menu")

                    while True:
                        # validating user input.
                        choice = input("Enter your choice: ")
                        if choice_validation(choice, 1, 4):
                            choice = int(choice)
                            break

                    # Calling Functions according to the input.
                    if choice == 1:
                        user.view_statement_income(STATEMENT_THIS_MONTH)
                    if choice == 2:
                        user.view_statement_expense(STATEMENT_THIS_MONTH)
                    if choice == 3:
                        user.view_statement_all(STATEMENT_THIS_MONTH)

                elif choice == 4:
                    # Printing available choices for the user.
                    print(f"{'*' * 6}** Choose an Option: ")
                    print(f"{'*' * 6}** 1. Statement of All Income")
                    print(f"{'*' * 6}** 2. Statement of All Expenses")
                    print(f"{'*' * 6}** 3. Statement of All Transaction")
                    print(f"{'*' * 6}** 4. Go Back to the Menu")

                    while True:
                        # Validating user input.
                        choice = input(F"{'*' * 6}** Enter your choice: ")
                        if choice_validation(choice, 1, 4):
                            choice = int(choice)
                            break

                    # Calling functions according to the user input.
                    if choice == 1:
                        user.view_statement_income(STATEMENT_PREV_MONTH)
                    if choice == 2:
                        user.view_statement_expense(STATEMENT_PREV_MONTH)
                    if choice == 3:
                        user.view_statement_all(STATEMENT_PREV_MONTH)

                elif choice == 5:
                    user.transition_lookup()
                    print()
                    print()

                # Exiting the program
                elif choice == 6:
                    return 0

                # Printing the Name and the Balance and going back to the loop
                print()
                print()

                print(f"{'*' * 6}", end=" ")
                print(f"{user.first_name} {user.last_name},")

                print(f"{'*' * 6}", end=" ")
                print(f"Your Balance: {user.balance}")

                print()
                print()

if __name__ == '__main__':
    main()

