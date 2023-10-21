import mysql.connector
import atexit
from src.config import get_config
import json



db_connection = None
db_cursor = None

def init_db_connection():
    global db_connection, db_cursor
    config = get_config()
    db_connection = mysql.connector.connect(
        host=config['mysql']['IP'],
        user=config['mysql']['username'],
        password=config['mysql']['password'],
        database=config['mysql']['DB'],
        port=config['mysql']['PORT']
    )
    db_cursor = db_connection.cursor()
    atexit.register(close_db_connection)

def close_db_connection():
    global db_connection, db_cursor
    if db_cursor:
        db_cursor.close()
    if db_connection:
        db_connection.close()

def create_table():
    global db_connection, db_cursor
    # 確保數據庫連接已經初始化
    if db_connection is None or db_cursor is None:
        print("Database connection has not been initialized. Call init_db_connection first.")
        return
    
    # 您可以根據需要修改以下SQL語句
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS HeartbeatData (
        id INT AUTO_INCREMENT PRIMARY KEY,
        mac_address VARCHAR(255) NOT NULL,
        heartbeat_value INT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        db_cursor.execute(create_table_sql)
        db_connection.commit()
        print("Table created successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db_connection.rollback()  # 如果出現錯誤，回滾事務



def save_to_sql(mac_address, heartbeat_value):
    try:
        # Load configuration
        with open('./src/config.json', 'r') as config_file:
            config = json.load(config_file)

        # Connect to the database
        connection = mysql.connector.connect(
            host=config['mysql']['IP'],
            user=config['mysql']['username'],
            password=config['mysql']['password'],
            database=config['mysql']['DB'],
            port=config['mysql']['PORT']
        )

        if connection is None:
            print("Failed to connect to the database.")
            return

        cursor = connection.cursor()

        # Insert data into the database
        sql = f"INSERT INTO {config['mysql']['TABLES']} (mac_address, heartbeat) VALUES (%s, %s)"
        
        # Print SQL query for debugging purposes
        print(f"Executing SQL: {sql}")

        cursor.execute(sql, (mac_address, heartbeat_value))
        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

