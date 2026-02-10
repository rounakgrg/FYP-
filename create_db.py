import MySQLdb
import sys

try:
    # Connect to MySQL Server (assume localhost, port 3306)
    db = MySQLdb.connect(
        host="localhost",
        user="user",
        passwd="1234"
    )
    cursor = db.cursor()
    
    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS municipal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("Successfully created/verified database 'municipal_db'")
    
    db.close()
except MySQLdb.Error as e:
    print(f"Error connecting to MySQL: {e}")
    sys.exit(1)
