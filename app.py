from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# --- Login Page ---
login_page = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <h2>Login</h2>
    <form method="post">
        Username: <input type="text" name="username" placeholder="Username"><br><br>
        Password: <input type="password" name="password" placeholder="Password"><br><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
'''

# --- Dashboard Page ---
dashboard_page = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
</head>
<body>
    <h2>Dashboard</h2>
    <form method="post">
        Enter medications (comma separated): <br>
        <input type="text" name="medications" placeholder="e.g., Aspirin, Ibuprofen"><br><br>
        <input type="submit" value="Check Interactions">
    </form>
    {% if meds_list %}
        <h3>You entered:</h3>
        <ul>
        {% for med in meds_list %}
            <li>{{ med }}</li>
        {% endfor %}
        </ul>
    {% endif %}
</body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == '123':
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials. Please go back and try again."

    return render_template_string(login_page)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    meds_list = None
    if request.method == 'POST':
        meds = request.form['medications']
        meds_list = [m.strip() for m in meds.split(',')]
    return render_template_string(dashboard_page, meds_list=meds_list)

if __name__ == '__main__':
    app.run(debug=True)


