from flask import Flask, render_template, request, redirect, session
import sqlite3


app = Flask(__name__)
app.secret_key = 'admin_secret_key'


# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            qualification TEXT,
            marks REAL,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')


# ---------------- STUDENT REGISTRATION ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        qualification = request.form['qualification']
        marks = request.form['marks']

        conn = sqlite3.connect('students.db')
        c = conn.cursor()

        name = name.strip()
        qualification = qualification.strip()

        c.execute(
            "SELECT * FROM students WHERE name=? AND qualification=?",
            (name, qualification)
        )
        existing = c.fetchone()

        if existing:
            conn.close()
            return "Student already registered!"
        else:
            c.execute(
                "INSERT INTO students (name, qualification, marks, status) VALUES (?, ?, ?, ?)",
                (name, qualification, marks, "Pending")
            )
            conn.commit()
            conn.close()
            return "Registration Successful! Status: Pending"

    return render_template('register.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Simple admin credentials
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect('/admin')
        else:
            error = "Invalid Admin Credentials"

    return render_template('admin_login.html', error=error)


# ---------------- ADMIN PANEL ----------------
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/admin_login')

    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT name, qualification, marks, status FROM students")
    students = c.fetchall()
    conn.close()
    return render_template('admin.html', students=students)


@app.route('/select/<name>')
def select_student(name):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("UPDATE students SET status=? WHERE name=?", ("Selected", name))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/reject/<name>')
def reject_student(name):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("UPDATE students SET status=? WHERE name=?", ("Rejected", name))
    conn.commit()
    conn.close()
    return redirect('/admin')

# ---------------- STUDENT STATUS ----------------
@app.route('/status', methods=['GET', 'POST'])
def status():
    status = None
    error = None

    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("SELECT status FROM students WHERE name=?", (name,))
        result = c.fetchone()
        conn.close()

        if result:
            status = result[0]
        else:
            error = "Student not found"

    return render_template('status.html', status=status, error=error)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run()
