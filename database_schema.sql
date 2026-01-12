DROP DATABASE IF EXISTS cbs_dbs;
CREATE DATABASE cbs_dbs;
USE cbs_dbs;

            CREATE TABLE BRANCH (
                BranchID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Address TEXT,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE EMPLOYEE (
                EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Role VARCHAR(50) NOT NULL,
                BranchID INT,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (BranchID) REFERENCES BRANCH(BranchID)
            );

            CREATE TABLE CUSTOMER (
                CustomerID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                CNIC VARCHAR(15) UNIQUE NOT NULL,
                Contact VARCHAR(15),
                Type ENUM('Individual', 'Business') DEFAULT 'Individual',
                DOB DATE,
                Password VARCHAR(100) NOT NULL DEFAULT '123456',  -- Added password field
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE ACCOUNTTYPE (
                AccountTypeID INT AUTO_INCREMENT PRIMARY KEY,
                TypeName VARCHAR(50) NOT NULL,
                Description TEXT,
                MinBalance DECIMAL(15,2) DEFAULT 0
            );


            CREATE TABLE ACCOUNT (
                AccountNo INT AUTO_INCREMENT PRIMARY KEY,
                CustomerID INT NOT NULL,
                Type VARCHAR(20) NOT NULL,
                Balance DECIMAL(15,2) DEFAULT 0,
                Status ENUM('Active', 'Closed', 'Suspended') DEFAULT 'Active',
                BranchID INT,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (CustomerID) REFERENCES CUSTOMER(CustomerID),
                FOREIGN KEY (BranchID) REFERENCES BRANCH(BranchID)
            );


            CREATE TABLE TRANSACTION (
                TransID INT AUTO_INCREMENT PRIMARY KEY,
                FromAccount INT,
                ToAccount INT,
                Amount DECIMAL(15,2) NOT NULL,
                Type ENUM('Deposit', 'Withdrawal', 'Transfer') NOT NULL,
                Remark TEXT,
                DateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (FromAccount) REFERENCES ACCOUNT(AccountNo),
                FOREIGN KEY (ToAccount) REFERENCES ACCOUNT(AccountNo)
            );


            CREATE TABLE AuditLog (
                LogID INT AUTO_INCREMENT PRIMARY KEY,
                Operation VARCHAR(50) NOT NULL,
                TableAffected VARCHAR(50) NOT NULL,
                UserName VARCHAR(50) NOT NULL,
                Details TEXT,
                DateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE AppUser (
                UserID INT AUTO_INCREMENT PRIMARY KEY,
                Username VARCHAR(50) UNIQUE NOT NULL,
                Password VARCHAR(100) NOT NULL,
                Role VARCHAR(20) DEFAULT 'admin',
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );


 # Add accounts for sample Data
INSERT INTO BRANCH (Name, Address) VALUES ('Main Branch', '123 Banking Street, City');
INSERT INTO EMPLOYEE (Name, Role, BranchID) VALUES ('Admin Manager', 'Manager', 1);
INSERT INTO ACCOUNTTYPE (TypeName, Description, MinBalance) VALUES ('Savings', 'Regular Savings Account', 500);
INSERT INTO ACCOUNTTYPE (TypeName, Description, MinBalance) VALUES ('Current', 'Business Current Account', 1000);
INSERT INTO ACCOUNTTYPE (TypeName, Description, MinBalance) VALUES ('Basic Banking', 'Basic Banking Account', 0);
INSERT INTO AppUser (Username, Password, Role) VALUES ('admin', 'admin123', 'admin');

 # Add sample customers with passwords
INSERT INTO CUSTOMER (Name, CNIC, Contact, Type, Password) VALUES ('John Doe', '4220112345678', '03001234567', 'Individual', 'john123');
INSERT INTO CUSTOMER (Name, CNIC, Contact, Type, Password) VALUES ('Jane Smith', '4220176543210', '03009876543', 'Individual', 'jane123');
INSERT INTO CUSTOMER (Name, CNIC, Contact, Type, Password) VALUES ('ABC Corporation', '4220155555555', '02112345678', 'Business', 'abc123');

 # Add accounts for sample customers
INSERT INTO ACCOUNT (CustomerID, Type, Balance, BranchID) VALUES (1, 'Savings', 50000.00, 1);
INSERT INTO ACCOUNT (CustomerID, Type, Balance, BranchID) VALUES (2, 'Current', 75000.00, 1);
INSERT INTO ACCOUNT (CustomerID, Type, Balance, BranchID) VALUES (3, 'Basic Banking', 100000.00, 1);
