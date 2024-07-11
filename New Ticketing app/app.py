from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticketing_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'

db = SQLAlchemy(app)
mail = Mail(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    role = db.Column(db.String(50))
    email = db.Column(db.String(255))
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))

class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    branches = db.relationship('Branch', backref='region', lazy=True)

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    tickets = db.relationship('Ticket', backref='branch', lazy=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    status = db.Column(db.String(50))
    priority = db.Column(db.String(50))
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Routes
@app.route('/')
def index():
    tickets = Ticket.query.all()
    return render_template('index.html', tickets=tickets)

@app.route('/add_ticket', methods=['GET', 'POST'])
def add_ticket():
    if request.method == 'POST':
        try:
            data = request.form
            ticket = Ticket(
                title=data['title'],
                description=data['description'],
                region_id=int(data['region']),
                branch_id=int(data['branch']),
                status='Open',
                priority=data['priority'],
                assigned_staff_id=int(data['assigned_staff'])
            )
            db.session.add(ticket)
            db.session.commit()
            notify_staff(ticket)
            return redirect(url_for('index'))
        except Exception as e:
            app.logger.error(f"Error processing ticket submission: {str(e)}")
            return "Error processing ticket submission. Please try again later.", 500

    regions = Region.query.all()
    branches = Branch.query.all()
    users = User.query.all()
    return render_template('add_ticket.html', regions=regions, branches=branches, users=users)

def notify_staff(ticket):
    assigned_staff = User.query.get(ticket.assigned_staff_id)
    if assigned_staff and assigned_staff.email:
        msg = Message('New Ticket Assigned',
                      recipients=[assigned_staff.email])
        msg.body = f"Ticket Title: {ticket.title}\nDescription: {ticket.description}\nPriority: {ticket.priority}"
        mail.send(msg)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
