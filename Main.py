from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
import pymysql

app = Flask(__name__)

app.secret_key = 'welcome'
global user, examname, hall, examtime, date

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'headmrce@gmail.com'  # Admin email
app.config['MAIL_PASSWORD'] = 'ogjm qwlf kgvy nnjf'  # Admin email password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



@app.route('/ViewAllotedSchedule', methods=['GET', 'POST'])
def ViewAllotedSchedule():
    global user
    command='<table border=1 align=center>'
    command+='<tr><th>Exam Name</th><th>Faculty Name</th><th>Hall No</th><th>Exam Time</th><th>Exam Date</th></tr>'
    color = '<font size="" color="black">'
    db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'duty',charset='utf8')
    with db_connect:
        cursor = db_connect.cursor()
        cursor.execute("select * from exam")
        rows = cursor.fetchall()
        for row in rows:
            if row[1] == user:
                command+='<tr><td>'+color+row[0]+'</td><td>'+color+row[1]+'</td><td>'+color+row[2]+'</td><td>'+color+row[3]+'</td><td>'+color+row[4]+'</td></tr>'            
    command += "</table><br/><br/><br/>"
    return render_template('InvigilatorScreen.html', msg=command)

@app.route('/ViewSchedule', methods=['GET', 'POST'])
def ViewSchedule():
    command='<table border=1 align=center>'
    command+='<tr><th>Exam Name</th><th>Faculty Name</th><th>Hall No</th><th>Exam Time</th><th>Exam Date</th></tr>'
    color = '<font size="" color="black">'
    db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'duty',charset='utf8')
    with db_connect:
        cursor = db_connect.cursor()
        cursor.execute("select * from exam")
        rows = cursor.fetchall()
        for row in rows:
            command+='<tr><td>'+color+row[0]+'</td><td>'+color+row[1]+'</td><td>'+color+row[2]+'</td><td>'+color+row[3]+'</td><td>'+color+row[4]+'</td></tr>'            
    command += "</table><br/><br/><br/>"
    return render_template('AdminScreen.html', msg=command)

@app.route('/AllotFaculty', methods=['GET', 'POST'])
def AllotFaculty():
    if request.method == 'GET':
        global examname, hall, examtime, date
        name = request.args.get('name')
        
        try:
            db_connect = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='duty', charset='utf8')
            cursor = db_connect.cursor()
            query = "INSERT INTO exam(exam_name, faculty_name, hall_number, exam_time, exam_date) VALUES(%s, %s, %s, %s, %s)"
            cursor.execute(query, (examname, name, hall, examtime, date))
            db_connect.commit()

            query = "UPDATE leisuretime SET status='Alloted to hall "+hall+"', allotted_date=%s WHERE faculty_name=%s"
            cursor.execute(query, (date, name))
            db_connect.commit()

            # Send email notification
            msg = Message("Exam Schedule Allocated",
                          sender="headmrce@gmail.com",
                          recipients=["invigilatormrce@gmail.com"])  # Faculty email
            msg.body = f"Hello {name},\n\nYou have been allocated the following exam schedule:\n\n" \
                        f"Exam Name: {examname}\nHall No: {hall}\nExam Date: {date}\nExam Time: {examtime}\n\n" \
                        "Best regards,\nExam Scheduling Team"
            mail.send(msg)

            return render_template('AdminScreen.html', msg=examname+" Invigilator choosen as "+name+"<br/> Hall No : "+hall+"<br/>Exam Date : "+date+"<br/>Exam Time : "+examtime)
        
        except Exception as e:
            # Log the error
            app.logger.error(f"Error occurred: {e}")
            return render_template('AdminScreen.html', msg="An error occurred: " + str(e))
        
        finally:
            cursor.close()
            db_connect.close()

@app.route('/ScheduleExamAction', methods=['GET', 'POST'])
def ScheduleExamAction():
    if request.method == 'POST':
        global examname, hall, examtime, date
        examname = request.form['t1']
        hall = request.form['t2']
        examtime = request.form['t3']
        et = examtime.split("-")
        et = et[0].strip()
        dd = request.form['t4']
        mm = request.form['t5']
        yy = request.form['t6']
        date = dd+"-"+mm+"-"+yy
        command='<table border=1 align=center>'
        command+='<tr><th>Faculty Name</th><th>Leisure Time</th><th>Choose Faculty</th></tr>'
        color = '<font size="" color="black">'
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'duty',charset='utf8')
        with db_connect:
            cursor = db_connect.cursor()
            cursor.execute("select faculty_name, leisure_time from leisuretime where allotted_date != %s", (date,))
            rows = cursor.fetchall()
            for row in rows:
                fname = row[0]
                ltime = row[1]
                ltime = ltime.split("-")
                ltime = ltime[0].strip()
                print(ltime+"==="+et)
                if ltime == et:
                    command+='<tr><td>'+color+row[0]+'</td><td>'+color+row[1]+'</td>'
                    command+='<td><a href=\'AllotFaculty?name='+str(fname)+'\'><font size=3 color=black>Click Here</font></a></td></tr>'
        return render_template('AdminScreen.html', msg=command)        

