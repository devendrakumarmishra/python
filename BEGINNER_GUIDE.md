# Beginner Guide - How to Run This Python Flask Project

A step-by-step guide for absolute beginners to set up and run this Flask web application on your computer.

---

## Table of Contents

1. [Prerequisites (What You Need First)](#1-prerequisites-what-you-need-first)
2. [Install Python](#2-install-python)
3. [Install MySQL Database](#3-install-mysql-database)
4. [Set Up the Database](#4-set-up-the-database)
5. [Set Up the Project](#5-set-up-the-project)
6. [Install Python Packages](#6-install-python-packages)
7. [Configure the App](#7-configure-the-app)
8. [Run the App](#8-run-the-app)
9. [Open in Browser](#9-open-in-browser)
10. [Run Other Python Scripts (ML)](#10-run-other-python-scripts-ml)
11. [Common Errors & Fixes](#11-common-errors--fixes)
12. [Useful Commands Cheat Sheet](#12-useful-commands-cheat-sheet)

---

## 1. Prerequisites (What You Need First)

Before starting, make sure you have:

- A computer (Windows, Mac, or Linux)
- Internet connection (to download tools)
- A text editor (VS Code recommended - https://code.visualstudio.com/)
- A terminal/command prompt

---

## 2. Install Python

### Check if Python is already installed:
```bash
python3 --version
```
If you see something like `Python 3.x.x`, you're good. If not, install it:

### Windows:
1. Go to https://www.python.org/downloads/
2. Download the latest Python 3 version
3. Run the installer
4. **IMPORTANT:** Check the box that says "Add Python to PATH"
5. Click "Install Now"

### Mac:
```bash
brew install python3
```
(Install Homebrew first from https://brew.sh if you don't have it)

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Verify installation:
```bash
python3 --version
pip3 --version
```

---

## 3. Install MySQL Database

### Windows:
1. Download MySQL Installer from https://dev.mysql.com/downloads/installer/
2. Run the installer and choose "Developer Default"
3. Set root password to `root` (or remember what you set)

### Mac:
```bash
brew install mysql
brew services start mysql
```

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

### Set MySQL root password (Linux):
```bash
sudo mysql
```
Then inside MySQL:
```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
FLUSH PRIVILEGES;
EXIT;
```

### Verify MySQL is running:
```bash
mysql -u root -p
```
Enter your password when prompted. If you see `mysql>` prompt, it's working. Type `EXIT;` to quit.

---

## 4. Set Up the Database

### Login to MySQL:
```bash
mysql -u root -p
```
Enter password: `root`

### Create the database and tables:
Copy and paste these commands one by one in the MySQL prompt:

```sql
-- Step 1: Create the database
CREATE DATABASE IF NOT EXISTS python;

-- Step 2: Select the database
USE python;

-- Step 3: Create users table (for login)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 4: Create profiles table (user details)
CREATE TABLE IF NOT EXISTS profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(200),
    email VARCHAR(200),
    phone VARCHAR(20),
    bio TEXT,
    profile_image VARCHAR(300),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Step 5: Create notes table (CRUD feature)
CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 6: Create contacts table (contact form messages)
CREATE TABLE IF NOT EXISTS contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL,
    subject VARCHAR(300),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 7: Verify tables were created
SHOW TABLES;
```

You should see:
```
+------------------+
| Tables_in_python |
+------------------+
| contacts         |
| notes            |
| profiles         |
| users            |
+------------------+
```

Type `EXIT;` to quit MySQL.

---

## 5. Set Up the Project

### Step 1: Open terminal and go to the project folder:
```bash
cd /var/www/html/python
```

### Step 2: Create a virtual environment (one time only):
```bash
python3 -m venv venv
```

**What is a virtual environment?**
It's a separate folder that keeps this project's packages isolated from other projects. Think of it like a private box for this project's tools.

### Step 3: Activate the virtual environment:

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

After activation, you'll see `(venv)` at the start of your terminal:
```
(venv) user@computer:/var/www/html/python$
```

**IMPORTANT:** You must activate the virtual environment every time you open a new terminal to work on this project.

### Step 4: To deactivate (when you're done working):
```bash
deactivate
```

---

## 6. Install Python Packages

Make sure your virtual environment is activated (you see `(venv)` in terminal), then run:

### Install all required packages:
```bash
pip install flask flask-bcrypt flask-mail pymysql
```

### What each package does:
| Package | Purpose |
|---------|---------|
| `flask` | The web framework (runs the website) |
| `flask-bcrypt` | Encrypts/hashes passwords securely |
| `flask-mail` | Sends emails from the app |
| `pymysql` | Connects Python to MySQL database |

### For the Machine Learning scripts, also install:
```bash
pip install numpy scikit-learn pandas
```

| Package | Purpose |
|---------|---------|
| `numpy` | Math and array operations |
| `scikit-learn` | Machine learning library |
| `pandas` | Data analysis and CSV handling |

### Save installed packages to a file (good practice):
```bash
pip freeze > requirements.txt
```

### Install from requirements.txt (if it already exists):
```bash
pip install -r requirements.txt
```

### Verify packages are installed:
```bash
pip list
```

---

## 7. Configure the App

### Database Configuration:
Open `app.py` and check the database settings (around line 97-105):

```python
def get_db():
    return pymysql.connect(
        host='localhost',       # Keep as localhost
        user='root',            # Your MySQL username
        password='root',        # Your MySQL password (change if different)
        database='python',      # Database name we created
        cursorclass=pymysql.cursors.DictCursor
    )
```

If your MySQL password is different from `root`, update it here.

### Email Configuration (Optional):
If you want the email feature to work, update these lines in `app.py` (around line 79-82):

```python
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'        # Your real Gmail
app.config['MAIL_PASSWORD'] = 'your_app_password_here'      # Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'  # Same Gmail
```

To get a Gmail App Password:
1. Go to Google Account > Security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate a new password for "Mail"
5. Use that password in the config

---

## 8. Run the App

### Step 1: Make sure you're in the project folder:
```bash
cd /var/www/html/python
```

### Step 2: Activate virtual environment:
```bash
source venv/bin/activate
```

### Step 3: Run the Flask app:
```bash
python app.py
```

### You should see:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to stop
```

### To stop the server:
Press `CTRL + C` in the terminal.

---

## 9. Open in Browser

Once the app is running, open your web browser and go to:

```
http://127.0.0.1:5000
```

or

```
http://localhost:5000
```

### App Pages:

| URL | Page |
|-----|------|
| `/login` | Login page |
| `/register` | Create new account |
| `/dashboard` | User dashboard (after login) |
| `/profile` | View profile |
| `/profile/edit` | Edit profile |
| `/notes` | View all notes |
| `/notes/add` | Create a new note |
| `/search` | Search notes |
| `/upload-image` | Upload profile picture |
| `/upload-file` | Upload/download files |
| `/send-email` | Send an email |
| `/contact` | Contact form |
| `/messages` | View contact messages |
| `/api/notes` | API - Get notes as JSON |
| `/api/profile` | API - Get profile as JSON |
| `/logout` | Logout |

---

## 10. Run Other Python Scripts (ML)

These are standalone Machine Learning scripts. Run them separately (not part of the Flask app):

```bash
# Make sure venv is activated
source venv/bin/activate

# House price prediction (simple linear regression)
python main.py

# Student marks analysis
python student_marks.py

# Spam email classifier
python spam_classifier.py

# Multi-feature house price prediction
python multi_house_price.py

# ML features demo
python features.py
```

---

## 11. Common Errors & Fixes

### Error: `command not found: python`
**Fix:** Use `python3` instead of `python`:
```bash
python3 app.py
```

### Error: `ModuleNotFoundError: No module named 'flask'`
**Fix:** Activate virtual environment first:
```bash
source venv/bin/activate
pip install flask
```

### Error: `Can't connect to MySQL server`
**Fix:** Start MySQL service:
```bash
# Linux
sudo systemctl start mysql

# Mac
brew services start mysql
```

### Error: `Access denied for user 'root'@'localhost'`
**Fix:** Check your MySQL password in `app.py` matches your actual MySQL password.

### Error: `Unknown database 'python'`
**Fix:** Create the database first (see Step 4).

### Error: `Table 'python.users' doesn't exist`
**Fix:** Create the tables (see Step 4).

### Error: `Address already in use`
**Fix:** Another app is using port 5000. Either stop it or run Flask on a different port:
```bash
python app.py
```
Or change the last line in `app.py` to:
```python
app.run(debug=True, port=5001)
```

### Error: `PermissionError` on Linux
**Fix:** Use sudo or fix folder permissions:
```bash
sudo chmod -R 755 /var/www/html/python
```

---

## 12. Useful Commands Cheat Sheet

### Terminal Basics:
```bash
cd /var/www/html/python       # Go to project folder
ls                             # List files in current folder
pwd                            # Show current folder path
clear                          # Clear the terminal screen
```

### Virtual Environment:
```bash
python3 -m venv venv           # Create virtual environment (one time)
source venv/bin/activate       # Activate (Linux/Mac)
venv\Scripts\activate          # Activate (Windows)
deactivate                     # Deactivate
```

### Pip (Package Manager):
```bash
pip install package_name       # Install a package
pip install -r requirements.txt  # Install all packages from file
pip list                       # Show installed packages
pip freeze > requirements.txt  # Save installed packages to file
pip uninstall package_name     # Remove a package
```

### Run the App:
```bash
python app.py                  # Start Flask server
CTRL + C                       # Stop Flask server
```

### MySQL:
```bash
mysql -u root -p               # Login to MySQL
```
```sql
SHOW DATABASES;                -- List all databases
USE python;                    -- Select database
SHOW TABLES;                   -- List all tables
SELECT * FROM users;           -- View all users
SELECT * FROM notes;           -- View all notes
EXIT;                          -- Quit MySQL
```

### Git (Version Control):
```bash
git init                       # Initialize git in project
git add .                      # Stage all files
git commit -m "your message"   # Save changes
git status                     # Check what changed
git log                        # View commit history
```

---

## Quick Start Summary

Run these commands in order to get started:

```bash
# 1. Go to project folder
cd /var/www/html/python

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install packages
pip install flask flask-bcrypt flask-mail pymysql

# 4. Set up database (run in MySQL)
# mysql -u root -p < (paste SQL from Step 4)

# 5. Run the app
python app.py

# 6. Open browser: http://localhost:5000
```

---

**Happy Coding!**
