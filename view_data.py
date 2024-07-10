import sqlite3

def fetch_data():
    conn = sqlite3.connect('budgetbuddy.db')
    c = conn.cursor()
    c.execute('SELECT * FROM budget')
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    data = fetch_data()
    for row in data:
        print(row)
