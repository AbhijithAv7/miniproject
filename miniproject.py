import sqlite3
import re
import random
from datetime import datetime

conn = sqlite3.connect('bank.db')

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT NOT NULL
    )
        ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        email TEXT UNIQUE,
        phone_no TEXT,
        password TEXT
    )
        ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS accdetails (
        acc_no INTEGER PRIMARY KEY UNIQUE,           
        balance REAL,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
        ''')


cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaction_details (
        trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
        acc_no INTEGER,
        deposit INTEGER,
        withdraw INTEGER,
        total_amount INTEGER,
        date TEXT,     
        FOREIGN KEY(acc_no) REFERENCES accdetails(acc_no)
    )
        ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS loans (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        loan_type TEXT,
        amount REAL,
        status TEXT DEFAULT 'PENDING',
        date TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
        ''')

# /////////////////////////  admin login  /////////////////////////////////////
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

def adminlogin():
    print("\n=== ADMIN LOGIN ===\n")

    username = input("Enter username: ")
    password = input("Enter password: ")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        print("✅ Login successful!")
        return True
    else:
        print("❌ Invalid username or password.")
        return False

# ///////////////////////////////////  account details ////////////////////////////////
def accdetails(user_id, pay):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    while True:
        acc_no = random.randint(1000, 9999)
        cursor.execute("SELECT acc_no FROM accdetails WHERE acc_no=?", (acc_no,))
        if not cursor.fetchone():  
            break                   

    cursor.execute('''
        INSERT INTO accdetails(acc_no, balance, user_id)
        VALUES (?, ?, ?)
    ''', (acc_no, pay, user_id))

    conn.commit()
    conn.close()


    print("\n✅ Account created successfully!")
    print(f"Account Number: {acc_no}")
    print(f"Balance: ₹{pay:.2f}\n")

# ///////////////////////////////////  user login ////////////////////////////////            
def register():
    print("\nREGISTER\n")
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    try:
        name = input("Enter username: ")
        age = int(input("Enter age: "))
        
        email = input("Enter email: ")
        pattern = r'[a-zA-Z0-9.^&*$_%+-]+@[a-z]+\.[a-z]+'
        result = re.findall(pattern, email)
        if not result:
            print("❌ Invalid email!")
            return
        email = result[0]

        phone_no = input("Enter phone number: ")
        ph = r'\d{10}'
        value = re.findall(ph, phone_no)
        if not value:
            print("❌ Invalid phone number!")
            return
        phone_no = value[0]

        password = input("Enter password: ")

        while True:
            pay = float(input("Pay minimum 1000rs to open your account: "))
            if pay >= 1000:
                break
            else:
                print("❌ Minimum ₹1000 required!")
        try:
            cursor.execute(
                "INSERT INTO users(name, age, email, phone_no, password) VALUES (?, ?, ?, ?, ?)",
                (name, age, email, phone_no, password)
            )
            
        except sqlite3.IntegrityError as e:
            print(f"❌ Registration failed: {e}")
            return

        cursor.execute("SELECT user_id FROM users WHERE email=?", (email,))
        user_id = cursor.fetchone()[0]

        accdetails(user_id, pay)

        print("\n✅ Registration completed successfully!")

    except Exception as e:
        print(f"❌ Something went wrong: {e}")
    finally:
        conn.commit()
        conn.close()



def userlogin():
    print('\nLOGIN USER\n')
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    username = input(' username : ')
    password = input(' password : ')
    cursor.execute('''
                SELECT user_id FROM users WHERE name = ? AND password = ?
        ''',(username,password))
    user = cursor.fetchone()
    if user:
        user_id = user[0]       
        print(f"\n✅ Login successful! Your user_id = {user_id}")
        return user_id
    else:
        print('no such user')
        return None

# //////////////////////////////////  transaction details ///////////////////////////////
def transaction(cursor, acc_no, deposit, withdraw, total_amount):
    cursor.execute('''
        INSERT INTO transaction_details(acc_no, deposit, withdraw, total_amount, date)
        VALUES (?, ?, ?, ?, datetime('now'))
    ''', (acc_no, deposit, withdraw, total_amount))


# ////////////////////////////////////// admin functions /////////////////////////////
def admin_view_all_accounts():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, acc_no, balance FROM accdetails")
    data = cursor.fetchall()

    if not data:
        print("\nNo accounts found.\n")
        return

    print("\n========== ALL USERS ACCOUNT DETAILS ==========\n")

 
    print("+----------+------------+-----------+")
    print("| USER ID  | ACC NO     | BALANCE   |")
    print("+----------+------------+-----------+")

   
    for user_id, acc_no, balance in data:
        print(f"| {user_id:<8} | {acc_no:<10} | {balance:<9} |")

    print("+----------+------------+-----------+")

    conn.close()


