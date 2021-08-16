from create_new_account import create_new

from user import User

# GLOBAL CONSTANTS
STATEMENT_PREV_MONTH = 0
STATEMENT_THIS_MONTH = 1



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


def main():
    user = User()
    print(f"{'*' * 40}")
    print(f"******{'Budget App':^28}******")
    print(f"{'*' * 40}")

    while True:
        if not user.login_status:
            print(f"{'*' * 6} Welcome to Budgeting App")
            print(f"{'*' * 6} Choose an Option: ")
            print(f"{'*' * 6} 1. Login")
            print(f"{'*' * 6} 2. Register")

            while True:
                choice = input(f"{'*' * 6} Enter an option number: ")
                if choice_validation(choice, 1, 2):
                    choice = int(choice)
                    break

            if choice == 2:
                create_new()
                print()
                print()
            elif choice == 1:
                user.login()
                print()
                print()
        else:
            print(f"{'*' * 6}", end=" ")
            print(f"Welcome {user.first_name} {user.last_name},")

            print(f"{'*' * 6}", end=" ")
            print(f"Your Current Balance: {user.balance}")

            # print(f"{'*' * 6}")
            # print(f"{'*' * 6}")

            print()
            print()

            while True:
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

                while True:
                    print(f"{'*' * 6}", end=" ")
                    choice = input("Enter an option: ")
                    if choice_validation(choice, 1, 5):
                        choice = int(choice)
                        break

                if choice == 1:
                    user.add_income()
                    print()
                    print()
                elif choice == 2:
                    user.add_expense()
                    print()
                    print()
                elif choice == 3:
                    print(f"{'*' * 6}** Choose an Option: ")
                    print(f"{'*' * 6}** 1. Statement of All Income")
                    print(f"{'*' * 6}** 2. Statement of All Expenses")
                    print(f"{'*' * 6}** 3. Statement of All Transaction")

                    while True:
                        choice = input("Enter your choice: ")
                        if choice_validation(choice, 1, 3):
                            choice = int(choice)
                            break

                    if choice == 1:
                        user.view_statement_income(STATEMENT_THIS_MONTH)
                    if choice == 2:
                        user.view_statement_expense(STATEMENT_THIS_MONTH)
                    if choice == 3:
                        user.view_statement_all(STATEMENT_THIS_MONTH)


                elif choice == 4:
                    print(f"{'*' * 6}** Choose an Option: ")
                    print(f"{'*' * 6}** 1. Statement of All Income")
                    print(f"{'*' * 6}** 2. Statement of All Expenses")
                    print(f"{'*' * 6}** 3. Statement of All Transaction")

                    while True:
                        choice = input(F"{'*' * 6}** Enter your choice: ")
                        if choice_validation(choice, 1, 3):
                            choice = int(choice)
                            break

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

                print(f"{'*' * 6}", end=" ")
                print(f"{user.first_name} {user.last_name},")

                print(f"{'*' * 6}", end=" ")
                print(f"Your Balance: {user.balance}")

                print()
                print()




if __name__ == '__main__':
    main()


