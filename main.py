from flask import Flask
from flask import Flask, render_template, Response, redirect, request, session, abort, url_for
from camera import VideoCamera
from datetime import datetime
from datetime import date
import datetime
import random
from random import seed
from random import randint
import threading
import os
import time
import shutil
import imagehash
import PIL.Image
from PIL import Image
import urllib.request
import urllib.parse

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  charset="utf8",
  database="illusion_offensive"
)


app = Flask(__name__)
##session key
app.secret_key = 'abcdef'
@app.route('/',methods=['POST','GET'])
def index():
    cnt=0
    act=""
    msg=""
    if request.method=='GET':
        act = request.args.get('act')
    if request.method=='POST':
        card=request.form['card']
        
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM register where card=%s",(card, ))
        cnt = mycursor.fetchone()[0]
        if cnt>0:
            msg="success"
            session['username'] = card
            mycursor.execute("SELECT face_st FROM register where card=%s",(card, ))
            face_st = mycursor.fetchone()[0]
            if face_st==1:
                return redirect(url_for('verify_face'))
            else:
                return redirect(url_for('verify_aadhar'))
            
            
        else:
            msg="fail"
            print("Incorrect")
        

    return render_template('index.html',msg=msg,act=act)


#################################>>>>>>>>>>>>>>>>>>USER<<<<<<<<<<<<<<<<############################################################
'''@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        return render_template('register.html')
    else:
        return render_template('register.html')'''

