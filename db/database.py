import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host="localhost", user="root", password="Test1234", database="test_db"):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if self.connection.is_connected():
                self.database = database
                print("Successfully connected to the database.")
        except Error as e:
            print(f"Error: {e}")
            self.connection = None
    
    def execute(self, query, params=()):
        if self.connection is None:
            print("No connection to the database.")
            return None
        print(query, params, "******")
        
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, params)
                self.connection.commit()
                return cursor
            except Error as ex:
                self.connection.rollback()
                print(f"Error executing query: {ex}")
                return None
            
    def execute_query(self, query, params=()):
        if self.connection is None:
            print("No connection to the database.")
            return None
        
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, params)
                return cursor.fetchall() 
            except Error as ex:
                print(f"Error executing query: {ex}")
                return None

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Connection closed.")
