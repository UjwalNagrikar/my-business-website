from flask import Flask, render_template, request, redirect, flash, url_for
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
app.secret_key = 'ujwal-enterprises-secret-key-2024'

# Database configuration for XAMPP
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'ujwal_enterprises',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✅ Connected to XAMPP MySQL database")
            return connection
    except Error as e:
        print(f"❌ Error connecting to XAMPP MySQL: {e}")
        return None

def init_database():
    """Initialize the database and create tables if they don't exist"""
    try:
        # Create database if it doesn't exist
        temp_config = DB_CONFIG.copy()
        temp_config.pop('database')
        
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ujwal_enterprises CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        print("✅ Database 'ujwal_enterprises' ready")
        cursor.close()
        connection.close()
        
        # Create table with proper schema
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("✅ Table 'contact_messages' ready")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Error initializing database: {e}")

@app.route('/', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            message = request.form.get('message', '').strip()
            
            print(f"📝 Form submission: {name} ({email})")
            
            # Validation
            if not name or not email or not message:
                flash("Please fill in all required fields (Name, Email, Message)", "error")
                return redirect(url_for('contact'))
            
            if '@' not in email or '.' not in email:
                flash("Please enter a valid email address", "error")
                return redirect(url_for('contact'))
            
            # Save to database
            connection = get_db_connection()
            if connection is None:
                flash("Database connection failed. Please try again later.", "error")
                return redirect(url_for('contact'))
            
            cursor = connection.cursor()
            sql = "INSERT INTO contact_messages (name, email, phone, message) VALUES (%s, %s, %s, %s)"
            values = (name, email, phone, message)
            cursor.execute(sql, values)
            connection.commit()
            
            message_id = cursor.lastrowid
            print(f"✅ Message saved with ID: {message_id}")
            
            cursor.close()
            connection.close()
            
            flash(f"Thank you {name}! Your message has been submitted successfully.", "success")
            return redirect(url_for('contact'))
            
        except Error as e:
            print(f"❌ Database error: {e}")
            flash("An error occurred while submitting your message. Please try again.", "error")
            return redirect(url_for('contact'))
        except Exception as e:
            print(f"❌ General error: {e}")
            flash("An unexpected error occurred. Please try again.", "error")
            return redirect(url_for('contact'))
    
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin panel to view contact messages"""
    try:
        connection = get_db_connection()
        if connection is None:
            return """
            <html>
            <head><title>Admin - Database Error</title></head>
            <body style="padding: 20px; font-family: Arial, sans-serif;">
                <h1>❌ Database Connection Failed</h1>
                <p>Could not connect to XAMPP MySQL. Make sure XAMPP MySQL service is running.</p>
                <a href="/" style="color: #3498db;">← Back to Website</a>
            </body>
            </html>
            """, 500
        
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, email, phone, message, created_at FROM contact_messages ORDER BY id DESC LIMIT 50")
        messages = cursor.fetchall()
        cursor.close()
        connection.close()
        
        # Build HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin - Contact Messages</title>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 15px; margin-bottom: 30px; }
                .stats { background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; text-align: center; font-size: 18px; font-weight: bold; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
                th { background: #2c3e50; color: white; padding: 15px 10px; text-align: left; font-weight: bold; }
                td { padding: 12px 10px; border-bottom: 1px solid #eee; vertical-align: top; }
                tr:hover { background: #f8f9fa; }
                .message-cell { max-width: 300px; word-wrap: break-word; }
                .email { color: #3498db; font-weight: 500; }
                .phone { color: #27ae60; }
                .date { color: #7f8c8d; font-size: 14px; }
                .no-messages { text-align: center; padding: 60px 20px; color: #7f8c8d; }
                .no-messages h3 { color: #95a5a6; margin-bottom: 10px; }
                .back-links { text-align: center; margin-top: 30px; }
                .btn { display: inline-block; padding: 12px 24px; margin: 0 10px; text-decoration: none; border-radius: 6px; font-weight: 500; transition: all 0.3s; }
                .btn-primary { background: #3498db; color: white; }
                .btn-primary:hover { background: #2980b9; }
                .btn-success { background: #27ae60; color: white; }
                .btn-success:hover { background: #229954; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📧 Contact Messages Dashboard</h1>
        """
        
        html += f'<div class="stats">📊 Total Messages: {len(messages)}</div>'
        
        if messages:
            html += """
                <table>
                    <thead>
                        <tr>
                            <th width="5%">ID</th>
                            <th width="15%">Name</th>
                            <th width="20%">Email</th>
                            <th width="12%">Phone</th>
                            <th width="35%">Message</th>
                            <th width="13%">Date</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for msg in messages:
                msg_id, name, email, phone, message, created_at = msg
                phone_display = phone if phone else "N/A"
                date_display = str(created_at) if created_at else "N/A"
                
                html += f"""
                        <tr>
                            <td><strong>#{msg_id}</strong></td>
                            <td>{name}</td>
                            <td class="email">{email}</td>
                            <td class="phone">{phone_display}</td>
                            <td class="message-cell">{message}</td>
                            <td class="date">{date_display}</td>
                        </tr>
                """
            
            html += """
                    </tbody>
                </table>
            """
        else:
            html += """
                <div class="no-messages">
                    <h3>📭 No Messages Yet</h3>
                    <p>When visitors submit the contact form, their messages will appear here.</p>
                </div>
            """
        
        html += """
                <div class="back-links">
                    <a href="/" class="btn btn-primary">← Back to Website</a>
                    <a href="/db-info" class="btn btn-success">🔍 Database Info</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        error_msg = str(e).replace('<', '&lt;').replace('>', '&gt;')
        return f"""
        <html>
        <head><title>Admin Error</title></head>
        <body style="padding: 20px; font-family: Arial, sans-serif;">
            <h1 style="color: #e74c3c;">❌ Error Loading Messages</h1>
            <div style="background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-radius: 6px; margin: 20px 0; font-family: monospace;">
                {error_msg}
            </div>
            <a href="/" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Back to Website</a>
        </body>
        </html>
        """, 500

@app.route('/db-info')
def db_info():
    """Database information for debugging"""
    try:
        connection = get_db_connection()
        if not connection:
            return "❌ Database connection failed"
        
        cursor = connection.cursor()
        cursor.execute("DESCRIBE contact_messages")
        columns = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM contact_messages")
        count = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        html = f"""
        <html>
        <head><title>Database Information</title></head>
        <body style="font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;">
            <div style="max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h1>🗄️ Database Information</h1>
                
                <h2>📊 Statistics:</h2>
                <p><strong>Total Records:</strong> {count}</p>
                
                <h2>📋 Table Structure:</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background: #2c3e50; color: white;">
                        <th style="padding: 10px; border: 1px solid #ddd;">Column</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Type</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Null</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Key</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Default</th>
                    </tr>
        """
        
        for col in columns:
            html += f"""
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">{col[0]}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{col[1]}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{col[2]}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{col[3]}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{col[4] or 'None'}</td>
                    </tr>
            """
        
        html += """
                </table>
                
                <div style="margin-top: 30px;">
                    <a href="/" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">← Back to Website</a>
                    <a href="/admin" style="background: #27ae60; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">👨‍💼 Admin Panel</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        return f"Error: {str(e)}"

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return "Internal Server Error - Please check the server logs", 500

if __name__ == '__main__':
    print("🚀 Starting Ujwal Global Enterprises Flask App...")
    print("📋 Make sure XAMPP MySQL is running!")
    print("🌐 Website: http://localhost:5000")
    print("👨‍💼 Admin Panel: http://localhost:5000/admin")
    print("🔍 Database Info: http://localhost:5000/db-info")
    print("-" * 60)
    
    init_database()
    app.run(debug=True, host='127.0.0.1', port=5000)