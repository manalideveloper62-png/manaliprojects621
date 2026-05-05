import sqlite3
import os

db_path = r'E:\Personal EdTech Platform (2)\minIO\storage\metadata.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Update NEET to Yakeen 2.0 2026
    cursor.execute("UPDATE batches SET title='Yakeen 2.0 2026' WHERE title LIKE '%NEET%'")
    conn.commit()
    print(f'Updated {cursor.rowcount} batches')
    conn.close()
else:
    print('Database not found')
