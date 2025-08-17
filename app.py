from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)

# -------------------- DATABASE --------------------
mydb = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", 3306))
)
mycursor = mydb.cursor()

# Ensure tables exist
mycursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    dob DATE NOT NULL
)
""")

mycursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(255) NOT NULL,
    patient_email VARCHAR(255) NOT NULL,
    doctor VARCHAR(255) NOT NULL,
    appointment_date DATE NOT NULL,
    message TEXT
)
""")

mycursor.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    message TEXT NOT NULL
)
""")

# -------------------- ROUTES ---------------------

@app.route('/')
def home():
    return render_template('index.html')

# ---------------- Registration ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        dob = request.form['dob']

        sql = "INSERT INTO users (name, email, password, phone, dob) VALUES (%s, %s, %s, %s, %s)"
        val = (name, email, password, phone, dob)

        try:
            mycursor.execute(sql, val)
            mydb.commit()
            return redirect(url_for('registration_success'))
        except mysql.connector.Error as err:
            print("Error:", err)
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/registration-success')
def registration_success():
    return render_template('registration_success.html')


# ---------------- Login ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        sql = "SELECT * FROM users WHERE email=%s AND password=%s"
        val = (email, password)

        try:
            mycursor.execute(sql, val)
            user = mycursor.fetchone()
            if user:
                return redirect(url_for('appointment'))
            else:
                return redirect(url_for('login', error=True))
        except mysql.connector.Error as err:
            print("Error:", err)
            return redirect(url_for('login', error=True))

    error = request.args.get('error')
    return render_template('login.html', error=error)


# ---------------- Appointment ----------------
@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        doctor = request.form['doctor']
        date = request.form['date']
        message = request.form['message']

        sql = """
        INSERT INTO appointments (patient_name, patient_email, doctor, appointment_date, message)
        VALUES (%s, %s, %s, %s, %s)
        """
        val = (name, email, doctor, date, message)

        try:
            mycursor.execute(sql, val)
            mydb.commit()
            return redirect(url_for('appointment_success'))
        except mysql.connector.Error as err:
            print("Error:", err)
            return redirect(url_for('appointment'))

    return render_template('appointment.html')


@app.route('/appointment_success')
def appointment_success():
    return render_template('appointment_success.html')


# ---------------- Contact ----------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        sql = "INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)"
        val = (name, email, message)

        try:
            mycursor.execute(sql, val)
            mydb.commit()
            return redirect(url_for('contact_success'))
        except mysql.connector.Error as err:
            print("Error:", err)
            return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/contact_success')
def contact_success():
    return render_template('contact_success.html')


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5010)
