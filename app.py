from flask import Flask, request, jsonify, render_template, redirect, send_file, Response, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from functools import wraps
import csv
import io
import os
from flask import Flask

app = Flask(__name__)

# Set secret_key from the environment variable, or default to 'dev' for development
app.secret_key = os.environ.get('SECRET_KEY', '1234')


services = [
    {
        "title": "General Checkup",
        "image": "general.png",
        "description": "Routine health exams to maintain your well-being."
    },
    {
        "title": "Pediatrics",
        "image": "child.png",
        "description": "Dedicated care for infants, children, and teens."
    },
    {
        "title": "Diabetes Management",
        "image": "diabetes.jpg",
        "description": "Personalized plans to manage diabetes effectively."
    },
        {
        "title": "Cardiology",
        "image": "car.jpg",
        "description": "Advanced heart care for cardiovascular health."
    },
    {
        "title": "Dental Care",
        "image": "dental.jpg",
        "description": "Comprehensive dental treatments to keep your smile healthy."
    }
]


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appointments.db'
db = SQLAlchemy(app)
CORS(app)

# Database model
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    date = db.Column(db.String(100))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')

# Basic Auth for admin
def check_auth(username, password):
    return username == 'admin' and password == '1234'

def authenticate():
    return Response(
        'Could not verify your access level.\nYou have to login with proper credentials.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Routes
@app.route('/')
def home():
    return render_template('index.html')

# About Us route
@app.route('/about')
def about():
    return render_template('about.html')

# Services route
@app.route('/services')
def services_page():
    return render_template('services.html', services=services)

# Gallery route
@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')



@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
   if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        date = request.form['date']
        message = request.form['message']

        new_appointment = Appointment(name=name, email=email, date=date, message=message)
        db.session.add(new_appointment)
        db.session.commit()
	
        return redirect(url_for('appointment',success='true'))


   return render_template('appointment.html')

# ✅ 👉 ADD THIS BLOCK RIGHT HERE (AFTER /admin)
@app.route('/admin/delete/<int:id>', methods=['POST'])
@requires_auth
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    db.session.delete(appointment)
    db.session.commit()
    return redirect('/admin')

@app.route('/admin/mark-done/<int:id>', methods=['POST'])
@requires_auth
def mark_done(id):
    appointment = Appointment.query.get_or_404(id)
    appointment.status = 'Completed'
    db.session.commit()
    return redirect('/admin')

from datetime import datetime

@app.route('/admin/export')
@requires_auth
def export_appointments():
    appointments = Appointment.query.all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Name', 'Email', 'Date', 'Message', 'Status'])

    for a in appointments:
        # Check if a.date is a string and convert it to datetime if needed
        if isinstance(a.date, str):
            a.date = datetime.strptime(a.date, '%Y-%m-%d')  # Adjusted format

        # Format the date as a string in the desired format
        formatted_date = a.date.strftime('%Y-%m-%d')  # Adjusted format to match '%Y-%m-%d'
        cw.writerow([a.name, a.email, formatted_date, a.message, a.status])

    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='appointments.csv')

@app.route('/admin')
@requires_auth
def admin():
    appointments = Appointment.query.all()
    return render_template('admin.html', appointments=appointments)


# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
