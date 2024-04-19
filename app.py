from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import sqlite3
import datetime
import csv

app = Flask(__name__)
app.secret_key = '12345'

# Function to write to the log
def log_change(change_type, name, organization_type, resources_available, contact_person, contact_email, contact_phone):
    """
    Log changes made to partner information.

    Args:
        change_type (str): Type of change (e.g., Added, Deleted, Updated).
        name (str): Name of the partner.
        organization_type (str): Type of organization.
        resources_available (str): Available resources.
        contact_person (str): Contact person's name.
        contact_email (str): Contact person's email.
        contact_phone (str): Contact person's phone number.
    """
    with open('log.txt', 'a') as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{name}~~{timestamp}~~{change_type}~~{organization_type}~~{resources_available}~~{contact_person}~~{contact_email}~~{contact_phone}\n")

# Function to fetch log data from log.txt
def get_log_data():
    """
    Retrieve log data from the log file.

    Returns:
        list: List of log entries.
    """
    log_data = []
    try:
        with open('log.txt', 'r') as file:
            for line in file:
                fields = line.strip().split('~~')
                log_data.append(fields)
    except FileNotFoundError:
        pass
    return log_data

# Route to serve images
@app.route('/images/<path:filename>')
def serve_image(filename):
    """
    Route to serve images from the static directory.

    Args:
        filename (str): Name of the image file.

    Returns:
        obj: Image file.
    """
    image_directory = 'static/images'
    return send_from_directory(image_directory, filename)

# Routes for help menus
@app.route('/help')
def help():
    """Route to display general help."""
    return render_template('help_menus/help.html')

@app.route('/adding_help')
def adding_help():
    """Route to display help for adding partners."""
    return render_template('help_menus/adding_help.html')

@app.route('/editing_help')
def editing_help():
    """Route to display help for editing partners."""
    return render_template('help_menus/editing_help.html')

@app.route('/deleting_help')
def deleting_help():
    """Route to display help for deleting partners."""
    return render_template('help_menus/deleting_help.html')

@app.route('/searching_help')
def searching_help():
    """Route to display help for searching partners."""
    return render_template('help_menus/searching_help.html')

@app.route('/sorting_help')
def sorting_help():
    """Route to display help for sorting partners."""
    return render_template('help_menus/sorting_help.html')

@app.route('/reporting_help')
def report_help():
    """Route to display help for generating reports."""
    return render_template('help_menus/report_help.html')

@app.route('/events')
# Route to generate action log report
def events():
    # Connect to SQLite database
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Retrieve events created by the user
    events = cursor.execute("SELECT * FROM events").fetchall()
    
    
    conn.close()

    return render_template('events.html', events=events)