def admin_view_one_account():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    acc_no = input("Enter account number: ")

    cursor.execute("SELECT user_id, acc_no, balance FROM accdetails WHERE acc_no = ?", (acc_no,))
    row = cursor.fetchone()

    if not row:
        print("\nNo accounts found.\n")
        return

    user_id, acc_no, balance = row  

    print("\n========== ACCOUNT DETAILS ==========\n")

    print("+----------+------------+-----------+")
    print("| USER ID  | ACC NO     | BALANCE   |")
    print("+----------+------------+-----------+")

    print(f"| {user_id:<8} | {acc_no:<10} | {balance:<9} |")

    print("+----------+------------+-----------+")

    conn.close()


def admin_view_all_transactions():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM transaction_details')
    rows = cursor.fetchall()

    if not rows:
        print("❌ No transactions found.")
        return

    print("\n=== ALL USERS TRANSACTION DETAILS ===\n")

    print("+-----------+-----------+-----------+-----------+-------------+---------------------+")
    print("| TRANS_ID  | ACC_NO    | DEPOSIT   | WITHDRAW  | BAL_AFTER   | DATE_TIME           |")
    print("+-----------+-----------+-----------+-----------+-------------+---------------------+")

    for trans_id, acc_no, deposit, withdraw, bal_after, date_time in rows:
        print(f"| {trans_id:<9} | {acc_no:<9} | {deposit:<9} | {withdraw:<9} | {bal_after:<11} | {date_time:<19} |")

    print("+-----------+-----------+-----------+-----------+-------------+---------------------+")


    conn.close()


def admin_view_one_transaction():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    acc_no = input("Enter account number: ")

    cursor.execute("SELECT * FROM transaction_details WHERE acc_no = ?", (acc_no,))
    rows = cursor.fetchall()   
    if not rows:
        print("❌ No transactions found.")
        return

    print("\n=== TRANSACTION DETAILS ===\n")

    print("+-----------+-----------+-----------+-----------+-------------+---------------------+")
    print("| TRANS_ID  | ACC_NO    | DEPOSIT   | WITHDRAW  | BAL_AFTER   | DATE_TIME           |")
    print("+-----------+-----------+-----------+-----------+-------------+---------------------+")

    for trans_id, acc_no, deposit, withdraw, bal_after, date_time in rows:
        print(f"| {trans_id:<9} | {acc_no:<9} | {deposit:<9} | {withdraw:<9} | {bal_after:<11} | {date_time:<19} |")

    print("+-----------+-----------+-----------+-----------+-------------+---------------------+")

    conn.close()

