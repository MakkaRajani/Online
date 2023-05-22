from flask import Flask,request,redirect,render_template,url_for,flash,session,send_file
from flask_mysqldb import MySQL
from flask_session import Session
from otp import genotp
from cmail import sendmail
import random
from itsdangerous import  TimedJSONWebSignatureSerializer  as Serializer
from tokenreset import token
from io import BytesIO
app=Flask(_name_)
app.secret_key='something@#'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='employee'
Session(app)
mysql=MySQL(app)
@app.route('/')
def homepage():
    return render_template('home.html')
@app.route('/registration',methods=['GET','POST'])
def adminreg():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        passcode=request.form['passcode']
        cursor=mysql.connection.cursor()
        cursor.execute('insert into admin values(%s,%s,%s,%s)',(username,email,password,passcode))
        mysql.connection.commit()
        cursor.close()
       
        return 'Details registered!'
    return render_template('adminreg.html')
@app.route('/onlinereg',methods=['GET','POST'])
return render_template('adminreg.html')

def onlinereg():
    if request.method=='POST':
        rollno= request.form.get('rollno')
        password = request.form.get('password')
        gender= request.form.get('gender')
        email = request.form.get('email')
        
        
        cursor=mysql.connection.cursor()
        cursor.execute('Select rollno from student')
        data=cursor.fetchall()
        cursor.execute('SELECT email from student')
        edata=cursor.fetchall()
        if(rollno,)in data:
            flash('User already already exists')
            return render_template('onlinereg.html')
        if(email,) in edata:
            flash('Email id  already already exists')
            return render_template('onlinereg.html')
        cursor.close()
        otp=genotp()
        subject='Thanks for registering to the application'
        body='Use this otp to register:'+otp
        sendmail(email,body,subject)
        return render_template('otp.html',otp=otp,rollno=rollno,password=password,gender=gender,email=email)
    return render_template('onlinereg.html')

@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    if session.get('user'):
        return redirect(url_for('adminhomepage'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from admin where username=%s and password=%s',[username,password])
        count=cursor.fetchone()  [0]
        if count==0:
            flash('Invalid user or password')
            return render_template('adminlogin.html')
        else:
            session['user']=username
            return redirect(url_for('adminlogin'))
    return render_template('adminlogin.html')
app.route('/loginpage',methods=['GET','POST'])
def loginpage():
    if session.get('user'):
        return redirect(url_for('index'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from login where username=%s and password=%s',[aname,password])
        count=cursor.fetchone()[0]
        if count==0:
           
            flash('Invalid user name or password')
            return render_template('login.html')
        else:
            session['user']=username
            return redirect(url_for('index'))
       
    return render_template('loginpage.html')

@app.route('/forgotpassword',methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select password from student')
        data=cursor.fetchall()
        if  (password,) in data:
            cursor.execute('select email from student where password=%s',[password])
            data=cursor.fetchone() [0]
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the password using-{request.host+url_for("createpassword",token=token(rollno,240))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('loginpage'))
        else:
            return 'Invalid user id'
    return render_template('forgot.html')
@app.route('/otp/<otp>/<aname>/<email>/<password>/<passcode>',methods=['GET','POST'])
def otp(otp,username,email,password,passcode):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.connection.cursor()
            lst=[username,email,password,passcode]
            query='insert into admin values(%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
           
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,aname=aname,email=email,password=password,passcode=passcode)
@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        username=s.loads(token)['user']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mysql.connection.cursor()
                cursor.execute('update admin set password=%s where aname=%s',[npass,aname])
                mysql.connection.commit()
                return 'Password reset Successfull'
            else:
                return 'Password mismatch'
        return render_template('newpassword.html')
    except:
        return 'Link expired try again'
app.run(debug=True,use_reloader=True)
