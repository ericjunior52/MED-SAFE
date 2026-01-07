from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)  # <-- this line MUST be at the top

# Dummy credentials
USERNAME = "admin"
PASSWORD = "1234"

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == admin and password == 123:
            # Redirect to dashboard after successful login
            return redirect(url_for('dashboard'))

        else:
            return "Invalid credentials, please try again."

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)

    # Drug interaction database (example)
drug_interactions = {
    "aspirin": {"ibuprofen", "warfarin"},
    "ibuprofen": {"aspirin", "prednisone"},
    "warfarin": {"aspirin"},
    "prednisone": {"ibuprofen"},
    "paracetamol": set()  # no known interactions here
}
def check_interactions(medications):
    interactions_found = []

    meds = [med.lower().strip() for med in medications]

    for i in range(len(meds)):
        for j in range(i + 1, len(meds)):
            drug1 = meds[i]
            drug2 = meds[j]

            if drug1 in drug_interactions:
                if drug2 in drug_interactions[drug1]:
                    interactions_found.append(f"{drug1} interacts with {drug2}")

    return interactions_found

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    results = []

    if request.method == 'POST':
        user_input = request.form.get('medications')
        medications = user_input.split(',')
        results = check_interactions(medications)

        if not results:
            results.append("No known interactions found.")

    return render_template('dashboard.html', results=results)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        # Get the list of medications from the form
        meds = request.form['medications']
        meds_list = [m.strip() for m in meds.split(',')]  # Split by commas
        
        # For now, just print them (we'll add interaction checking later)
        return f"You entered: {meds_list}"

    return '''
        <h2>Dashboard</h2>
        <form method="post">
            Enter medications (comma separated): <br>
            <input type="text" name="medications" placeholder="e.g., Aspirin, Ibuprofen">
            <input type="submit" value="Check Interactions">
        </form>
    '''

