from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DATABASE = "hardware.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/inventory", methods=["GET"])
def inventory():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Inventory
        ORDER BY component_name
    """)

    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/reserve", methods=["POST"])
def reserve():

    data = request.get_json()

    student_name = data["student_name"]
    role = data["role"]
    inventory_id = data["inventory_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM Users WHERE student_name=?",
        (student_name,)
    )

    user = cursor.fetchone()

    if user:
        user_id = user["id"]
    else:
        cursor.execute(
            "INSERT INTO Users(student_name, role) VALUES(?,?)",
            (student_name, role)
        )
        user_id = cursor.lastrowid

    cursor.execute(
        "SELECT available_qty FROM Inventory WHERE id=?",
        (inventory_id,)
    )

    item = cursor.fetchone()

    if item["available_qty"] <= 0:
        conn.close()
        return jsonify({"message":"Item Not Available"})

    cursor.execute("""
        INSERT INTO Reservations(user_id,inventory_id,status)
        VALUES(?,?,?)
    """,(user_id,inventory_id,"Active"))

    cursor.execute("""
        UPDATE Inventory
        SET available_qty=available_qty-1
        WHERE id=?
    """,(inventory_id,))

    conn.commit()
    conn.close()

    return jsonify({"message":"Reservation Successful!"})


@app.route("/api/reservations", methods=["GET"])
def reservations():

    conn=get_db_connection()
    cursor=conn.cursor()

    cursor.execute("""
        SELECT
        Reservations.id,
        Users.student_name,
        Users.role,
        Inventory.component_name,
        Reservations.status,
        Reservations.reservation_date
        FROM Reservations
        JOIN Users
        ON Reservations.user_id=Users.id
        JOIN Inventory
        ON Reservations.inventory_id=Inventory.id
        ORDER BY Reservations.id DESC
    """)

    rows=cursor.fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/return/<int:reservation_id>", methods=["POST"])
def return_item(reservation_id):

    conn=get_db_connection()
    cursor=conn.cursor()

    cursor.execute("""
        SELECT inventory_id,status
        FROM Reservations
        WHERE id=?
    """,(reservation_id,))

    reservation=cursor.fetchone()

    if reservation is None:

        conn.close()

        return jsonify({"message":"Reservation Not Found"})

    if reservation["status"]=="Returned":

        conn.close()

        return jsonify({"message":"Already Returned"})

    inventory_id=reservation["inventory_id"]

    cursor.execute("""
        UPDATE Reservations
        SET status='Returned'
        WHERE id=?
    """,(reservation_id,))

    cursor.execute("""
        UPDATE Inventory
        SET available_qty=available_qty+1
        WHERE id=?
    """,(inventory_id,))

    conn.commit()

    conn.close()

    return jsonify({"message":"Equipment Returned Successfully"})


@app.route("/api/dashboard")
def dashboard():

    conn=get_db_connection()
    cursor=conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Inventory")
    total_items=cursor.fetchone()[0]

    cursor.execute("SELECT SUM(available_qty) FROM Inventory")
    available=cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Reservations WHERE status='Active'")
    reserved=cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Users")
    users=cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "total_items":total_items,
        "available":available,
        "reserved":reserved,
        "users":users
    })


if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
