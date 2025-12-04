from flask import Flask, redirect, request, render_template, url_for, session, jsonify, flash, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from db import db, Userers, Event, Registration, Admin
from sqlalchemy.orm import joinedload
import smtplib
import ssl
import random
import os

# from flask_mail import Mail, Message

import os
from flask import Flask
from db import db   # your db object from db.py

app = Flask(__name__)
app.secret_key = 'somethingfishy'

# 1️⃣ DATABASE CONFIG
# Use PostgreSQL on Render (DATABASE_URL), otherwise fallback to SQLite locally
db_path = os.path.join(os.getcwd(), "hackathon.sqlite3")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",                # Render Postgres
    "sqlite:///" + db_path         # Local SQLite fallback
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

# 2️⃣ INITIALIZE DB
db.init_app(app)

# 3️⃣ CREATE TABLES ON START
with app.app_context():
    db.create_all()




#-------------------------------------------------------------------------------------------

import os
import random
from flask import session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY_NEW")
# SENDGRID_API_KEY = SENDGRID_API_KEY_NEW

SENDER_EMAIL = "ivinjose.work@gmail.com"   # must be verified in SendGrid


def send_otp(user_email):
    if not SENDGRID_API_KEY:
        print("ERROR: SENDGRID_API_KEY_NEW is not set")
        return None

    otp = str(random.randint(1000, 9999))
    session['verification_otp'] = otp

    subject = "Your Verification Code"
    body = f"Your OTP is: {otp}"

    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=user_email,
        subject=subject,
        plain_text_content=body,
    )

    try:
        print("=== SENDING OTP VIA SENDGRID API TO:", user_email)
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print("=== OTP SEND STATUS ===", response.status_code)
        # 202 is SendGrid's "accepted" status
        if response.status_code == 202:
            return otp
        else:
            return None
    except Exception as e:
        print("=== OTP SEND FAILED (API) ===", repr(e))
        return None



# import smtplib
# import ssl
# import random
# from email.message import EmailMessage

# SMTP_SERVER = "smtp.sendgrid.net"
# PORT = 587
# USERNAME = "apikey"
# PASSWORD = os.getenv("SENDGRID_API_KEY_NEW")  # MUST be set in Render env
# SENDER_EMAIL = "ivinjose.work@gmail.com"      # verified sender in SendGrid


# def send_otp(user_email):
#     # Check env var first
#     if not PASSWORD:
#         print("ERROR: SENDGRID_APIKEY_NEW is not set in environment")
#         return None

#     otp = str(random.randint(1000, 9999))
#     session['verification_otp'] = otp

#     subject = "Your Verification Code"
#     body = f"Your OTP is: {otp}"

#     # Build proper email
#     msg = EmailMessage()
#     msg["From"] = SENDER_EMAIL
#     msg["To"] = user_email
#     msg["Subject"] = subject
#     msg.set_content(body)

#     context = ssl.create_default_context()

#     try:
#         print("=== SENDING OTP TO:", user_email)
#         with smtplib.SMTP(SMTP_SERVER, PORT, timeout=10) as server:  # timeout added
#             server.ehlo()
#             server.starttls(context=context)
#             server.ehlo()
#             server.login(USERNAME, PASSWORD)
#             server.send_message(msg)
#         print("=== OTP SEND SUCCESS ===")
#         return otp
#     except Exception as e:
#         print("=== OTP SEND FAILED ===", repr(e))
#         return None



# SMTP_SERVER = "smtp.sendgrid.net"
# PORT = 587
# USERNAME = "apikey"
# PASSWORD = os.getenv("SENDGRID_API_KEY_NEW")  # Read from environment
# SENDER_EMAIL = "ivinjose.work@gmail.com"

# def send_otp(user_email):
#     otp = str(random.randint(1000, 9999))
#     session['verification_otp'] = otp

#     subject = "Your Verification Code"
#     body = f"Your OTP is: {otp}"

#     message = f"""From: {SENDER_EMAIL}
# To: {user_email}
# Subject: {subject}

# {body}
# """

#     context = ssl.create_default_context()

