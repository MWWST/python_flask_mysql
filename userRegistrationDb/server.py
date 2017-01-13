from flask import Flask, request, render_template, flash, session, redirect
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import re
app= Flask(__name__)
app.secret_key = "SoSoSecret"
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app, 'loginreg')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/',methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/create_user',methods=["POST"])
def createUser():

	if len(request.form['email'])<1:
		flash("Email cannot be blank!",'warning')
	elif not EMAIL_REGEX.match(request.form['email']):
		flash("Invalid Email Address","warning")
	elif len(request.form['first_name'])<1 or len(request.form['last_name'])<1:
		flash("First and Last Name Required")
	else:
		first_name = request.form['first_name']
		last_name = request.form['last_name']
		email = request.form['email']
		password = request.form['password']

		pw_hash = bcrypt.generate_password_hash(password)

		insert_query = "INSERT INTO users (first_name,last_name,email, password, created_at) VALUES (:first_name,:last_name,:email,:password,NOW())"
		query_data = { 'first_name':first_name,'last_name':last_name,'email':email,'password':pw_hash}

		registered = mysql.query_db(insert_query,query_data)
		if registered:
			flash("Registration Successful, You may now login",'success')
			return redirect('/')
		else:
			flash("Problem with registration, try again",'warning')
			return redirect('/')

@app.route('/login',methods=['POST'])
def login():
	email = request.form['email']
	password = request.form['password']

	user_query = "SELECT * FROM USERS WHERE EMAIL = :email LIMIT 1"
	query_data = {'email':email}

	user = mysql.query_db(user_query,query_data)

	if bcrypt.check_password_hash(user[0]['password'],password):
		#login user
		session['loggedIn'] = True
		session['userId'] = user[0]['id']
		session['first_name'] = user[0]['first_name']
		flash("welcome","success")
		return redirect('/dashboard')
	else:
		flash("invalid login credentials","warning")
		return redirect('/')

@app.route('/dashboard')
def dashboard():
	if 'loggedIn' not in session:
		flash("Not Authorized","warning")
		return redirect('/')
	else:
		return render_template('dashboard.html')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')

app.run(debug=True)

