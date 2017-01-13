from flask import Flask, request, render_template, flash, session, redirect
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import re
app= Flask(__name__)
app.secret_key = "SoSoSecret"
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app, 'thewall')

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
		return redirect('/wall')
	else:
		flash("invalid login credentials","warning")
		return redirect('/')

@app.route('/wall')
def wall():
	if 'loggedIn' not in session:
		flash("Not Authorized","warning")
		return redirect('/')
	else:
		queryMessages ="SELECT messages.id as messageId, messages.message as message, DATE_FORMAT(messages.created_at, '%M %d, %Y') as messages_created, users.first_name,users.last_name, users.id FROM messages LEFT JOIN users on users.id = messages.user_id"

		queryComments ="SELECT comments.id as commentId, comments.comment as comment, comments.message_id, DATE_FORMAT(comments.created_at, '%M %d, %Y') as comments_created,users.first_name,users.last_name, users.id FROM comments LEFT JOIN users on users.id = comments.user_id"
		
		messages = mysql.query_db(queryMessages)
		comments = mysql.query_db(queryComments)
		return render_template('wall.html',messages=messages,comments=comments)

@app.route('/message/create',methods=["POST"])
def createMessage():
	message = request.form['message']

	if len(message)>10:
		query = "INSERT INTO messages (message,user_id,created_at) VALUES (:message,:user,NOW())"
		query_data = {'message':message,'user':session['userId']}
		results = mysql.query_db(query,query_data)
		return redirect('/wall')

@app.route('/comment/create',methods=["POST"])
def createComment():
	comment = request.form['comment']
	messageId = request.form['message_id']
	if len(comment)>10:
		query = "INSERT INTO comments (comment,user_id,message_id,created_at) VALUES (:comment,:user,:messageid,NOW())"
		query_data = {'comment':comment,'user':session['userId'],'messageid':messageId}
		results = mysql.query_db(query,query_data)
		return redirect('/wall')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')

app.run(debug=True)