#     with smtplib.SMTP(SMTP_SERVER, PORT) as server:
#         server.starttls(context=context)
#         server.login(USERNAME, PASSWORD)
#         server.sendmail(SENDER_EMAIL, user_email, message)

#     return otp

#-------------------------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("errors/500.html"), 500

#-------------------------------------------------------------------------------------------


def clear_sessions():
	session.clear()

#-------------------------------------------------------------------------------------------

def get_admins():
	admins = Admin.query.all()
	return admins

#-------------------------------------------------------------------------------------------

def get_users():
    users = Userers.query.all()
    return users
#-------------------------------------------------------------------------------------------

def get_registrations():
    registrations = Registration.query.all()
    return registrations

#-------------------------------------------------------------------------------------------

def get_events():
	today = datetime.utcnow().date()
	all_events = Event.query.all()
	events = [
        e for e in all_events
        if datetime.strptime(e.last_date, "%Y-%m-%d").date() >= today
    ]

	registrations = Registration.query.all()

	return events

#-------------------------------------------------------------------------------------------


def get_events_outdated():
	today = datetime.utcnow().date()
	all_events = Event.query.all()
	events = [
        e for e in all_events
        if datetime.strptime(e.last_date, "%Y-%m-%d").date() < today
    ]

	registrations = Registration.query.all()

	return events

#-------------------------------------------------------------------------------------------


def get_all_registrations_with_events():
    regs = (
        Registration.query
        .options(joinedload(Registration.event))  # eager load Event
        .order_by(Registration.created_at.desc())
        .all()
    )

    data = []
    for r in regs:
        data.append({
            "reg_id": r.reg_id,
            "userid": r.userid,
            "team_name": r.team_name,
            "email": r.email,
            "reg_date": r.reg_date,

            # member details
            "member1_name": r.member1_name,
            "member1_phone": r.member1_phone,
            "member2_name": r.member2_name,
            "member2_phone": r.member2_phone,

            # event details (from relationship)
            "event_id": r.event.event_id if r.event else None,
            "event_name": r.event.event_name if r.event else None,
            "event_date": r.event.event_date if r.event else None,
            "last_date": r.event.last_date if r.event else None,
            "description": r.event.description if r.event else None,
        })
    return data






#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------


@app.route('/home')
def home():
	registrations = Registration.query.all()
	events = get_events()
	return render_template('index.html', events=events, registrations=registrations)


#-------------------------------------------------------------------------------------------


@app.route('/login-verification', methods=['POST', 'GET'])
def login_verification():
	if 'temp_email' in session:
		error_msg = ''
		email = session['temp_email']
		if request.method == 'POST':
			n1 = request.form.get('n1')
			n2 = request.form.get('n2')
			n3 = request.form.get('n3')
			n4 = request.form.get('n4')

			otp = n1+n2+n3+n4

			if str(session['verification_otp']) == str(otp):
				user = Userers.query.filter_by(email=email).first()
				session['user_id'] = user.id
				session['user_name'] = user.username
				session['user_email'] = user.email
				session.pop('temp_email', None)
				session.pop('verification_otp', None)
				return redirect('/home')
			else:
				error_msg = "OTP Verification failed"
	else:
		return redirect('/login')

	return render_template('email_verification.html', email=email, error_msg=error_msg)


#-------------------------------------------------------------------------------------------


@app.route('/login', methods=['POST', 'GET'])
def login():
    error_msg = ''

    if request.method == 'POST':
        email = request.form.get('email')

        if not email:
            error_msg = "Email required"
            return render_template('login.html', error_msg=error_msg)

        user = Userers.query.filter_by(email=email).first()
        if user:
            session['temp_email'] = email

            otp = send_otp(email)
            if otp is None:
                # Do NOT redirect, show error
                error_msg = "Unable to send OTP right now. Please try again later."
                return render_template('login.html', error_msg=error_msg)

            return redirect(url_for('login_verification'))
        else:
            error_msg = "Email not Registered..!"

    return render_template('login.html', error_msg=error_msg)



#-------------------------------------------------------------------------------------------

