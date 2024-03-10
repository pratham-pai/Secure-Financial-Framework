# Secure Financial Framework

Secure Financial Framework is a Python-based banking system designed to ensure robust data persistence and security in financial transactions. Built using an object-oriented approach, it offers various advanced features for secure banking operations.

## Main Features

- **Data Persistence:** Utilizes SQLite3 database for persistent storage of account details and transaction history.
- **Object-Oriented Approach:** Organized and structured codebase for efficient management of banking operations.
- **Password Encryption:** Implements SHA-256 hashing algorithm to encrypt user passwords for enhanced security.
- **Two-Factor Authentication:** Provides an additional layer of security through password-based authentication. (will be implemented in the next commit)
- **Transaction History:** Transparent recording and display of account transaction history for users and administrators.
- **Account Locking Mechanism:** Prevents unauthorized access by locking user accounts after consecutive failed login attempts.
- **Database Operations:** Enables seamless database operations for account management and administrative tasks.
- **Admin Panel:** Includes functionalities for administrators to manage user accounts, monitor transactions, and maintain system integrity.

## Usage

1. **Admin Functions:** Admins can log in, create user accounts, delete accounts, display all accounts, delete the entire database, change admin password, remove/reset admin password, and lock/unlock user accounts.
2. **User Functions:** Users can log in, deposit funds, withdraw funds, transfer funds, check account details, view transaction history, and log out securely.

## Getting Started

To run the Secure Financial Framework:

1. Ensure you have Python 3.x installed on your system.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the program by executing `python secure_financial_framework.py` in your terminal.

## Disclaimer

This project is intended for educational purposes only and should not be used in production environments without proper security auditing and enhancements.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/pratham-pai/Secure-Financial-Framework/blob/main/LICENSE) file for details.

