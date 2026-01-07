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

        if username == USERNAME and password == PASSWORD:
            # Redirect to dashboard after successful login
            return render_template('dashboard.html', username=username)
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