@app.route('/logout')
def logout():
	session.clear()  # remove ALL session data
	return redirect('/home')


#-------------------------------------------------------------------------------------------

@app.route('/user-verification', methods=['POST', 'GET'])
def user_verification():
	if 'temp_new_email' in session:
		error_msg = ''
		email = session['temp_new_email']
		name = session['temp_new_name']
		if request.method == 'POST':
			n1 = request.form.get('n1')
			n2 = request.form.get('n2')
			n3 = request.form.get('n3')
			n4 = request.form.get('n4')

			if not n1 or not n2 or not n3 or not n4:
				error_msg = 'Please Enter OTP'
				return render_template('email_verification.html', email=email, error_msg=error_msg)


			otp = n1+n2+n3+n4

			if str(session['verification_otp']) == str(otp):
				new_user = Userers(username=name, email=email)
				db.session.add(new_user)
				db.session.commit()

				user = Userers.query.filter_by(email=email).first()
				if user:
					session['user_id'] = user.id
					session['user_name'] = user.username
					session['user_email'] = user.email

				session.pop('temp_new_email', None)
				session.pop('temp_new_name', None)
				session.pop('verification_otp', None)
				return redirect('/home')
			else:
				error_msg = "OTP Verification failed"
	else:
		return redirect('/user-register')

	return render_template('email_verification.html', email=email, error_msg=error_msg)


#-------------------------------------------------------------------------------------------


@app.route('/user-register', methods=['POST', 'GET'])
def user_register():
	error_msg=''
	if request.method == 'POST':
		name = request.form.get('name')
		email = request.form.get('email')

		if not name or not email:
		    error_msg = "Name and Email are required"
		    return render_template('user_register.html', error_msg=error_msg)

		# checking duplications

		user = Userers.query.filter_by(email=email).first()
		if user:
			error_msg = "Email Already Registered"
			return render_template('user_register.html', error_msg=error_msg)
		else:
			session['temp_new_email'] = email
			session['temp_new_name'] = name
			send_otp(email)
			return redirect(url_for('user_verification'))

	return render_template('user_register.html')


#-------------------------------------------------------------------------------------------



@app.route('/programmes/team-register/<int:event_id>', methods=['POST', 'GET'])
def team_register(event_id):
	error_msg = ' '
	if 'user_name' not in session:
		return redirect('/login')


	reg_detail = Registration.query.filter_by(
    userid=session['user_id'],
    event_id=event_id
	).first()

	if reg_detail:
	    return redirect('/user/user-info')
	
	event_detail = Event.query.get(event_id)
	event_name = event_detail.event_name


	if request.method == 'POST':
		reg_date = datetime.utcnow().strftime("%Y-%m-%d")
		userid = session['user_id']

		team_name = request.form.get('teamName')
		email = request.form.get('email')
		eventname = request.form.get('eventname')

		member1 = request.form.get('member1')
		member1phone = request.form.get('member1phone')

		member2 = request.form.get('member2')
		member2phone = request.form.get('member2phone')

		if not team_name or not eventname or not member1 or not member1phone:
		    error_msg = "Please fill all required fields"
		    return render_template("team_register.html", error_msg=error_msg)


		#Inserting the new team
		new_team = Registration(
		    userid=userid,
		    reg_date =reg_date,
		    event_name=eventname,
		    team_name=team_name,
		    event_id=event_id,
		    email=email,
		    member1_name=member1,
		    member1_phone=member1phone,
		    member2_name=member2,
		    member2_phone=member2phone
		)
		try:
		    db.session.add(new_team)
		    db.session.commit()
		    return render_template('registered.html')
		except Exception as e:
		    db.session.rollback()
		    return render_template('registered_failed.html')



	return render_template('team_register.html', event_name=event_name)



#-------------------------------------------------------------------------------------------




# @app.route('/inserter')
# def inserter():
# 	creator_id = 2
# 	event3 = Event(
#        event_name="CYBER SECURITY 2026",
#         description="A 24-hour coding challenge to build AI solutions.",
#         event_date="2025-12-15",
#         last_date="2025-12-12",
#         event_upload_date="2025-12-01",
#         creator=creator_id,
#         prize1="₹10,000",
#         prize2="₹5,000")
# 	db.session.add(event3)
# 	db.session.commit()

