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
app.secret_key='*67@hjyjhk'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='online'
Session(app)
mysql=MySQL(app)
@app.route('/')
def homepage():
    return render_template('homepage.html')
@app.route('/onlinereg',methods=['GET','POST'])
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
@app.route('/loginpage',methods=['GET','POST'])
def loginpage():
    
    if request.method=='POST':
        rollno=request.form['rollno']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from student where rollno=%s and password=%s',[rollno,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid rollno or password')
            return render_template('loginpage.html')
        else:
            session['studentid']=rollno
            return redirect(url_for('studentbase'))
    return render_template('loginpage.html')
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('homepage'))
    else:
        flash('already logged out!')
        return redirect(url_for('loginpage'))
@app.route('/otp/<otp>/<rollno>/<password>/<gender>/<email>/',methods=['GET','POST'])
def otp(otp,rollno,password,gender,email):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            lst=[rollno,password,gender,email]
            query='insert into student values(%s,%s,%s,%s)'
            cursor=mysql.connection.cursor()
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('loginpage'))
        else:
            flash('Wrong otp')
    return render_template('otp.html',otp=otp,rollno=rollno,password=password,gender=gender,email=email)
@app.route('/forget',methods=['GET','POST'])
def forget():
    if request.method=='POST':
        email=request.form['email']
        cursor=mysql.connection.cursor()
        cursor.execute('select email from admin')
        data=cursor.fetchall()  
        if (email,) in data:
            cursor.execute('select email from admin where email=%s',[email])
            data=cursor.fetchone()[0]
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the passwword using- {request.host+url_for("createpassword",token=token(email,120))}'
            sendmail(email,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('loginpage'))
        else:
            return 'Invalid user id'
    return render_template('forget.html')

@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        rollno=s.loads(token)['user']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mysql.connection.cursor()
                cursor.execute('update student set password=%s where rollno=%s',[npass,rollno])
                mysql.connection.commit()
                return 'Password reset Successfull'
            else:
                return 'Password mismatch'
        return render_template('createpassword.html')
    except Exception as e:
        print(e)
        return 'Link expired try again'
@app.route('/adminhomepage')
def adminpage():
    return render_template('adminhomepage.html')


@app.route('/adminreg',methods=['GET','POST'])
def adminreg():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']
        cursor=mysql.connection.cursor()
        cursor.execute('insert into admin(username,password,email) values(%s,%s,%s)',[username,password,email])
        mysql.connection.commit()
        data=cursor.fetchall()
            #print(data)
        if (username,) in data:
            flash('User already exists')
            return render_template('adminlogin.html')
            cursor.close()
        else:
            flash('Successfully registered')
            return render_template('adminreg.html')
    return render_template('adminreg.html')
@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    
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
            return redirect(url_for('dashboard'))
    return render_template('adminlogin.html')
@app.route('/alogout')
def alogout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('adminhomepage'))
    else:
        flash('already logged out!')
        return redirect(url_for('login'))

    
@app.route('/forgetpassword',methods=['GET','POST'])
def adminforgot():
    if request.method=='POST':
        email=request.form['email']
        cursor=mysql.connection.cursor()
        cursor.execute('select email from admin')
        data=cursor.fetchall()  
        if (email,) in data:
            cursor.execute('select email from admin where email=%s',[email])
            data=cursor.fetchone()[0]
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the passwword using- {request.host+url_for("createpassword",token=token(email,120))}'
            sendmail(email,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('adminlogin'))
        else:
            return 'Invalid user id'
    return render_template('adminforgot.html')

@app.route('/newpassword/<token>',methods=['GET','POST'])
def newpassword(token):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        username=s.loads(token)['user']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mysql.connection.cursor()
                cursor.execute('update admin set password=%s where username=%s',[npass,username])
                mysql.connection.commit()
                return 'Password reset Successfull'
            else:
                return 'Password mismatch'
        return render_template('newpassword.html')
    except Exception as e:
        print(e)
        return 'Link expired try again'
