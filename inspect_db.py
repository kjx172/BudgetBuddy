import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('instance/database.db')
cursor = conn.cursor()

# Retrieve the list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

if not tables:
    print("No tables found in the database.")
else:
    for table in tables:
        table_name = table[0]
        print(f"\nContents of table '{table_name}':")
        
        # Retrieve the column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        print(" | ".join(column_names))
        
        # Retrieve the contents of the table
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        
        for row in rows:
            print(row)

# Close the connection
conn.close()
