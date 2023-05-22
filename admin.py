from flask import Flask,request,redirect,render_template,url_for,flash,session,send_file
from flask_mysqldb import MySQL
from flask_session import Session
from otp import genotp
from cmail import sendmail
import random
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
#from io import BytesIO                      
app=Flask(__name__)
app.secret_key='#nhy@uh7'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='online'
Session(app)
mysql=MySQL(app)
 app.run(use_reloader=True,debug=True)
