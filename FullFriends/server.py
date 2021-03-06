from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
app = Flask (__name__)
mysql = MySQLConnector(app,'friendsdb')
app.secret_key = "SoSoSecret"
@app.route('/')
def index():
	query = "SELECT * FROM friends"                           # define your query
	friends = mysql.query_db(query)                           # run query with query_db()
	return render_template('index.html', all_friends=friends) # pass data to our template

@app.route('/friends/create', methods=["POST"])
def create():
	# add a friend to the database 
	query =" INSERT INTO friends  (first_name,last_name,occupation,created_at,updated_at) VALUES (:first_name, :last_name, :occupation, NOW(), NOW())"

	data = {
		'first_name': request.form['first_name'],
		'last_name': request.form['last_name'],
		'occupation': request.form['occupation'],
	}

	mysql.query_db(query,data)

	return redirect('/')

@app.route('/friends/profile/<friend_id>')
def read(friend_id):
	query = "SELECT * FROM friends WHERE id =?"

	data = {'?': friend_id}

	friends = mysql.query_db(query,data)
	return render_template('/profile.html',one_friend=friends[0])


@app.route('/friends/<friend_id>/edit')
def updatePage(friend_id):

	query = "SELECT * FROM friends WHERE id = :user"
	data = {'user': friend_id}
	results = mysql.query_db(query,data)
	session['edit'] ='true'
	return render_template('profile.html',data={'one_friend':results})

@app.route('/friends/<friendId>',methods=["POST"])
def update(friendId):
	for value in request.form:
		if len(request.form[value])>1:
			data = {
				'dataVal':request.form[value],
				'userVal': friendId
			}
			query = "UPDATE friends SET "+value+"= :dataVal, updated_at = NOW() WHERE id = :userVal"
			mysql.query_db(query,data)

	return redirect('/')
@app.route('/friends/<friendId>/delete')
def destroy(friendId):
	query = "DELETE FROM friends WHERE id = :friendId"
	data = {
	"friendId":friendId
	} 
	mysql.query_db(query,data)
	return redirect('/')





app.run(debug=True)