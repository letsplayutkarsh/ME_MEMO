from flask import Flask, render_template, url_for,request,flash,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail , Message
from flask_wtf import FlaskForm

from forms import SaveForm, LoginForm , WriteForm ,EditForm,ResetForm,EmailForm,FindForm
from wtforms import StringField, PasswordField, SubmitField,SelectField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError

import os
import pyttsx3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bro its not hello world'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'mynotesappbyflask@gmail.com'
app.config['MAIL_PASSWORD'] = "MyNotesApp@123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
mail=Mail(app)
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)



class SignupForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField("email",validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("confirm password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_name(self,name):
        if User.query.filter_by(username=name.data).first():
            raise ValidationError('user name already taken')

    def validate_email(self,email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('user email already taken')

class ResetForm(FlaskForm):
    email = StringField("email",validators=[DataRequired(), Email()])
    submit = SubmitField('GET')

    def validate_email(self,email):

        if not User.query.filter_by(email=email.data).first():
            raise ValidationError('email dont match')

class User(db.Model):
    id = db.Column(db.Integer ,primary_key=True)
    username = db.Column(db.String(20), unique=True , nullable=False)
    email = db.Column(db.String(20), unique=True , nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):                         #for my checking purpose
        return "User is {}".format(self.username)

class Friends(db.Model):
    id = db.Column(db.Integer ,primary_key=True)
    origin = db.Column(db.String(20),unique=False,nullable=False)
    isfriend = db.Column(db.String(20),unique=False,nullable=False)

class Requesters(db.Model):
    id = db.Column(db.Integer ,primary_key=True)
    origins = db.Column(db.String(20),unique=False,nullable=False)
    requester = db.Column(db.String(20),unique=False,nullable=False)


@app.route('/')
def start():
    return redirect(url_for("login"))

a=os.getcwd()
active_user = ""

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    os.chdir(a)
    global active_user

    if(form.validate_on_submit()):

        user = User.query.filter_by(username=str(form.name.data)).first()

        if(user and user.password == form.password.data):
            active_user = form.name.data
            path = os.path.join("./users",str(form.name.data))
            os.chdir(path)
            return redirect(url_for('home'))
        else:
            flash("Invalid details",'danger')
            return redirect(url_for('login'))

    return render_template('login.html', title='Login', form=form)

def forgotpassword(user):
    msg = Message('Password',sender='mynotesappbyflask@gmail.com', recipients=[user.email])
    msg.body = '''remember your password now
    password = {}'''.format(user.password)
    mail.send(msg)



@app.route("/forgot", methods=['GET', 'POST'])
def forgot():
    form = ResetForm()
    if(form.validate_on_submit()):
        user = User.query.filter_by(email=str(form.email.data)).first()
        forgotpassword(user)
        flash('Email sent','info ')
        return redirect(url_for('login'))

    return render_template('forgot.html', title='forgot', form=form)

@app.route("/signup",methods=["POST","GET"])
def signup():
    form = SignupForm()
    os.chdir(a)
    if(form.validate_on_submit()):

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.name.data, email=form.email.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Account created !", 'success')
        path = os.path.join("./users",str(form.name.data))
        os.mkdir(path)
        return redirect(url_for('login'))

    return render_template("signup.html",title="signup",form=form)

@app.route("/home",methods=["POST","GET"])
def home():
    files = os.listdir('./')
    all_file_data = []
    files.sort()
    c=0
    while True:
        if(len(files) > 0 and c < len(files)):
            if files[c].startswith("byfriend"):
                files.remove(files[c])
            else:
                c+=1
        else:
            break

    for x in files:
        text2 = open(x,'r+')
        contents = text2.read()
        text2.close()
        all_file_data.append([contents,x])

    return render_template("home.html",title="home",all_file_data=all_file_data)

@app.route("/write",methods=["POST","GET"])
def write():
    form = WriteForm()
    if(form.filename.data and form.text.data):
        name = form.filename.data
        filename1=str(name) + ".txt"

        list_names = os.listdir('./')

        if(filename1 in list_names):
            flash("file already exist (try editing)",'danger')
            return redirect(url_for('write'))

        else:
            text1= form.text.data
            text2 = open(filename1,'w+')
            text2.write(text1)
            text2.close()

    if(form.validate_on_submit()):
        flash("file created !", 'success')
        return redirect(url_for('home'))
    return render_template("write.html",title="write",form=form)

file_name=""

@app.route("/newread" , methods=["POST","GET"])
def newread():
    files = os.listdir('./')
    files.sort()
    c=0
    while True:
        if(len(files) > 0 and c < len(files)):
            if files[c].startswith("byfriend"):
                files.remove(files[c])
            else:
                c+=1
        else:
            break
    return render_template("newread.html",title="read",files=files)

@app.route("/sharednotes" , methods=["POST","GET"])
def sharednotes():
    shared = []
    files = os.listdir('./')
    files.sort()
    c=0
    while True:
        if(len(files) > 0 and c < len(files)):
            if files[c].startswith("byfriend"):
                shared.append(files[c])
                files.remove(files[c])
            else:
                c+=1
        else:
            break
    return render_template("newread2.html",title="read",files=shared)

@app.route("/newcontents2",methods=["POST","GET"])
def newcontents2():
    global file_name
    file=request.form.get("file")
    file = str(file) + ".txt"
    file_name = file
    text2 = open(file,'r+')
    contents = text2.read()
    text2.close()
    return render_template('contents2.html',title="read",contents=contents)


@app.route("/save",methods=["POST","GET"])
def save():
    global file_name
    form = SaveForm()
    list_names = os.listdir('./')

    if(form.validate_on_submit()):
        name = form.filename.data
        filename1=str(name) + ".txt"

        if(filename1 in list_names):
            flash("name already taken(try other name)",'danger')
            return redirect(url_for('save'))
        else:
            os.rename(file_name,filename1)
            flash("file renamed !",'success')
            return redirect(url_for('sharednotes'))
    return render_template('save.html',title="save",form=form)



@app.route("/newcontents",methods=["POST","GET"])
def newcontents():
    global file_name
    file=request.form.get("file")
    file = str(file) + ".txt"
    file_name = file
    text2 = open(file,'r+')
    contents = text2.read()
    text2.close()
    return render_template('contents.html',title="read",contents=contents)



@app.route("/newedit",methods=["POST","GET"])
def newedit():
    files = os.listdir('./')
    files.sort()
    c=0
    while True:
        if(len(files) > 0 and c < len(files)):
            if files[c].startswith("byfriend"):
                files.remove(files[c])
            else:
                c+=1
        else:
            break
    return render_template("newedit.html",title='edit',files=files)

filename=""

@app.route("/intermidiate",methods=["POST","GET"])
def intermidiate():
    global filename
    file=request.form.get("file")
    a = str(file) + ".txt"
    filename=a
    return redirect(url_for('newedit2'))

@app.route("/newedit2",methods=["POST","GET"])
def newedit2():
    form = EditForm()
    global filename

    text2 = open(filename,'r+')
    already = text2.read()
    text2.close()

    if(form.text.data):
        text1 = request.form.get("text")
        text2 = open(filename,'w+')
        text2.write(text1)
        text2.close()
        flash("file edited !", 'success')
        return redirect(url_for('home'))

    return render_template("edit2.html",title="edit",form=form, already = already)



@app.route("/newdelete",methods=["GET","POST"])
def newdelete():
    global nofriendfile
    files = os.listdir('./')
    files.sort()
    c=0
    while True:
        if(len(files) > 0 and c < len(files)):
            if files[c].startswith("byfriend"):
                files.remove(files[c])
            else:
                c+=1
        else:
            break
    return render_template("newdelete.html",title=delete,files=files)

@app.route("/deleteprocess",methods=["GET","POST"])
def deleteprocess():
    file=request.form.get("file")
    filename1=str(file) + ".txt"
    os.remove(filename1)
    flash("file Deleted !", 'success')
    return redirect(url_for('newdelete'))

@app.route("/share",methods=['GET', 'POST'])
def share():
    allf = Friends.query.filter_by(origin=active_user).all()
    allfriend = [x.isfriend for x in allf]
    return render_template('share.html',title="share",allfriend=allfriend)

@app.route("/sendnotes",methods=['GET','POST'])
def sendnotes():
    sendername = request.form.get("name")
    global file_name
    text2 = open(file_name,'r+')
    contents = text2.read()
    text2.close()

    os.chdir(a)
    path = os.path.join("./users",str(sendername))
    os.chdir(path)

    new_file_name = "byfriend_"+ active_user + "_" + file_name

    list_names = os.listdir('./')

    if(new_file_name in list_names):
        os.chdir(a)
        path = os.path.join("./users",str(active_user))
        os.chdir(path)
        flash("file already shared !", 'danger')
        return redirect(url_for("newread"))

    text2 = open(new_file_name,'w+')
    text2.write(contents)
    text2.close()

    os.chdir(a)
    path = os.path.join("./users",str(active_user))
    os.chdir(path)

    flash("note sent ","info")

    return redirect(url_for('home'))

@app.route("/edit_text",methods=["POST","GET"])
def edit2( ):
    form = EditForm()
    global file_name

    text2 = open(file_name,'r+')
    already = text2.read()
    text2.close()

    if(form.text.data):
        text1 = request.form.get("text")
        text2 = open(file_name,'w+')
        text2.write(text1)
        text2.close()
        flash("file edited !", 'success')
        return redirect(url_for('home'))

    return render_template("edit2.html",title="edit",form=form, already = already)



@app.route("/speech",methods=["POST","GET"])
def speech():
    engine = pyttsx3.init()
    global file_name
    text2 = open(file_name,'r+')
    contents = text2.read()
    text2.close()
    engine.setProperty('rate', 170)
    engine.say(contents)
    engine.runAndWait()
    return render_template('contents.html',title="read",contents=contents)

@app.route("/speech2",methods=["POST","GET"])
def speech2():
    engine = pyttsx3.init()
    speak = request.form.get("file")
    filename = speak + ".txt"
    text2 = open(filename,'r+')
    contents = text2.read()
    text2.close()
    engine.setProperty('rate', 170)
    engine.say(contents)
    engine.runAndWait()
    return redirect(url_for("home"))


@app.route("/EmailIt", methods=['GET', 'POST'])
def EmailIt():
    form = EmailForm()
    global file_name
    text2 = open(file_name,'r+')
    contents = text2.read()
    text2.close()
    if(form.validate_on_submit()):
        emailsender(form.email.data)
        flash('Email sent','info ')
        return render_template('contents.html',title="read",contents=contents)
    return render_template('emailit.html',title="emailit",form=form)

def emailsender(email):
    msg = Message('yourfile',sender='mynotesappbyflask@gmail.com', recipients=[email])
    global file_name
    text2 = open(file_name,'r+')
    contents = text2.read()
    text2.close()
    msg.body = ''' file sent form online note = {}

    {}

    THANK YOU '''.format(file_name,contents)
    mail.send(msg)

@app.route("/delete",methods=["POST","GET"])
def delete():
    form = ReadForm()

    if(form.filename.data and form.validate_on_submit()):
        name = form.filename.data
        filename1=str(name) + ".txt"
        list_names = os.listdir('./')
        if(filename1 in list_names):

            os.remove(filename1)
            flash("file Deleted !", 'success')
            return redirect(url_for('home'))
        else:
            flash("file do not exixt !", 'danger')

    return render_template("delete.html",title="read",form=form)

@app.route("/requests",methods=["POST","GET"])
def requests():
    reqe = Requesters.query.filter_by(origins = active_user).all()
    req = [x.requester for x in reqe]
    return render_template("requests.html",title="requests",req=req)

@app.route("/accept",methods=["POST","GET"])
def accept():
    new = request.form.get("requester")
    friend = Friends(origin = active_user, isfriend = new)
    db.session.add(friend)
    db.session.commit()

    del1 = Requesters.query.filter_by(origins = active_user , requester= new).first()
    db.session.delete(del1)
    db.session.commit()

    return redirect(url_for("requests"))

@app.route("/decline",methods=["POST","GET"])
def decline():
    new = request.form.get("requester")
    del1 = Requesters.query.filter_by(origins = active_user , requester= new).first()
    db.session.delete(del1)
    db.session.commit()

    return redirect(url_for("requests"))

@app.route("/allfriends",methods=["POST","GET"])
def allfriends():
    allf = Friends.query.filter_by(origin=active_user).all()
    allfriend = [x.isfriend for x in allf]
    return render_template("allfriends.html",title=allfriends , allfriend=allfriend)

@app.route("/find",methods=["POST","GET"])
def find():
    form = FindForm()

    if(form.validate_on_submit()):

        user = User.query.filter_by(username=str(form.user.data)).first()
        if(user):
            frnd = Friends.query.filter_by(origin = active_user, isfriend = form.user.data).first()
            reqe = Requesters.query.filter_by(origins = form.user.data , requester=active_user).first()
            if(reqe):
                flash('REQUEST-ALREADY-SENT','danger')
                return redirect(url_for('find'))
            elif(frnd):
                flash('YOU ARE ALREADY FRIENDS','danger')
                return redirect(url_for('find'))

            elif(not (reqe and frnd)):
                req = Requesters(origins=form.user.data, requester=active_user)
                db.session.add(req)
                db.session.commit()
                flash('REQUEST-SENT','success')
                return redirect(url_for('home'))
        else:
            flash("NO USER FOUND",'danger')
            return redirect(url_for('find'))
    return render_template("find.html",title="find",form=form)


if __name__ == "__main__":
    app.run()
