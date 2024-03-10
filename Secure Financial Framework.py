import sqlite3
from tabulate import tabulate
import hashlib

class BankAccount:
    def __init__(self, name, acc_num, conn):
        # Initialize BankAccount object with name, account number, and connection to the database
        self.name = name
        self.acc_num = acc_num
        self.conn = conn
        # Initialize account details by fetching values from the database
        self._initialize_account()

    def _initialize_account(self):
        # Fetch account details from the database based on the account number
        cursor = self.conn.cursor()
        cursor.execute("SELECT total_amount, total_dep, total_wit, total_tra, login_attempts, is_locked FROM accounts WHERE acc_num=?", (self.acc_num,))
        account_details = cursor.fetchone()
        if account_details:
            # If account details are found, initialize attributes with database values
            self.total_amount = account_details[0]
            self.total_dep = account_details[1]
            self.total_wit = account_details[2]
            self.total_tra = account_details[3]
            self.login_attempts = account_details[4]
            self.is_locked = account_details[5]
        else:
            # If account details are not found, initialize attributes with default values
            self.total_amount = 0
            self.total_dep = 0
            self.total_wit = 0
            self.total_tra = 0
            self.login_attempts = 0
            self.is_locked = 0

    # Method to deposit funds into the account
    def deposit(self, amount):
        self.total_amount += amount
        self.total_dep += amount
        self._record_transaction('deposit', amount)

    # Method to withdraw funds from the account
    def withdraw(self, amount):
        if amount <= self.total_amount:
            self.total_amount -= amount
            self.total_wit += amount
            self._record_transaction('withdrawal', -amount)
        else:
            print("Insufficient funds")

    # Method to transfer funds from this account to another account
    def transfer(self, amount, target_acc):
        if amount <= self.total_amount:
            self.total_amount -= amount
            target_acc.deposit(amount)
            self.total_tra += amount  # Update total_transferred
            self._record_transaction('transfer', -amount)
            target_acc._record_transaction('transfer', amount)
        else:
            print("Insufficient funds")

    # Method to record transaction details in the database
    def _record_transaction(self, transaction_type, amount):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO transactions (acc_num, transaction_type, amount) VALUES (?, ?, ?)",
                       (self.acc_num, transaction_type, amount))
        self.conn.commit()

    # Method to retrieve transaction history for this account
    def get_transaction_history(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE acc_num=?", (self.acc_num,))
        return cursor.fetchall()

    # Method to display account details
    def check_details(self):
        print("\nTotal amount =", self.total_amount)
        print("Total deposited amount =", self.total_dep)
        print("Total withdrawal amount =", self.total_wit)
        print("Total transferred amount =", self.total_tra)

    # Method to display a summary of account details
    def summary(self):
        print("\n-----------------------------------------")
        print("Your name:", self.name)
        print("Account number:", self.acc_num)
        print("Total amount:", self.total_amount)
        print("Total deposited amount:", self.total_dep)
        print("Total withdraw amount:", self.total_wit)
        print("Total transferred amount:", self.total_tra)
        print("Account locked:" + ("Yes" if self.is_locked else "No"))
        print("---------------THANK-YOU----------------")

    # Method to update account details in the database
    def update_database(self):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE accounts SET total_amount=?, total_dep=?, total_wit=?, total_tra=?, login_attempts=?, is_locked=? WHERE acc_num=?", 
                       (self.total_amount, self.total_dep, self.total_wit, self.total_tra, self.login_attempts, self.is_locked, self.acc_num))
        self.conn.commit()

    # Method to delete the account from the database
    def delete_account(self, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE acc_num=? AND password=?", (self.acc_num, password))
        account_exists = cursor.fetchone() is not None

        if account_exists:
            cursor.execute("DELETE FROM accounts WHERE acc_num=?", (self.acc_num,))
            self.conn.commit()
            print("Account deleted successfully.")
        else:
            print("Account not found or incorrect password.")
        
    # Method to display transaction history for this account
    def display_transaction_history(self):
        transactions = self.get_transaction_history()
        headers = ["Transaction ID", "Transaction Type", "Amount", "Timestamp"]
        print(tabulate(transactions, headers=headers, tablefmt="grid"))

# Function to create a new account
def create_account(conn):
    name = input("Enter your name: ")
    password = hash_password(input("Set your password: "))
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(acc_num) FROM accounts")
    last_acc_num = cursor.fetchone()[0] or 0
    acc_num = last_acc_num + 1
    # Insert new account details into the accounts table
    cursor.execute("INSERT INTO accounts (name, acc_num, total_amount, total_dep, total_wit, total_tra, login_attempts, is_locked, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   (name, acc_num, 0, 0, 0, 0, 0, 0, password))
    conn.commit()
    print(f"Account created successfully with account number: {acc_num}")
    return BankAccount(name, acc_num, conn)

# Function to display all accounts
def display_accounts(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts")
        accounts = cursor.fetchall()

        if len(accounts) == 0:  # Check if there are no accounts
            print("No accounts found.")
        else:
            headers = ["Username", "Account Number", "Balance", "Consecutive Incorrect Login Attempts", "Account Status"]
            account_data = [(acc[0], acc[1], acc[2], acc[6], "Locked" if acc[7] == 1 or acc[6] >= 3 else "Unlocked") for acc in accounts]
            print(tabulate(account_data, headers=headers, tablefmt="grid"))

    except sqlite3.OperationalError as e:
        print("Error:", e)
        print("The 'accounts' table does not exist or the database has been cleared.")

# Function to lock or unlock a user account
def lock_unlock_account(conn, acc_num, lock_status):
    cursor = conn.cursor()
    
    cursor.execute("UPDATE accounts SET is_locked=? WHERE acc_num=?", (lock_status, acc_num))
    conn.commit()
    if lock_status:
        print(f"Account with account number {acc_num} is locked.")
    else:
        password = hash_password(input("Enter new password to unlock account:"))
        pass_cursor = conn.cursor()
        pass_cursor.execute("UPDATE accounts SET password=? where acc_num=?", (password, acc_num)) 
        print(f"Account with account number {acc_num} is unlocked.")
        cursor.execute("UPDATE accounts SET login_attempts = 0 WHERE acc_num = ?", (acc_num,))

# Function to create an admin account
def create_admin(conn):
    admin_password = hash_password(input("Set your admin password: "))
    cursor = conn.cursor()
    cursor.execute("INSERT INTO admin VALUES (?)", (admin_password,))
    conn.commit()
    print("Admin account created successfully.")

# Function to delete the entire database (only accessible by admin)
def delete_database(conn, password):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin WHERE password=?", (password,))
    admin_exists = cursor.fetchone() is not None

    if admin_exists:
        confirm_delete = input("Are you sure you want to delete the entire database? This will delete all accounts and their transaction history. (yes/no): ")
        if confirm_delete.lower() == 'yes':
            cursor.execute("DROP TABLE accounts")
            cursor.execute("DROP TABLE transactions")
            conn.commit()
            print("Database cleared successfully.")
        else:
            print("Database deletion canceled.")
    else:
        print("Unauthorized access.")

# Function to get user input and return it as an integer choice
def get_user_choice(prompt):
    while True:
        user_input = input(prompt)
        if user_input.strip():
            try:
                choice = int(user_input)
                return choice
            except ValueError:
                print("Invalid input. Please enter a valid choice.")
        else:
            print("Please enter a choice.")

# Function to hash the given password using SHA-256 algorithm
def hash_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

# Function to change the main admin password
def change_admin_password(conn):
    admin_password = hash_password(input("Enter current admin password: "))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin WHERE password=?", (admin_password,))
    admin_exists = cursor.fetchone() is not None

    if admin_exists:
        new_password = hash_password(input("Enter new admin password: "))
        cursor.execute("UPDATE admin SET password=?", (new_password,))
        conn.commit()
        print("Admin password changed successfully.")
    else:
        print("Incorrect admin password. Password change failed.")

# Function to remove or reset the admin password
def remove_admin_password(conn):
    admin_password = hash_password(input("Enter current admin password: "))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin WHERE password=?", (admin_password,))
    admin_exists = cursor.fetchone() is not None

    if admin_exists:
        remove = input("Do you want to remove the admin password? (yes/no): ").lower()
        if remove == 'yes':
            cursor.execute("DELETE FROM admin")
            conn.commit()
            print("Admin password removed successfully.")
        else:
            new_password = hash_password(input("Enter new admin password: "))
            cursor.execute("UPDATE admin SET password=?", (new_password,))
            conn.commit()
            print("Admin password reset successfully.")
    else:
        print("Incorrect admin password. Password removal/reset failed.")

# Main function to run the banking system
def main():
    conn = sqlite3.connect('bank.db')
    # Create necessary tables if they don't exist already
    conn.execute('''CREATE TABLE IF NOT EXISTS accounts 
                     (name TEXT, acc_num INTEGER PRIMARY KEY, total_amount INTEGER, 
                     total_dep INTEGER, total_wit INTEGER, total_tra INTEGER, 
                     login_attempts INTEGER DEFAULT 0, is_locked INTEGER DEFAULT 0, password TEXT)''')

    conn.execute('''CREATE TABLE IF NOT EXISTS admin 
                     (password TEXT PRIMARY KEY)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  acc_num INTEGER,
                  transaction_type TEXT,
                  amount INTEGER,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (acc_num) REFERENCES accounts(acc_num))''')

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin")
    admin_exists = cursor.fetchone() is not None

    # Create admin account if it doesn't exist already
    if not admin_exists:
        create_admin(conn)

    # Main loop to handle user and admin interactions
    while True:
        print("\n  1. Admin ")
        print("  2. User ")
        print("  3. Exit ")

        choice = get_user_choice("Enter your choice: ")

        if choice == 1:
            admin_password = hash_password(input("Enter admin password: "))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE password=?", (admin_password,))
            admin_exists = cursor.fetchone() is not None

            if admin_exists:
                while True:
                    print("\n  1. Admin Login ")
                    print("  2. Create User Account ")
                    print("  3. Delete User Account ")
                    print("  4. Display All Accounts ")
                    print("  5. Delete Entire Database ")
                    print("  6. Change Admin Password ")
                    print("  7. Remove Admin Password ")
                    print("  8. Lock/Unlock User Account ")
                    print("  9. Exit ")

                    admin_choice = get_user_choice("Enter your choice: ")

                    if admin_choice == 1:
                        acc_num = int(input("Enter your account number: "))
                        password = hash_password(input("Enter your password: "))
                        cursor.execute("SELECT * FROM accounts WHERE acc_num=? AND password=?", (acc_num, password))
                        account_details = cursor.fetchone()
                        if account_details:
                            account = BankAccount(account_details[0], account_details[1], conn)
                            account.check_details()
                        else:
                            print("Account not found or incorrect password.")
                    elif admin_choice == 2:
                        account = create_account(conn)
                    elif admin_choice == 3:
                        acc_num = int(input("Enter the account number you want to delete: "))
                        password = hash_password(input("Enter your password: "))
                        cursor.execute("SELECT * FROM accounts WHERE acc_num=?", (acc_num,))
                        account_details = cursor.fetchone()
                        if account_details:
                            account = BankAccount(account_details[0], account_details[1], conn)
                            account.delete_account(password)
                        else:
                            print("Account not found.")
                    elif admin_choice == 4:
                        display_accounts(conn)
                    elif admin_choice == 5:
                        admin_password = hash_password(input("Enter admin password to delete database: "))
                        delete_database(conn, admin_password)
                    elif admin_choice == 6:
                        change_admin_password(conn)
                    elif admin_choice == 7:
                        remove_admin_password(conn)
                    elif admin_choice == 8:
                        acc_num = int(input("Enter account number to lock/unlock: "))
                        lock_status = int(input("Enter lock status (1 for lock, 0 for unlock): "))
                        lock_unlock_account(conn, acc_num, lock_status)
                    elif admin_choice == 9:
                        break
                    else:
                        print("Invalid choice")
            else:
                print("Unauthorized access.")
        elif choice == 2:
            while True:
                print("\n  1. Log In ")
                print("  2. Create Account ")
                print("  3. Exit ")

                user_choice = get_user_choice("Enter your choice: ")

                if user_choice == 1:
                    try:
                        acc_num = int(input("Enter your account number: "))
                        password = hash_password(input("Enter your password: "))
                        cursor.execute("SELECT * FROM accounts WHERE acc_num=?AND password=?", (acc_num, password))
                        account_details = cursor.fetchone()
                        if account_details:
                            if account_details[7] == 1 or account_details[6] >= 3:
                                print("Account is locked. Please contact admin.")
                                continue
                            # reinitialize consecutive incorrect login attempts to 0
                            cursor.execute("UPDATE accounts SET login_attempts = 0 WHERE acc_num = ?", (acc_num,))
                            account = BankAccount(account_details[0], account_details[1], conn)
                            while True:
                                print("\n  1. Deposit Amount ")
                                print("  2. Withdraw Amount ")
                                print("  3. Transfer Amount ")
                                print("  4. Check Detail ")
                                print("  5. Check Transaction History ")
                                print("  6. Log Out ")

                                option = get_user_choice("Enter your choice: ")

                                if option == 1:
                                    amount = int(input("Enter the Amount you want to deposit: "))
                                    account.deposit(amount)
                                    account.update_database()
                                elif option == 2:
                                    amount = int(input("Enter the amount you wish to withdraw: "))
                                    account.withdraw(amount)
                                    account.update_database()
                                elif option == 3:
                                    amount = int(input("Enter the amount you want to transfer: "))
                                    target_acc_num = int(input("Enter the target account number: "))
                                    cursor.execute("SELECT * FROM accounts WHERE acc_num=?", (target_acc_num,))
                                    target_account_details = cursor.fetchone()
                                    if target_account_details:
                                        target_account = BankAccount(target_account_details[0], target_account_details[1], conn)
                                        account.transfer(amount, target_account)
                                        account.update_database()
                                        target_account.update_database()
                                    else:
                                        print("Target account not found.")
                                elif option == 4:
                                    account.check_details()
                                elif option == 5:
                                    acc_num = int(input("Enter your account number: "))
                                    password = hash_password(input("Enter your password: "))
                                    cursor.execute("SELECT * FROM accounts WHERE acc_num=? AND password=?", (acc_num, password))
                                    account_details = cursor.fetchone()
                                    if account_details:
                                        account = BankAccount(account_details[0], account_details[1], conn)
                                        account.display_transaction_history()
                                    else:
                                        print("Account not found or incorrect password.")
                                elif option == 6:
                                    account.summary()
                                    break
                                else:
                                    print("Invalid choice")
                        else:
                            cursor.execute("SELECT * FROM accounts WHERE acc_num=?", (acc_num,))
                            account_details = cursor.fetchone()

                            if account_details:
                                print("Incorrect password")
                                # Increment login attempts
                                cursor.execute("UPDATE accounts SET login_attempts = login_attempts + 1 WHERE acc_num = ?", (acc_num,))
                                conn.commit()  # Commit the changes
                                # Retrieve the updated account details
                                cursor.execute("SELECT * FROM accounts WHERE acc_num=?", (acc_num,))
                                updated_account_details = cursor.fetchone()
                                if updated_account_details[6] == 3:
                                    print("Account is locked after 3 consecutive failed login attempts. Please contact admin.")
                                if updated_account_details[6] > 3:
                                    print("Account is locked. Please contact admin.")

                            else:
                                print("Account does not exist")
                    except sqlite3.OperationalError as e:
                        print("Error:", e)
                        print("The 'accounts' table does not exist or the database has been cleared.")
                elif user_choice == 2:
                    account = create_account(conn)
                    print("Account created successfully.")
                elif user_choice == 3:
                    break
                else:
                    print("Invalid choice")
        elif choice == 3:
            break
        else:
            print("Invalid choice")

    conn.close()

if __name__ == "__main__":
    main()