@app.route('/register',methods=['POST','GET'])
def register():
    result=""
    act=""
    if request.method=='POST':
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        address=request.form['address']
        bank=request.form['bank']
        branch=request.form['branch']
        card=request.form['card']
        account=request.form['accno']
        uname=request.form['username']
        password=request.form['password']

        aadhar1=request.form['aadhar1']
        aadhar2=request.form['aadhar2']
        aadhar3=request.form['aadhar3']

        face_st=request.form['face_st']
        
        
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        mycursor.execute("SELECT count(*) FROM register where card=%s",(card, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM register")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            sql = "INSERT INTO register(id, name, mobile, email, address,  bank, accno, branch, card, deposit, username, password, rdate, aadhar1, aadhar2, aadhar3, face_st, fimg) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (maxid, name, mobile, email, address, bank, account, branch, card, '10000', uname, password, rdate, aadhar1, aadhar2, aadhar3, face_st, '')
            print(sql)
            mycursor.execute(sql, val)
            mydb.commit()            
            print(mycursor.rowcount, "record inserted.")
            if face_st=="1":
                return redirect(url_for('add_photo',vid=maxid))
            #if mycursor.rowcount==1:
            #    result="Registered Success"
            else:
                return redirect(url_for('index',act='success'))
        else:
            result="Card No. already Exist!"
    return render_template('register.html',result=result)

@app.route('/add_photo',methods=['POST','GET'])
def add_photo():
    vid=""
    if request.method=='GET':
        vid = request.args.get('vid')
    if request.method=='POST':
        vid=request.form['vid']
        fimg="v"+vid+".jpg"
        cursor = mydb.cursor()

        cursor.execute("SELECT max(id)+1 FROM vt_face")
        maxid = cursor.fetchone()[0]
        if maxid is None:
            maxid=1
        vface="v"+vid+"_"+str(maxid)+".jpg"
        sql = "INSERT INTO vt_face(id, vid, vface) VALUES (%s, %s, %s)"
        val = (maxid, vid, vface)
        print(val)
        cursor.execute(sql,val)
        mydb.commit()
            
        cursor.execute('update register set fimg=%s WHERE id = %s', (vface, vid))
        mydb.commit()
        shutil.copy('faces/f1.jpg', 'static/photo/'+vface)
        return redirect(url_for('index',act='success'))
        
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM register")
    data = cursor.fetchall()
    return render_template('add_photo.html',data=data, vid=vid)

@app.route('/login1')
def login1():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM numbers")
    value = mycursor.fetchall()
    return render_template('login.html', value=value)



@app.route('/login',methods=['POST','GET'])
def login():
    uname=""
##    value=["1","2","3","4","5","6","7","8","9","0"]
##    change=random.shuffle(value)
##    print(change)
    if 'username' in session:
        uname = session['username']
    print(uname)
    mycursor1 = mydb.cursor()

    mycursor1.execute("SELECT * FROM register where card=%s",(uname, ))
    value = mycursor1.fetchone()
    accno=value[5]
    session['accno'] = accno
    
    mycursor1.execute("SELECT number FROM numbers order by rand()")
    value = mycursor1.fetchall()
    msg=""
        
    if request.method == 'POST':
        password1 = request.form['password']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM register where card=%s && password=%s",(uname, password1))
        myresult = mycursor.fetchone()[0]
        if password1=="":
            
            return render_template('login.html')
        else:
            
            #if str(password1)==str(myresult[10]):
            if myresult>0:
                #ff2=open("log.txt","w")
                #ff2.write(password1)
                #ff2.close()
                result=" Your Logged in sucessfully**"
                
                return redirect(url_for('userhome'))
            else:
                msg="Your logged in fail!!!"
                #return render_template('userhome.html',result=result)
    
    
    return render_template('login.html',value=value,msg=msg)



@app.route('/userhome')
def userhome():
    uname=""
    if 'username' in session:
        uname = session['username']
        accno = session['accno']

    name=""
    
   
    

    print(uname)
    mycursor1 = mydb.cursor()
    mycursor1.execute("SELECT * FROM register where card=%s",(uname, ))
    value = mycursor1.fetchone()
    print(value)
    name=value[1]  
        
    return render_template('userhome.html',name=name)

'''@app.route('/deposit')
def deposit():
    return render_template('deposit.html')
@app.route('/deposit_amount',methods=['POST','GET'])
def deposit_amount():
    if request.method=='POST':
        name=request.form['name']
        accountno=request.form['accno']
        amount=request.form['amount']
        today = date.today()
        rdate = today.strftime("%b-%d-%Y")
        mycursor = mydb.cursor()
        mycursor.execute("SELECT max(id)+1 FROM event")
        maxid = mycursor.fetchone()[0]
        sql = "INSERT INTO event(id, name, accno, amount, rdate) VALUES (%s, %s, %s, %s, %s)"
        val = (maxid, name, accountno, amount, rdate)
        mycursor.execute(sql, val)
        mydb.commit()   
    return render_template('userhome.html')'''

'''@app.route('/withdraw')
def withdraw():

    
    return render_template('withdraw.html')'''

@app.route('/verify_face',methods=['POST','GET'])
def verify_face():
    msg=""
    ss=""
    uname=""
    if 'username' in session:
        uname = session['username']
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM register WHERE card = %s', (uname, ))
    account = cursor.fetchone()
    mobile=account[3]
    vid=account[0]
    if request.method=='POST':
        shutil.copy('faces/f1.jpg', 'faces/s1.jpg')
        cutoff=10
        img="v"+str(vid)+".jpg"
        cursor.execute('SELECT * FROM vt_face WHERE vid = %s', (vid, ))
        dt = cursor.fetchall()
        for rr in dt:
            hash0 = imagehash.average_hash(Image.open("static/photo/"+rr[2])) 
            hash1 = imagehash.average_hash(Image.open("faces/s1.jpg"))
            cc1=hash0 - hash1
            if cc1<=10:
                ss="ok"
                break
            else:
                ss="no"
        if ss=="ok":
            return redirect(url_for('verify_aadhar', msg=msg))
        else:
            xn=randint(1000, 9999)
            otp=str(xn)
            message="Some other person acces your ATM card, Your OTP:"+otp
            cursor1 = mydb.cursor()
            cursor1.execute('update register set otp=%s WHERE card = %s', (otp, uname))
            mydb.commit()
        
            params = urllib.parse.urlencode({'token': 'b81edee36bcef4ddbaa6ef535f8db03e', 'credit': 2, 'sender': 'RnDTRY', 'message':message, 'number':mobile})
            url = "http://pay4sms.in/sendsms/?%s" % params
            with urllib.request.urlopen(url) as f:
                print(f.read().decode('utf-8'))
                print("sent"+str(mobile))
            
            return redirect(url_for('otp'))
                
    return render_template('verify_face.html',msg=msg)

@app.route('/otp', methods=['GET', 'POST'])
def otp():
    msg=""
    if 'username' in session:
        uname = session['username']
    cursor = mydb.cursor()
    cursor.execute('SELECT otp FROM register WHERE card = %s', (uname, ))
    account = cursor.fetchone()[0]
    key=account
    
    if request.method=='POST':
        otp=request.form['otp']
        
        if otp==key:
            session['username'] = uname
            
            return redirect(url_for('verify_aadhar'))
        else:
            msg = 'OTP wrong!'
    return render_template('otp.html',msg=msg)


@app.route('/verify_aadhar', methods=['GET', 'POST'])
def verify_aadhar():
    msg=""
    if 'username' in session:
        uname = session['username']
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM register WHERE card = %s', (uname, ))
    account = cursor.fetchone()
    
    
    if request.method=='POST':
        aadhar=request.form['aadhar']
        
        if aadhar==account[13] or aadhar==account[14] or aadhar==account[15]:
            session['username'] = uname
            
            return redirect(url_for('login'))
        else:
            msg = 'Aadhar no. wrong!'
    return render_template('verify_aadhar.html',msg=msg)

@app.route('/withdraw',methods=['POST','GET'])
def withdraw():
    uname=""
    if 'username' in session:
        uname = session['username']
        accno = session['accno']
    msg=""
    amt=0
    amt1=0
    amt2=0
    if request.method=='POST':
        
        amount1=request.form['amount']
        
        mycursor = mydb.cursor()

        mycursor.execute("SELECT amount FROM admin where username='admin'")
        amt1 = mycursor.fetchone()[0]

        mycursor.execute("SELECT deposit FROM register where card=%s",(uname, ))
        amt2 = mycursor.fetchone()[0]

        amt=int(amount1)
        if amt<=amt1:

            if amt<=amt2:
                mycursor.execute("UPDATE admin SET amount=amount-%s WHERE username='admin'",(amount1, ))
                mydb.commit()
                mycursor.execute("UPDATE register SET deposit=deposit-%s WHERE card=%s",(amount1, uname))
                mydb.commit()

                now = datetime.datetime.now()
                rdate=now.strftime("%d-%m-%Y")
                mycursor.execute("SELECT max(id)+1 FROM event")
                maxid = mycursor.fetchone()[0]
                if maxid is None:
                    maxid=1
                sql = "INSERT INTO event(id, accno, amount, rdate) VALUES (%s, %s, %s, %s)"
                val = (maxid, accno, amt, rdate)
                mycursor.execute(sql, val)
                msg="Withdraw success..."
            else:
                msg="Your Account balance is low!"
        else:
            msg="Cash is not available in ATM!!"
        
    return render_template('withdraw.html',msg=msg)


@app.route('/balance')
def balance():
    uname=""
    if 'username' in session:
        uname = session['username']
        accno = session['accno']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register where card=%s",(uname, ))
    data = mycursor.fetchone()
    deposit=data[9]
    print(str(deposit))
    return render_template('balance.html', data=deposit)

##@app.route('/login2')
##def login2():
##    return render_template('login2.html')
@app.route('/admin_login', methods=['POST','GET'])
def admin_login():
    result=""
    if request.method == 'POST':
        username1 = request.form['username']
        password1 = request.form['password']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM admin where username=%s && password=%s",(username1,password1))
        myresult = mycursor.fetchone()[0]
        if myresult>0:
            result=" Your Logged in sucessfully**"
            return redirect(url_for('admin')) 
        else:
            result="Your logged in fail!!!"
                
    
    return render_template('login2.html',result=result)

@app.route('/admin',methods=['POST','GET'])
def admin():
    amt="0"
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM admin where username='admin'")
    result = mycursor.fetchone()
    amt=result[2]
    if request.method == 'POST':
        amount = request.form['amount']
    
        mycursor = mydb.cursor()
        mycursor.execute("update admin set amount=%s where username='admin'",(amount, ))
        mydb.commit()
    
    return render_template('admin.html', amt=amt)   

'''@app.route('/deposit_view')
def deposit_view():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM event")
    result = mycursor.fetchall()
    return render_template('view_deposit.html', result=result)'''

@app.route('/user_view')
def user_view():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register")
    result = mycursor.fetchall()
    return render_template('user_view.html', result=result)

@app.route('/view_withdraw')
def view_withdraw():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM event order by id desc")
    result = mycursor.fetchall()
    return render_template('view_withdraw.html', result=result)

@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    #session.pop('username', None)
    return redirect(url_for('index'))

def gen(camera):
    
    while True:
        frame = camera.get_frame()
        
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    
@app.route('/video_feed')
        

def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=5000)