# Route for the main page (index)
@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Route for the main page.

    Returns:
        obj: Rendered template of the main page.
    """
    conn = sqlite3.connect('partnerdb.sqlite')
    cursor = conn.cursor()
    query = request.args.get('q')
    if query:
        partners = cursor.execute("SELECT * FROM partners WHERE name LIKE ? OR role LIKE ? OR service_type LIKE ? OR available_days LIKE ? OR contact_email LIKE ? OR contact_phone LIKE ?", 
                                  ('%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%')).fetchall()
    else:
        partners = cursor.execute("SELECT * FROM partners").fetchall()
    conn.close()
    return render_template('index.html', partners=partners)

@app.route('/report')
def generate_report():
    """
    Route to generate an action log report.

    Returns:
        obj: Rendered template of the report.
    """
    log_data = get_log_data()
    query = request.args.get('q')
    if query:
        log_data = [entry for entry in log_data if query.lower() in ' '.join(entry).lower()]
    return render_template('report.html', log_data=log_data)

@app.route('/add_event', methods=['GET'])
def add_event_form():
    conn = sqlite3.connect('partnerdb.sqlite')
    cursor = conn.cursor()
    partners = cursor.execute("SELECT * FROM partners").fetchall()
    query = request.args.get('q')
    if query:
        partners1 = cursor.execute("SELECT * FROM partners WHERE name LIKE ? OR role LIKE ? OR service_type LIKE ? OR available_days LIKE ? OR contact_email LIKE ? OR contact_phone LIKE ?", 
                                  ('%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%')).fetchall()
    else:
        partners1 = cursor.execute("SELECT * FROM partners").fetchall()
    conn.close()
    return render_template('add_event.html', partners=partners,partners1=partners1)

# Route to handle the form submission and add the new event to the database
@app.route('/add_event', methods=['POST'])
def add_event():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        date = request.form['date']
        people_attending = request.form.getlist('people_attending[]')
        conn = sqlite3.connect('partnerdb.sqlite')
        cursor = conn.cursor()
        emails = []
        for i in people_attending:
            emails.append(cursor.execute("SELECT contact_email FROM partners WHERE name=?", (i,)).fetchone()[0])
        people_attending = ','.join(people_attending)
        emails = ','.join(emails)
        # Connect to SQLite database
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()

        # Insert new event into the database
        cursor.execute("INSERT INTO events (name, location, date, people_attending, participant_emails) VALUES (?, ?, ?, ?, ?)",
                       (name, location, date, people_attending, emails))
        conn.commit()
        conn.close()

        # Redirect to the events page after adding the event
        return redirect(url_for('events'))
# Route to add a new partner
@app.route('/add_partner', methods=['GET', 'POST'])
def add_partner():
    """
    Route to add a new partner.

    Returns:
        obj: Redirect to the main page after adding the partner or render the add partner template.
    """
    if request.method == 'POST':
        name = request.form['name']
        organization_type = request.form['role']
        resources_available = request.form['service_type']
        contact_person = request.form['available_days']
        contact_email = request.form['contact_email']
        contact_phone = request.form['contact_phone']
        conn = sqlite3.connect('partnerdb.sqlite')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO partners (name, role, service_type, available_days, contact_email, contact_phone) VALUES (?, ?, ?, ?, ?, ?)", 
                       (name, organization_type, resources_available, contact_person, contact_email, contact_phone))
        conn.commit()
        conn.close()
        log_change("Added Partner", name, organization_type, resources_available, contact_person, contact_email, contact_phone)
        return redirect(url_for('index'))
    return render_template('add_partner.html')

def allowed_file(filename):
    """
    Check if the filename has an allowed file extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    ALLOWED_EXTENSIONS = {'csv'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_csv_data', methods=['POST'])
def add_csv_data():
    """
    Route to add data from a CSV file to the database.

    Returns:
        obj: Redirect to the main page after adding the data or render a template.
    """
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        # Read data from CSV file
        csv_data = file.read().decode("utf-8").splitlines()
        reader = csv.reader(csv_data)
        
        # Connect to SQLite database
        conn = sqlite3.connect('partnerdb.sqlite')
        cursor = conn.cursor()

        # Iterate over CSV rows and insert data into the 'partners' table
        for idx, row in enumerate(reader):
            if idx == 0: 
                continue
            
            timestamp, name, organization_type, resources_available, contact_person, contact_email, contact_phone = row
            log_change("Added", name, organization_type, resources_available, contact_person, contact_email, contact_phone)
            cursor.execute("INSERT INTO partners (name, role, service_type, available_days, contact_email, contact_phone) VALUES (?, ?, ?, ?, ?, ?)", 
                           (name, organization_type, resources_available, contact_person, contact_email, contact_phone))

        conn.commit()  # Commit the transaction
        conn.close()   # Close the database connection

        flash('Data from CSV file added successfully')
        return redirect(url_for('index'))
    
    flash('Invalid file type')
    return redirect(url_for('index'))


# Route to delete a partner
@app.route('/delete_partner/<int:partner_id>', methods=['POST'])
def delete_partner(partner_id):
    """
    Route to delete a partner.

    Args:
        partner_id (int): ID of the partner to delete.

    Returns:
        obj: Redirect to the main page after deleting the partner or render the delete partner template.
    """
    conn = sqlite3.connect('partnerdb.sqlite')
    cursor = conn.cursor()
    partner = cursor.execute("SELECT * FROM partners WHERE id = ?", (partner_id,)).fetchone()
    if request.method == 'POST':
        cursor.execute("DELETE FROM partners WHERE id = ?", (partner_id,))
        conn.commit()
        conn.close()
        log_change("Deleted", partner[1], partner[2], partner[3], partner[4], partner[5], partner[6])
        return redirect(url_for('index'))
    conn.close()
    return render_template('delete_partner.html', partner=partner)

# Route to retrieve partner information
def get_partner_info(name):
    """
    Retrieve partner information from the log.

    Args:
        name (str): Name of the partner.

    Returns:
        dict: Partner information.
    """
    partner_info = {}
    try:
        with open('log.txt', 'r') as file:
            for line in file:
                fields = line.strip().split('~~')
                if fields[0] == name:
                    partner_info['name'] = fields[0]
                    partner_info['timestamp'] = fields[1]
                    partner_info['change_type'] = fields[2]
                    partner_info['organization_type'] = fields[3]
                    partner_info['resources'] = fields[4]
                    partner_info['contact_person'] = fields[5]
                    partner_info['contact_email'] = fields[6]
                    partner_info['contact_phone'] = fields[7]
                    break
    except FileNotFoundError:
        pass
    return partner_info

# Route to display partner information
@app.route('/partner_info/<name>')
def partner_info(name):
    """
    Route to display partner information.

    Args:
        name (str): Name of the partner.

    Returns:
        obj: Rendered template of the partner information.
    """
    partner = get_partner_info(name)
    return render_template('partner_info.html', partner=partner)

# Route to edit partner information
@app.route('/edit_partner/<int:partner_id>', methods=['GET', 'POST'])
def edit_partner(partner_id):
    """
    Route to edit partner information.

    Args:
        partner_id (int): ID of the partner to edit.

    Returns:
        obj: Redirect to the main page after editing the partner or render the edit partner template.
    """
    conn = sqlite3.connect('partnerdb.sqlite')
    cursor = conn.cursor()
    partner = cursor.execute("SELECT * FROM partners WHERE id = ?", (partner_id,)).fetchone()
    if request.method == 'POST':
        name = request.form['name']
        organization_type = request.form['organization_type']
        resources_available = request.form['resources_available']
        contact_person = request.form['contact_person']
        contact_email = request.form['contact_email']
        contact_phone = request.form['contact_phone']
        cursor.execute("UPDATE partners SET name=?, role=?, service_type=?, available_days=?, contact_email=?, contact_phone=? WHERE id=?", 
                       (name, organization_type, resources_available, contact_person, contact_email, contact_phone, partner_id))
        conn.commit()
        conn.close()
        log_change("Updated", name, organization_type, resources_available, contact_person, contact_email, contact_phone)
        return redirect(url_for('index'))
    conn.close()
    return render_template('edit_partner.html', partner=partner)

# Route to sort partners alphabetically by name
@app.route('/sort_partners', methods=['POST'])
def sort_partners():
    """
    Route to sort partners alphabetically by name.

    Returns:
        obj: Rendered template of the sorted partners.
    """
    conn = sqlite3.connect('partnerdb.sqlite')
    cursor = conn.cursor()
    partners = cursor.execute("SELECT * FROM partners ORDER BY name").fetchall()
    conn.close()
    return render_template('index.html', partners=partners)

if __name__ == '__main__':
    app.run(debug=True)
