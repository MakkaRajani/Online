from flask import Flask,request,redirect,render_template,url_for,flash,session,send_file
from flask_mysqldb import MySQL
from flask_session import Session
from otp import genotp
from cmail import sendmail
import random
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
from io import BytesIO                      # files input &output package
app=Flask(__name__)
app.secret_key='*grsig@khgy'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='user'
Session(app)
mysql=MySQL(app)
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/userreg',methods=['GET','POST'])
def userreg():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']
        mobile=request.form['mobile']
        gender=request.form['gender']
        
        
        cursor=mysql.connection.cursor()
        cursor.execute('Select username from userinfo')
        data=cursor.fetchall()
        cursor.execute('SELECT email from userinfo')
        edata=cursor.fetchall()
        if(username,)in data:
            flash('User already already exists')
            return render_template('userreg.html')
        if(email,) in edata:
            flash('Email id  already already exists')
            return render_template('userreg.html')
        cursor.close()
        otp=genotp()
        subject='Thanks for registering to the application'
        body=f'Use this otp to register {otp}'
        sendmail(email,body,subject)
        return render_template('otp.html',otp=otp,username=username,password=password,email=email,mobile=mobile,gender=gender)
    return render_template('userreg.html')
@app.route('/userlogin',methods=['GET','POST'])
def userlogin():
    
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from userinfo where username=%s and password=%s',[username,password])
        count=cursor.fetchone()  [0]
        if count==0:
            flash('Invalid username or password')
            return render_template('userlogin.html')
        else:
            session['user']=username
            return redirect(url_for('home9'))
    return render_template('userlogin.html')
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('home'))
    else:
        flash('already logged out!')
        return redirect(url_for('login'))
@app.route('/otp/<otp>/<username>/<password>/<email>/<mobile>/<gender>',methods=['GET','POST'])
def otp(otp,username,password,email,mobile,gender):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            lst=[username,password,email,mobile,gender]
            query='insert into userinfo values(%s,%s,%s,%s,%s)'
            cursor=mysql.connection.cursor()
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('userlogin'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,username=username,password=password,email=email,mobile=mobile,gender=gender)
@app.route('/forgetpassword',methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        username=request.form['username']
        cursor=mysql.connection.cursor()
        cursor.execute('select username from userinfo')
        data=cursor.fetchall()
        if  (username,) in data:
            cursor.execute('select email from userinfo where username=%s',[username])
            data=cursor.fetchone() [0]
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the password using-{request.host+url_for("createpassword",token=token(username,240))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('userlogin'))
        else:
            return 'Invalid user id'
    return render_template('forgot.html')

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
                cursor.execute('update userinfo set password=%s where username=%s',[npass,username])
                mysql.connection.commit()
                return 'Password reset Successfull'
            else:
                return 'Password mismatch'
        return render_template('newpassword.html')
    except Exception as e:
        print(e)
        return 'Link expired try again'
 
@app.route('/aindex')
def aindex():
    return render_template('aindex.html')

@app.route('/adminreg',methods=['GET','POST'])
def adminreg():
    if request.method=='POST':
        name=request.form['username']
        email=request.form['email']
        password=request.form['password']
        passcode=request.form['passcode']
        upasscode='4567'
        cursor=mysql.connection.cursor()
        # check if the email already exists
        cursor.execute('SELECT COUNT(*) FROM admin WHERE email = %s', [email])
        count = cursor.fetchone()[0]
        if count > 0:
            flash('Email id already exists')
            return render_template('admincourse.html')
        # check if the passcode matches
        elif upasscode != passcode:
            flash('Invalid passcode')
            return render_template('admincourse.html')
        # insert the admin details
        else:
            cursor.execute('INSERT INTO admin VALUES (%s,%s,%s,%s)',[name,email,password,passcode])
            mysql.connection.commit()
            cursor.close()
            flash("Admin account created successfully")
            return render_template('adminlogin.html')
    return render_template('adminreg.html')
    
@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    if request.method=='POST':
        print(request.form)
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from userinfo where username=%s and password=%s',[username,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid username or password')
            return render_template('adminlogin.html')
        else:
            session['user']=username
            return redirect(url_for('admin'))
    return render_template('adminlogin.html')

@app.route('/adminforgotpassword',methods=['GET','POST'])
def adminforgot():
    if request.method=='POST':
        username=request.form['username']
        cursor=mysql.connection.cursor()
        cursor.execute('select username from admin')
        data=cursor.fetchall()
        if  (username,) in data:
            cursor.execute('select email from admin where username=%s',[username])
            data=cursor.fetchone() [0]
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the password using-{request.host+url_for("createpassword",token=token(username,240))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('adminlogin'))
        else:
            return 'Invalid user id'
    return render_template('adminforgot.html')

@app.route('/adminpassword/<token>',methods=['GET','POST'])
def adminpassword(token):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        username=s.loads(token)['user']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mysql.connection.cursor()
                cursor.execute('update userinfo set password=%s where username=%s',[npass,username])
                mysql.connection.commit()
                return 'Password reset Successfull'
            else:
                return 'Password mismatch'
        return render_template('adminnewpassword.html')
    except: 
        return 'Link expired try again'

@app.route('/admin')
def admin():
    return render_template('admin.html')
    
@app.route('/admincourse')
def admincourse():
    return render_template('admincourse.html')
@app.route('/adminques')
def adminques():
    return render_template('adminques.html')


@app.route('/addcourse',methods=['GET','POST'])
def addcourse():
    if session.get('user'):
        if request.method=='POST':
           courseid=request.form['id']
           coursename=request.form['cname']
           duration=request.form['duration']
          
           cursor=mysql.connection.cursor()
           cursor.execute('insert into course(course_id,course_name,duration)values(%s,%s,%s)',[courseid,coursename,duration])
           mysql.connection.commit()
           cursor.close()
           flash('Details Registered')
           return redirect(url_for('admincourse'))
        return render_template('addcourse.html')
    else:
       
        return redirect(url_for('addcourse'))
@app.route('/viewcourse')
def viewcourse():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from course')
        course_data=cursor.fetchall()
        print(course_data)
        cursor.close()
        return render_template('viewcourse.html',data=course_data)     
    else:
        return redirect(url_for('login'))
@app.route('/delete/<course_id>')
def delete(course_id):
    cursor=mysql.connection.cursor()
    cursor.execute('delete from course where course_id=%s',[course_id])
    mysql.connection.commit()
    cursor.close()
    flash('Course deleted successfully')
    return redirect(url_for('viewcourse'))




app.run(use_reloader=True,debug=True)
