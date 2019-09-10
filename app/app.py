from flask import Flask,render_template,request,flash,redirect,url_for,session,logging,Response
from flask_mysqldb import MySQL
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from wtforms import Form,fields, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from werkzeug.utils import secure_filename
from flask import jsonify,json
from array import *
from flask_mail import Mail, Message
from flask.debughelpers import DebugFilesKeyError
from flask.ext.bcrypt import Bcrypt
from flask.ext.hashing import Hashing
import hashlib


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hack'
app.config['MYSQL_CURSORCLASS']= 'DictCursor'

mysql = MySQL(app)
bcrypt = Bcrypt(app)
s = URLSafeTimedSerializer('secret123')
hashing = Hashing(app)

class DataForm(Form):
	model = StringField('model' , [validators.length(min=1,max=20)])
	name = StringField('name',[validators.length(min=5,max=30),validators.Required()])
	cal = StringField('cal',[validators.length(min=6,max=15)])
#	card = StringField('card',[validators.length(min=1,max=15)])
	number = StringField('number', [validators.length(min=10,max=15)])

@app.route('/',methods=['GET','POST'])
def generate():
	form = DataForm(request.form)
	if request.method == 'POST' and form.validate():
		model = form.model.data
		name = form.name.data
		cal = form.cal.data
		#card = form.card.data
		number = form.number.data
		m = hashing.hash_value(model,salt='model123')
		n = hashing.hash_value(name,salt='name234')
		d = hashing.hash_value(cal,salt='date345')
		identity = hashing.hash_value(m+n+d,salt='combine')
		token = s.dumps(m+n+d,salt='comb')
		link = url_for('fetch',token=token,_external=True)
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO tabel(model,name,cal,number,identity) VALUES(%s,%s,%s,%s,%s)",(model,name,cal,number,identity))
		mysql.connection.commit()
		cur.close()
		return render_template('generate.html',identity=identity)
	return render_template('first.html')

@app.route('/fetch/<token>')
def fetch_link(token):
	try:
		token1 = s.loads(token,salt='acd',max_age=2000)
	except SignatureExpired:
		return 'fail'
	return 'success'	

class FetchData(Form):
	identity = StringField('identity',[validators.length(min=64,max=120)])


@app.route('/fetched',methods=['GET','POST'])
def fetch():
	form = FetchData(request.form)
	if request.method == 'POST' and form.validate():
		identity = form.identity.data
		useless = str(identity)
		cur = mysql.connection.cursor()
		result=cur.execute("SELECT * FROM tabel WHERE identity=%s",[useless])
		fetched=cur.fetchall()
		if result>0:
			return render_template('retrieved.html',fetched=fetched)
		else:
			flash('Data is not found or check manually key is coorect are worng','danger')
			return render_template('retrieved.html',msg=msg)
		cur.close()
		flash('somthing is wrong','danger')
		return render_template('retrieved.html',error=error)
	return render_template('retrieve.html')

if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)