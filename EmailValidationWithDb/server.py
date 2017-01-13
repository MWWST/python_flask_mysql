from flask import Flask, request, redirect, render_template, session, flash
import re
from mysqlconnection import MySQLConnector

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask (__name__)
app.secret_key = "SoSoSecret"
mysql = MySQLConnector(app,'emailTracker')



@app.route('/')
def index():
	return render_template('index.html')

@app.route('/email/create',methods=["POST"])
def createEmail():
	if len(request.form['email'])<1:
		flash("Email cannot be blank!",'error')
	elif not EMAIL_REGEX.match(request.form['email']):
		flash("Invalid Email Address","error")
	else:
		query = "INSERT INTO emails(email_address,created_at,updated_at) VALUES (:email,NOW(),NOW())"

		data = { 'email': request.form['email']
		}

		if mysql.query_db(query,data):
			flash("Successfully added"+request.form['email'],"success")
			return redirect('/success')
		else:
			flash("Error adding to database","error")
			return redirect('/')
	return redirect('/')
@app.route('/success')

def success():
	query = "SELECT email_address, DATE_FORMAT(created_at , '%m/%d/%Y') as created_at FROM emails"
	
	results = mysql.query_db(query)
	print results
	if results:
		return render_template('success.html',emails=results)
	else:
		return render_template('success.html')  

@app.route('/remove/<emailid>')    
def destroy(emailid):
	query ="DELETE FROM emails WHERE id = :specific_id"

	data = { 'specific_id': emailid
	}

	mysql.query_db(query,data)
	return redirect('/success')

app.run(debug=True)