def admin_view_loans():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT loan_id, name, loan_type, amount, status, date
        FROM loans, users
        WHERE loans.user_id = users.user_id
    """)
    data = cursor.fetchall()
    conn.close()

    print("\n=== ALL LOAN REQUESTS ===\n")

    if not data:
        print("No loan applications found.\n")
        return

    print("+--------+---------------+-----------------+------------+-----------+---------------------+")
    print("| ID     | User Name     | Loan Type       | Amount     | Status    | Date                |")
    print("+--------+---------------+-----------------+------------+-----------+---------------------+")

    for loan_id, username, loan_type, amount, status, date in data:
        print(f"| {loan_id:<6} | {username:<13} | {loan_type:<15} | {amount:<10} | {status:<9} | {date} |")

    print("+--------+---------------+-----------------+------------+-----------+---------------------+\n")

def approve_reject_loan():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    loan_id = int(input("Enter Loan ID to update: "))

    cursor.execute("SELECT status FROM loans WHERE loan_id=?", (loan_id,))
    result = cursor.fetchone()

    if not result:
        print("❌ Invalid Loan ID")
        conn.close()
        return

    if result[0] != "PENDING":
        print("⚠ Loan already processed")
        conn.close()
        return

    print("\n1. APPROVE LOAN")
    print("2. REJECT LOAN")
    
    choice = int(input("\nChoose: "))

    if choice == 1:
        new_status = "APPROVED"
    elif choice == 2:
        new_status = "REJECTED"
    else:
        print("❌ Invalid option")
        conn.close()
        return

    cursor.execute("UPDATE loans SET status=? WHERE loan_id=?", (new_status, loan_id))
    conn.commit()
    conn.close()

    print(f"\n✅ Loan {new_status} Successfully!\n")


# ///////////////////////////////  user functions  /////////////////////////////

def user_view_accdetails(current_user_id):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, acc_no, balance FROM accdetails WHERE user_id = ?", (current_user_id,))
    row = cursor.fetchone()

    if not row:
        print("❌ No account found.")
        return

    user_id, acc_no, balance = row  

    print("\n=== ACCOUNT DETAILS ===\n")

    print("+----------+------------+-----------+")
    print("| USER ID  | ACC NO     | BALANCE   |")
    print("+----------+------------+-----------+")

    print(f"| {user_id:<8} | {acc_no:<10} | {balance:<9} |")

    print("+----------+------------+-----------+")

    conn.close()


def deposit(user_id):
    print("\n=== DEPOSIT AMOUNT ===\n")
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    acc_no = get_acc_no(user_id)

    if acc_no is None:
        print("❌ No account found!")
        conn.close()
        return

    cursor.execute("SELECT balance FROM accdetails WHERE acc_no = ?", (acc_no,))
    result = cursor.fetchone()

    current_balance = result[0]

    amount = float(input("Enter amount to deposit: "))

    if amount <= 0:
        print("❌ Amount must be greater than zero")
        return

    new_balance = current_balance + amount

    cursor.execute("UPDATE accdetails SET balance = ? WHERE acc_no = ?", (new_balance, acc_no))

    transaction(cursor, acc_no, amount, 0, new_balance)

    print("\n✅ Amount deposited successfully")
    print(f"💰 New Balance: ₹{new_balance:.2f}\n")

    conn.commit()
    conn.close()


def withdraw(user_id):
    print("\n=== WITHDRAW AMOUNT ===\n")
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    acc_no = get_acc_no(user_id)

    if acc_no is None:
        print("❌ No account found!")
        conn.close()
        return

    cursor.execute("SELECT balance FROM accdetails WHERE acc_no = ?", (acc_no,))
    result = cursor.fetchone()

    current_balance = result[0]

    amount = float(input("Enter amount to withdraw: "))

    if amount <= 0:
        print("❌ Amount must be greater than zero")
        return

    if amount > current_balance:
        print("❌ Insufficient balance!")
        return

    new_balance = current_balance - amount

    cursor.execute("UPDATE accdetails SET balance = ? WHERE acc_no = ?", (new_balance, acc_no))

    transaction(cursor, acc_no, 0, amount, new_balance)

    print("\n✅ Amount withdrawn successfully")
    print(f"💰 New Balance: ₹{new_balance:.2f}\n")

    conn.commit()
    conn.close()



def check_balance(user_id):
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM accdetails WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    conn.close()  

    if result:
        balance = result[0]
        print(f"Current Balance: ₹{balance:.2f}")
    else:
        print("Account not found.")


def get_acc_no(user_id):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT acc_no FROM accdetails WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None


def user_transaction(acc_no):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transaction_details WHERE acc_no = ?", (acc_no,))
    transactions = cursor.fetchall()

    if not transactions:
        print("❌ No transactions found.")
        return

    print("+-----------+-----------+-----------+-----------+-------------+---------------------+")
    print("| TRANS_ID  | ACC_NO    | DEPOSIT   | WITHDRAW  | BAL_AFTER   | DATE_TIME           |")
    print("+-----------+-----------+-----------+-----------+-------------+---------------------+")

    for trans_id, acc_no, deposit, withdraw, bal_after, date_time in transactions:
        print(f"| {trans_id:<9} | {acc_no:<9} | {deposit:<9} | {withdraw:<9} | {bal_after:<11} | {date_time:<19} |")

    print("+-----------+-----------+-----------+-----------+-------------+---------------------+")

    conn.close()


def apply_loan(user_id):
    print("\n=== APPLY FOR LOAN ===\n")
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    print("1. Personal Loan")
    print("2. Home Loan")
    print("3. Vehicle Loan")
    print("4. Education Loan")

    choice = int(input("Select loan type: "))

    loan_types = {
        1: "Personal Loan",
        2: "Home Loan",
        3: "Vehicle Loan",
        4: "Education Loan"
    }

    if choice not in loan_types:
        print("❌ Invalid choice")
        return

    loan_type = loan_types[choice]
    amount = float(input("Enter loan amount: "))

    if amount <= 0:
        print("❌ Amount must be greater than zero")
        return
    
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO loans (user_id, loan_type, amount, date) VALUES (?, ?, ?, ?)",
        (user_id, loan_type, amount, date)
    )

    conn.commit()
    conn.close()

    print("\n✅ Loan Request Submitted Successfully!")
    print(f"📌 Loan Type: {loan_type}")
    print(f"💰 Amount Requested: ₹{amount:.2f}")
    print("⏳ Status: PENDING\n")


def view_my_loans(user_id):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT loan_id, loan_type, amount, status, date FROM loans WHERE user_id=?", (user_id,))
    loans = cursor.fetchall()

    conn.close()

    print("\n=== MY LOAN DETAILS ===\n")

    if not loans:
        print("❌ You have no loan applications.\n")
        return

    print("+--------+-----------------+------------+-----------+---------------------+")
    print("| ID     | Loan Type       | Amount     | Status    | Date                |")
    print("+--------+-----------------+------------+-----------+---------------------+")

    for loan_id, loan_type, amount, status, date in loans:
        print(f"| {loan_id:<6} | {loan_type:<15} | {amount:<10} | {status:<9} | {date} |")

    print("+--------+-----------------+------------+-----------+---------------------+\n")



def delete_transaction():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    trans_id = int(input("Enter the transaction ID to delete: "))

   
    cursor.execute('''
                SELECT trans_id FROM transaction_details WHERE trans_id = ?
                   ''', (trans_id,))
    result = cursor.fetchone()

    cursor.execute('''
                DELETE FROM transaction_details WHERE trans_id = ?
                   ''', (trans_id,))

    if not result:
        print("❌ Transaction ID not found.")
        conn.close()
        return
    print("✅ Transaction deleted successfully.")

    conn.commit()
    conn.close()

def delete_account(user_id):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    choice = input("Do you want to delete your account (y/n) : ")

    if choice != 'y':
        print("\n❌ Account deletion cancelled.")
        return  

    cursor.execute("SELECT acc_no FROM accdetails WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        print("❌ No account found.")
        conn.close()
        return

    acc_no = row[0]

    cursor.execute('''
                DELETE FROM transaction_details WHERE acc_no = ?
                   ''', (acc_no,))
    
    cursor.execute('''
                DELETE FROM accdetails WHERE acc_no = ?
                   ''', (acc_no,))

    cursor.execute('''
                DELETE FROM users WHERE user_id = ?
                   ''', (user_id,))

    print("\n✅ Your account has been deleted successfully!")
    print("➡ Redirecting to main menu...\n")
    conn.commit()
    conn.close()

    main()  


def main():
    print("======BANK MANAGEMENT SYSTEM======")
    while True:
        print("1.ADMIN")
        print("2.USER")
        print("3.EXIT")
        ch = int(input("\n enter your choice : "))

        if ch == 1:
            if adminlogin():  
                while True:  
                    print("\n=== ADMIN MENU ===\n")
                    print("1. View all account details")
                    print("2. View particular person account details")
                    print("3. View all transaction details")
                    print("4. View particular person transaction details")
                    print("5. View Loan Requests")
                    print("6. Approve / Reject Loan")
                    print("7. Logout")  

                    c = int(input("\nEnter your choice: "))

                    if c == 1:
                        admin_view_all_accounts()
                    elif c == 2:
                        admin_view_one_account()
                    elif c == 3:
                        admin_view_all_transactions()
                    elif c == 4:
                        admin_view_one_transaction()
                    elif c == 5:
                        admin_view_loans()
                    elif c == 6:
                        approve_reject_loan()
                    elif c == 7:
                        print("Logging out...")
                        break 
                    else:
                        print("❌ Invalid choice")

        elif ch == 2:
            while True:
                print("\n==USER==\n")
                print("1. Register")
                print("2. Login")
                print("3. Previous")

                try:
                    choice = int(input("\nEnter your choice : "))
                except ValueError:
                    print("❌ Invalid input! Numbers only.")
                    continue

        
                if choice == 1:
                    register()
                    print("\nThank You For Registering\n")
                elif choice == 2:
                    user_id = userlogin()

                    if user_id:
                        while True:
                            print("\n1. Account details")
                            print("2. Deposit")
                            print("3. Withdraw")
                            print("4. Balance")
                            print("5. Transactions")
                            print("6. apply loans")
                            print("7. view loans")
                            print("8. Delete Transaction")
                            print("9. Delete Account")
                            print("10. Logout")

                            try:
                                uc = int(input("\nEnter your choice: "))
                            except ValueError:
                                print("❌ Invalid input!")
                                continue

                            if uc == 1:
                                user_view_accdetails(user_id)
                            elif uc == 2:
                                deposit(user_id)
                            elif uc == 3:
                                withdraw(user_id)
                            elif uc == 4:
                                check_balance(user_id)
                            elif uc == 5:
                                acc_no = get_acc_no(user_id)
                                if acc_no:
                                    user_transaction(acc_no)
                                else:
                                    print("❌ No account found!")
                            elif uc == 6:
                                apply_loan(user_id)
                            elif uc == 7:
                                view_my_loans(user_id)
                            elif uc == 8:
                                delete_transaction()
                            elif uc == 9:
                                delete_account(user_id)
                            elif uc == 10:
                                return  
                            else:
                                print("❌ Invalid option!")
                elif choice == 3:
                    break 
                else:
                    print("❌ Invalid choice, try again.")


main()


       