# 	return redirect('/home')





@app.route('/progrmmes/team-register/email-verification')
def team_register_email_verification():
	return render_template('email_verification.html')

@app.route('/progrmmes/team-register/email-verification/success')
def team_register_email_verification_success():
	return render_template('registered.html')


@app.route('/user/user-info')
def user_details():
	if 'user_name' in session:
		userid =  session['user_id']

		users = Userers.query.get(userid)
		user_detail = [users.id, users.username, users.email]

		# events = Registration.query.all()
		# events = Registration.query.filter_by(userid=userid).all()
		events = (
		    Registration.query
		    .filter_by(userid=userid)
		    .options(joinedload(Registration.event))
		    .order_by(Registration.created_at.desc())
		    .all()
		)


		print(events)

		return render_template('user_details.html', user_detail=user_detail, events=events)
	else:
		return redirect('/home')


# -------------------------------------------------------------
# -------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------------------

@app.route('/admin-logout')
def adminlogout():
	if 'admin' in session:
		session.pop('admin', None)
		return redirect('/admin/admin-login')
	else:
		return redirect('/admin/admin-login')



@app.route('/admin/admin-login', methods=['POST', 'GET'])
def admin_login():
    error_msg = ''
    if request.method == 'POST':
        adminname = request.form.get('adminname')
        password = request.form.get('password')

        # find existing admin
        try:
        	admin = Admin.query.filter_by(name=adminname).first()
        except Exception as e:
        	error_msg = "Admin not found " + e
        	return render_template('admin/login.html', error_msg=error_msg)

        if not admin:
            error_msg = "Admin not found"
            return render_template('admin/login.html', error_msg=error_msg)

        # check password match
        if admin.password == password:
        	session['admin'] = admin.name
        	return redirect('/admin/admin-home')
        else:
            error_msg = "Incorrect password"

    return render_template('admin/login.html', error_msg=error_msg)


@app.route('/admin/register-admin', methods=['POST', 'GET'])
def register_admin():
    error_msg = ''
    if request.method == 'POST':
        adminname = request.form.get('adminname')
        password = request.form.get('password')

        # Check if admin already exists
        existing_admin = Admin.query.filter_by(name=adminname).first()
        if existing_admin:
            error_msg = 'Admin already exists'
            return render_template('admin/register.html', error_msg=error_msg)

        # Create new admin
        new_admin = Admin(name=adminname, password=password)
        db.session.add(new_admin)
        db.session.commit()
        return redirect('/admin/admin-home')  # after successful registration

    return render_template('admin/register.html', error_msg=error_msg)


@app.route('/admin/admin-home')
def admin_page():
	if 'admin' in session:
		try:
			admin = get_admins()
			return render_template('admin/admins.html', admin=admin)
		except Exception as e:
			return redirect('/admin/admin-login')
	else:
		return redirect('/admin/admin-login')


@app.route('/admin/admin-get-registrations')
def admin_get_registrations():
    if 'admin' in session:
        registrations = admin_get_registrations()
        return render_template('admin/admin_get_registrations.html', registrations=registrations)
    else:
        return redirect('/admin/admin-login')



@app.route('/admin/admin-get-users')
def admin_get_users():
    if 'admin' in session:
    	try:
    		users = get_users()
    		return render_template('admin/admin_users.html', users=users)
    	except Exception as e:
    		return redirect('/admin/admin-login')
    else:
        return redirect('/admin/admin-login')



@app.route('/admin/delete-event/<int:event_id>', methods=['POST', 'GET'])
def admin_delete_event(event_id):
    if 'admin' in session:
        error_msg = ''
        try:
            evt = db.session.get(Event, event_id)
            if not evt:
                return redirect(url_for('admin_add_event'))

            db.session.delete(evt)
            db.session.commit()
            error_msg = "Successfully Deleted..!!"

        except Exception as e:
            error_msg = "Something Wrong"


        try:
        	events = get_events()
        	events_outdated = get_events_outdated()
        except Exception as e:
        	return redirect('/admin/admin-login')
        return render_template('admin/admin.html', error_msg=error_msg, events=events, events_outdated=events_outdated)
    else:
        return redirect('/admin/admin-login')





