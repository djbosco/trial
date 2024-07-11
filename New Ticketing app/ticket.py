from flask_mail import Mail, Message
from app import app, mail, User

def notify_staff(ticket):
    assigned_staff = User.query.get(ticket.assigned_staff_id)
    if assigned_staff and assigned_staff.email:
        msg = Message('New Ticket Assigned',
                      recipients=[assigned_staff.email])
        msg.body = f"Ticket Title: {ticket.title}\nDescription: {ticket.description}\nPriority: {ticket.priority}"
        mail.send(msg)