@app.route('/ScheduleExam', methods=['GET', 'POST'])
def ScheduleExam():
    output = '<TD><select name="t4">'
    for i in range(1,31):
        output += '<option value="'+str(i)+'">'+str(i)+'</option>'  
    output += "</select>&nbsp;"
    output += '<select name="t5">'
    for i in range(1,12):
        output += '<option value="'+str(i)+'">'+str(i)+'</option>'  
    output += "</select>&nbsp;"
    output += '<select name="t6">'
    for i in range(2023, 2030):
        output += '<option value="'+str(i)+'">'+str(i)+'</option>'  
    output += "</select></TD>"
    return render_template('ScheduleExam.html', data=output)

@app.route('/AddLeisureAction', methods=['POST'])
def AddLeisureAction():
    if request.method == 'POST':
        faculty_name = request.form.get('faculty_name')
        leisure_time = request.form.get('leisure_time')
        
        # Log the incoming form data
        print(f"Received data - faculty_name: {faculty_name}, leisure_time: {leisure_time}")
        
        if not faculty_name or not leisure_time:
            return render_template('AdminScreen.html', msg="Faculty name and leisure time are required")
        
        try:
            # Connect to the database
            db_connect = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='duty', charset='utf8')
            cursor = db_connect.cursor()
            
            # Check if faculty exists
            cursor.execute("SELECT username FROM faculty WHERE username = %s", (faculty_name,))
            row = cursor.fetchone()
            
            if row:
                cursor.execute("INSERT INTO leisuretime (faculty_name, leisure_time) VALUES (%s, %s)", (faculty_name, leisure_time))
                db_connect.commit()
                return render_template('AdminScreen.html', msg="Leisure time added successfully")
            else:
                return render_template('AdminScreen.html', msg="Faculty name not found")
        
        except Exception as e:
            return render_template('AdminScreen.html', msg=f"An error occurred: {e}")
        
        finally:
            cursor.close()
            db_connect.close()
   
@app.route('/AddLeisure', methods=['GET', 'POST'])
def AddLeisure():
    output = '<TD>&nbsp;<select name="t1">'
    db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'duty',charset='utf8')
    with db_connect:
        cursor = db_connect.cursor()
        cursor.execute("select username from faculty")
        rows = cursor.fetchall()
        for row in rows:
            output += '<option value="'+row[0]+'">'+row[0]+'</option>'  
    output += "</select>"    
    return render_template('AddLeisure.html', data=output)

@app.route('/AddFaculty', methods=['GET', 'POST'])
def AddFaculty():
    return render_template('AddFaculty.html', msg='')

@app.route('/AddFacultyAction', methods=['GET', 'POST'])
def AddFacultyAction():
    if request.method == 'POST':
        name = request.form['t1']
        gender = request.form['t2']
        contact = request.form['t3']
        qualification = request.form['t4']
        username = request.form['t5']
        password = request.form['t6']
        command = 'not_found'
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'duty',charset='utf8')
        with db_connect:
            cursor = db_connect.cursor()
            cursor.execute("select username from faculty where username = %s", (username,))
            rows = cursor.fetchall()
            for row in rows:
                if row[0] == username:
                    command = username+' Given Username already exists'
                    break
        if command == 'not_found':
            db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'duty',charset='utf8')
            cursor = db_connect.cursor()
            query = "INSERT INTO faculty(faculty_name, gender, contact_no, qualification, username, password) VALUES(%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (name, gender, contact, qualification, username, password))
            db_connect.commit()
            if cursor.rowcount == 1:
                command = 'Faculty details added successfully'
        return render_template('AdminScreen.html', msg=command)        

@app.route('/InvigilatorLoginAction', methods=['GET', 'POST'])
def InvigilatorLoginAction():
    if request.method == 'POST' and 't1' in request.form and 't2' in request.form:
        global user
        user = request.form['t1']
        password = request.form['t2']
        command = 'none'
        db_connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'duty',charset='utf8')
        with db_connect:
            cursor = db_connect.cursor()
            cursor.execute("select username, password from faculty")
            rows = cursor.fetchall()
            for row in rows:
                if row[0] == user and row[1] == password:
                    command = 'success'
                    break
        if command == "success":
            return render_template('InvigilatorScreen.html', msg="Welcome "+user)
        else:
            return render_template('InvigilatorLogin.html', msg="Invalid login details")

@app.route('/InvigilatorLogin', methods=['GET', 'POST'])
def InvigilatorLogin():
   return render_template('InvigilatorLogin.html', msg='')

@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', msg='')

@app.route('/AdminLogin', methods=['GET', 'POST'])
def AdminLogin():
   return render_template('AdminLogin.html', msg='')

@app.route('/AdminLoginAction', methods=['GET', 'POST'])
def AdminLoginAction():
    if request.method == 'POST' and 't1' in request.form and 't2' in request.form:
        user = request.form['t1']
        password = request.form['t2']
        if user == "admin" and password == "admin":
            return render_template('AdminScreen.html', msg="Welcome "+user)
        else:
            return render_template('AdminLogin.html', msg="Invalid login details")

@app.route('/Logout')
def Logout():
    return render_template('index.html', msg='')

if __name__ == '__main__':
    app.run(debug=True)