@app.route('/admin/add-event', methods=['POST', 'GET'])
def admin_add_event():
    if 'admin' in session:
        error_msg = ''

        if request.method == 'POST':
            error_msg = ""
            creator_id = session['admin']
            eventname = request.form.get('eventname')
            eventdate = request.form.get('eventdate')
            lastdate = request.form.get('lastdate')
            description = request.form.get('description')
            prize1 = request.form.get('prize1')
            prize2 = request.form.get('prize2')
            reg_date = datetime.utcnow().strftime("%Y-%m-%d")

            try:
                event3 = Event(
                    event_name=eventname,
                    description=description,
                    event_date=eventdate,
                    last_date=lastdate,
                    event_upload_date=reg_date,
                    creator=creator_id,
                    prize1=prize1,
                    prize2=prize2
                )
                db.session.add(event3)
                db.session.commit()
                error_msg = "Successfully added..!"
            except Exception as e:
                error_msg = "Failed to add..!"

        try:
        	events = get_events()
        	events_outdated = get_events_outdated()
        except Exception as e:
        	return redirect('/admin/admin-login')

        return render_template('admin/admin.html', error_msg=error_msg, events=events, events_outdated=events_outdated)
    else:
        return redirect('/admin/admin-login')





def add_admin():
	adminname = "Ivin Jose"
	password = 12345

	new_admin = Admin(name=adminname, password=password)
	db.session.add(new_admin)
	db.session.commit()


@app.route('/admin/registrations')
def admin_registrations():
    regs = (
        Registration.query
        .options(joinedload(Registration.event))  # load Event in same query
        .order_by(Registration.created_at.desc())
        .all()
    )
    return render_template('admin/admin_registrations.html', regs=regs)


#----------------------------------------------------------------------------------------------------


import csv
from io import StringIO
from flask import Response
from sqlalchemy.orm import joinedload

@app.route("/admin/export-registrations")
def export_registrations():
    regs = (
        Registration.query
        .options(joinedload(Registration.event))
        .order_by(Registration.created_at.desc())
        .all()
    )

    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)

    # CSV Header
    writer.writerow([
        "Team Name", "Email",
        "Member1 Name", "Member1 Phone",
        "Member2 Name", "Member2 Phone", "reg_date",
        "Event Name", "Event Date", "Last Date"
    ])

    # CSV Rows
    for r in regs:
        writer.writerow([
            r.team_name,
            r.email,
            r.member1_name,
            r.member1_phone,
            r.member2_name,
            r.member2_phone,
            r.reg_date,
            r.event.event_name if r.event else "",
            r.event.event_date if r.event else "",
            r.event.last_date if r.event else ""
        ])

    # Return as downloadable CSV
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=registrations.csv"
        }
    )



@app.route("/admin/export-events")
def export_events():
    events = get_events()

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Event ID", "Event Name", "Description",
        "Event Date", "Last Date", "Uploaded On", "Creator"
    ])

    # Rows
    for e in events:
        writer.writerow([
            e.event_id,
            e.event_name,
            e.description or "",
            e.event_date,
            e.last_date,
            e.event_upload_date,
            e.creator
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=events.csv"
        }
    )



#----------------------------------------------------------------------------------------------------


@app.route('/admin/create-default')
def create_default_admin():
    # change these to what you want
    admin_name = "admin"
    admin_password = "admin123"   # plain text for demo only

    existing = Admin.query.filter_by(name=admin_name).first()
    if existing:
        return "Admin already exists."

    new_admin = Admin(name=admin_name, password=admin_password)
    db.session.add(new_admin)
    db.session.commit()
    return "Default admin created."

if __name__ == '__main__':
    app.run(ssl_context='adhoc', port=5000)