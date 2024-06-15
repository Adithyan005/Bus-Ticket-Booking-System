from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def init_mysql_db():
    """Connects to the MySQL server, creates the database if it doesn't exist, and creates tables."""
    try:
        conn = mysql.connector.connect(
            host="localhost",  # Replace with your MySQL host
            user="root",  # Replace with your MySQL username
            password="dinesh@2004"  # Replace with your MySQL password
        )
        cursor = conn.cursor()

        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS your_database")
        cursor.execute("USE your_database")

        # Create tables
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password TEXT NOT NULL
        );''')
        cursor.execute("CREATE TABLE IF NOT EXISTS bus(id int AUTO_INCREMENT PRIMARY KEY, origin VARCHAR(225) NOT NULL, destination VARCHAR(225) NOT NULL, bus_name VARCHAR(225) NOT NULL,date_of_travel DATE);")
        cursor.execute('''CREATE TABLE IF NOT EXISTS ticket(
            id INT AUTO_INCREMENT PRIMARY KEY,
            no_of_persons INT,
            bid INT not null,
            uid INT not null,
            foreign key(bid) references bus(id),
            foreign key(uid) references users(id)
        );''')
        print("MySQL database connected and tables created successfully")
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL database: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

init_mysql_db()

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/admin')
def admin():
    conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dinesh@2004",
            database="your_database"
        )
    cursor = conn.cursor()
    cursor.execute("select * from bus")
    data = cursor.fetchall()
    conn.close()
    return render_template('admin.html',data=data)

@app.route('/new_bus',methods=['POST'])
def new_bus():
    origin=request.form['origin']
    destination=request.form['des']
    bus_name=request.form['bus']
    date_of_travel=request.form['dot']
    conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dinesh@2004",
            database="your_database"
        )
    cursor = conn.cursor()
    cursor.execute("insert into bus (origin, destination, bus_name,date_of_travel) values(%s,%s,%s,%s)",(origin, destination, bus_name,date_of_travel))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin'))
@app.route('/delete_bus/<int:id>')
def delete_bus(id):
    conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dinesh@2004",
            database="your_database"
        )
    cursor = conn.cursor()
    cursor.execute("delete from ticket where bid =%s",(id,))
    cursor.execute("delete from bus where id =%s",(id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username=='admin' and password=='12345':
            session['username']='admin'
            session['uid']=-1
            return redirect(url_for('admin'))
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dinesh@2004",
            database="your_database"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['username']=user[1]
            session['uid'] = user[0]
            return redirect(url_for('main'))
        else:
            return "Invalid username or password"

    return render_template('login.html')

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match"

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dinesh@2004",
            database="your_database"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "Username already taken"

        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        conn.close()

        return render_template("main.html")

    return render_template('signup.html')

@app.route('/profile/')
def profile():
    if 'username' in session:
        return render_template('profile.html')
    return redirect(url_for('login'))

@app.route('/logout/')
def logout():
    session.pop('username', None)
    return redirect(url_for('main'))

@app.route('/booking', methods=['POST', 'GET'])
def booking():
    if request.method == 'POST':
        origin = request.form['orgin']
        destination = request.form['destination']
        date_of_booking = request.form['date']
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dinesh@2004",
            database="your_database"
        )
        cursor = conn.cursor()
        cursor.execute("select * from bus where origin=%s and destination=%s and  date_of_travel=%s;",(origin, destination, date_of_booking))
        data=cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('buslist.html',data=data)
    return render_template('booking.html')

@app.route('/book/<int:id>',methods=['POST'])
def book(id):
    no_of_persons = request.form['nop']
    conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dinesh@2004",
            database="your_database"
        )
    cursor = conn.cursor()
    cursor.execute("insert into ticket (bid,uid,no_of_persons) values(%s,%s,%s)",
                       (id, session['uid'], no_of_persons))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('show'))

@app.route('/show')
def show():
    conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dinesh@2004",
            database="your_database"
        )
    cursor = conn.cursor()
    cursor.execute("select t.id,b.origin,b.destination,b.date_of_travel,t.no_of_persons from ticket t inner join bus b where b.id = t.bid and t.uid = %s;",(session['uid'],))
    data = cursor.fetchall()
    conn.close()
    return render_template('booked.html',data=data)


@app.route('/delete/<int:id>',methods=['get'])
def deletebooking(id):
    conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dinesh@2004",
            database="your_database"
        )
    cursor = conn.cursor()
    cursor.execute("delete from ticket where id=%s;",(id,))
    conn.commit()
    return redirect(url_for('show'))
if __name__ == '__main__':
    app.run(debug=True)
