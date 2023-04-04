from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, current_app
    )
from app.db import get_db
from mailjet_rest import Client
import os

bp = Blueprint('mail', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
def index():
    search = request.args.get('search')
    db, c = get_db()
    if search is None:
        c.execute('SELECT * FROM email')
    else:
        c.execute("SELECT * FROM email WHERE content LIKE %s", ('%'+search+'%',))
    mails = c.fetchall()
    return render_template('mails/index.html', mails=mails)

@bp.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'POST':
        email = request.form.get('email')
        subject = request.form.get('subject')
        content = request.form.get('content')
        errors = []
        if not email:
            errors.append('Email es obligatorio')
        if not subject:
            errors.append('Asunto es obligatorio')
        if not content:
            errors.append('Contenido es obligatorio')

        if len(errors) == 0:
            send(email, subject, content)
            db,c = get_db()
            c.execute("INSERT INTO email (email, subject, content) VALUES(%s, %s, %s)",
                       (email, subject, content))
            db.commit()
            return redirect(url_for('mail.index'))
        else:
            for error in errors:
                flash(error)

    return render_template('mails/create.html')

def send(to, subject, content):
    mi_correo = current_app.config['FROM_EMAIL']
    api_key = current_app.config['MAILJET_API_KEY']
    api_secret = current_app.config['MAILJET_SECRET_KEY']
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
    'Messages': [
        {
        "From": {
            "Email": mi_correo,
            "Name": "Correo de MailJet"
        },
        "To": [
            {
            "Email": mi_correo,
            "Name": "Alejandro Gatica"
            }
        ],
        "Subject": subject,
        "TextPart": "My first Mailjet email",
        "HTMLPart":  f"<h2>Correo de: {to}</h2><br />{content}",
        "CustomID": ""
        }
    ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())