@app.route('/dashboard')
def dashboard():
    
    return render_template('dashboard.html')
@app.route('/stuhome')
def stuhome():
    return render_template('stuhome.html')

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
           courseid=request.form['courseid']
           coursename=request.form['coursename']
           duration=request.form['duration']
          
           cursor=mysql.connection.cursor()
           cursor.execute('insert into courses(courseid,coursename,duration)values(%s,%s,%s)',[courseid,coursename,duration])
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
        cursor.execute('select * from courses')
        course_data=cursor.fetchall()
        print(course_data)
        cursor.close()
        return render_template('viewcourse.html',data=course_data)     
    else:
        return redirect(url_for('viewcourse'))
@app.route('/delete/<courseid>')
def delete(courseid):
    cursor=mysql.connection.cursor()
    cursor.execute('delete from courses where courseid=%s',[courseid])
    mysql.connection.commit()
    cursor.close()
    flash('Course deleted successfully')
    return redirect(url_for('viewcourse'))
@app.route('/addquestion',methods=['GET','POST'])
def addquestion():
    if session.get('user'):
        if request.method=='POST':
           questionid=request.form['questionid']
           questionname=request.form['questionname']
           courseid=request.form['courseid']
           option1=request.form['option1']
           option2=request.form['option2']
           option3=request.form['option3']
           option4=request.form['option4']
           correctoption=request.form['correctoption']
           marks=request.form['marks']
           cursor=mysql.connection.cursor()
           
           cursor.execute('insert into questions(questionid,questionname,courseid,option1,option2,option3,option4,correctoption,marks)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',[questionid,questionname,courseid,option1,option2,option3,option4,correctoption,marks])
           mysql.connection.commit()
           cursor.close()
           flash('Details Registered')
           return redirect(url_for('adminques'))
        return render_template('addquestion.html')
    else:
       
        return redirect(url_for('addquestion'))
@app.route('/allquestions')
def allquestions():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from questions')
        course_data=cursor.fetchall()
        print(course_data)
        cursor.close()
        return render_template('allquestions.html',data=course_data)     
    else:
        return redirect(url_for('allquestions'))
@app.route('/update/<qid>',methods=['GET','POST'])
def update(qid):
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select questionid,questionname,courseid,option1,option2,option3,option4,correctoption,marks from questions where questionid=%s',[qid])
        data=cursor.fetchone()
        cursor.close()
        if request.method=='POST':
            questionid=request.form['questionid']
            questionname=request.form['questionname']
            courseid=request.form['courseid']
            option1=request.form['option1']
            option2=request.form['option2']
            option3=request.form['option3']
            option4=request.form['option4']
            correctoption=request.form['correctoption']
            marks=request.form['marks']
            cursor=mysql.connection.cursor()
            cursor.execute('update questions set questionid=%s,questionname=%s,courseid=%s,option1=%s,option2=%s,option3=%s,option4=%s,correctoption=%s,marks=%s where questionid=%s',[qid,questionname,courseid,option1,option2,option3,option4,correctoption,marks,qid])
            mysql.connection.commit()
            cursor.close()
            flash('questionss updated successfully')
            return redirect(url_for('allquestions'))
        return render_template('update.html',data=data)
    else:
        return redirect(url_for('dashboard'))
 


@app.route('/studentbase')
def studentbase():
    return render_template('studentbase.html')
@app.route('/studentdashboard')
def studentdashboard():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT count(*) from courses')
    data=cursor.fetchone()[0]
    #total_courses=a[0]
    cursor.close()
    return render_template('studentdashboard.html',data=data)
@app.route('/coursedetails')
def studentcoursedetails():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * from courses')
    courselist=cursor.fetchall()    
    cursor.close()
    return render_template('studentcoursedetails.html',courselist=courselist)
