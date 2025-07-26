from flask import Flask, render_template, request, redirect, flash
import mysql.connector
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Database config

import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # No password
    database="ujwal_enterprises"
)





@app.route('/', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        cursor = db.cursor()
        sql = "INSERT INTO contact_messages (name, email, phone, message) VALUES (%s, %s, %s, %s)"
        values = (name, email, phone, message)
        cursor.execute(sql, values)
        db.commit()
        cursor.close()

        flash("Message submitted successfully!", "success")
        return redirect('/')

    return render_template('index.html')
