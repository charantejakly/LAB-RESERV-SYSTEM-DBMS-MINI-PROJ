import sqlite3

DATABASE_NAME = "hardware.db"

inventory_items = [
    ("Arduino UNO", 10, 10),
    ("ADXL345 Accelerometer", 8, 8),
    ("5-DOF Robot Base", 5, 5),
    ("Raspberry Pi 4", 4, 4),
    ("Ultrasonic Sensor HC-SR04", 15, 15),
    ("Servo Motor SG90", 20, 20),
    ("ESP32 Development Board", 12, 12),
    ("Breadboard", 25, 25),
    ("Jumper Wires Set", 30, 30),
    ("L298N Motor Driver", 10, 10)
]

try:
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Inventory(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        component_name TEXT NOT NULL,
        total_qty INTEGER NOT NULL,
        available_qty INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Reservations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        inventory_id INTEGER,
        status TEXT NOT NULL,
        reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES Users(id),
        FOREIGN KEY(inventory_id) REFERENCES Inventory(id)
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM Inventory")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            """
            INSERT INTO Inventory(component_name, total_qty, available_qty)
            VALUES (?, ?, ?)
            """,
            inventory_items
        )

    conn.commit()
    conn.close()

    print("Database created successfully!")
    print("Inventory added successfully!")

except Exception as e:
    print("Error:", e)