@app.route('/studentexam')
def studentexam():
    cursor=mysql.connection.cursor()   
    cursor.execute('SELECT coursename from courses')
    data=cursor.fetchall()
    #data1=data[0]
    #print(data)
    #print(a)
    cursor.close()
    return render_template('studentexam.html',coursename=data)
@app.route('/examinstructions/<coursename>')
def takeexam(coursename):
    return render_template('takeexam.html',coursename=coursename)
@app.route('/attempts/<coursename>')
def attempt(coursename):
    students=session['studentid']
    cursor=mysql.connection.cursor()
    cursor.execute('select courseid from courses where coursename=%s',[coursename]);
    course_id=cursor.fetchone()[0]
    cursor.execute('select count(*) from submit where rollno=%s and courseid=%s',[students,course_id])
    result=int(cursor.fetchone()[0])
    if result>0:
        return render_template('noattempt.html')
    else:
        return redirect(url_for('takeexam',coursename=coursename))
@app.route('/submission')
def submit():
    return render_template('examsubmit.html')
@app.route('/startexam/<coursename>',methods=['GET','POST'])
def startexam(coursename):
    cursor=mysql.connection.cursor()
    cursor.execute('select courseid from courses where coursename=%s',[coursename])
    course_id=cursor.fetchone()[0]
    cursor.execute('SELECT questionid,questionname,courseid,option1,option2,option3,option4,marks from questions where courseid=%s',[course_id])
    data=list(cursor.fetchall())
    random.shuffle(data)
    cursor.close()
    if request.method=='POST':
        selectedoption=request.form.getlist('options')
        print(selectedoption)
        students=session['studentid']
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT questionid from questions where courseid=%s',[course_id])
        question_id=cursor.fetchall()
        #print(courseid)
        #print( questionid)
        for i,j in zip(selectedoption,question_id):
                cursor=mysql.connection.cursor()
                cursor.execute('insert into submit (optionselected,rollno,courseid,questionid) values(%s,%s,%s,%s)',[i,students,course_id,j])
                mysql.connection.commit()
                cursor.close()
        return redirect(url_for('submit'))
    
    #print(a)
    #print(data)                        
    return render_template('startexam.html',data=data,courseid=course_id)
@app.route('/studentmarks')
def studentmarks():
    students=session['studentid']
    #print(students)
    cursor=mysql.connection.cursor()
    cursor.execute('select distinct(courseid) from submit where rollno=%s',[students]);
    courseid=cursor.fetchall()
    #print(courseid)
    cursor.close()
    return render_template('studentmarks.html',courseid=courseid)    
@app.route('/checkmarks/<courseid>',methods=['GET'])
def checkmarks(courseid):
    students=session['studentid']
    #print(students)
    cursor=mysql.connection.cursor()
    cursor.execute('select distinct(questionid) from submit where courseid=%s',[courseid])
    question_id=cursor.fetchall()
    cursor.execute('select count(questionid) from questions where courseid=%s',[courseid])
    data=cursor.fetchone()[0]
    cursor.execute('select sum(marks) from questions where courseid=%s',[courseid])
    data1=cursor.fetchone()[0]
    #print(question_id)
    cursor.execute('select optionselected from submit where rollno=%s and courseid=%s',[students,courseid])
    selectedoption=cursor.fetchall()
    #print(selectedoption)
    cursor.execute('select correctoption  from questions where courseid=%s',[courseid])
    correctoption=cursor.fetchall()
    print(correctoption)
    cursor.execute('select marks from questions where courseid=%s',[courseid])
    marks=cursor.fetchall()
    #print(correctoption)    
    for i in question_id:        
        count=0
        for l,m,n in zip(correctoption,selectedoption,marks):
            if l==m:
                count+=int(n[0])
            else:
                count+=0            
    cursor.close()
    return render_template('checkmarks.html',count=count,courseid=courseid,data=data,data1=data1)
app.run(use_reloader=True,debug=True)
