from enum import unique
import os
from flask import Flask,render_template,request,redirect,url_for,flash  
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column,String,Text,Integer
import random,string
from flask_login import LoginManager,UserMixin, login_manager , login_required,login_user,logout_user
from werkzeug.security import generate_password_hash,check_password_hash
from flask_migrate import Migrate

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data1.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mykey'

db = SQLAlchemy(app)
Migrate(app,db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'




class url(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer(),primary_key=True)
    original_url = db.Column(db.String(120),unique=False,nullable=False)
    shorten_url = db.Column(db.String(7),unique=False,nullable=False)

    def __init__(self,original_url,shorten_url):
        self.original_url = original_url
        self.shorten_url = shorten_url
    
    def __repr__(self):
        return "original_url:{} shorten_url:{}".format(self.original_url,self.shorten_url)

@app.before_first_request
def create_tables():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model,UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))

    def __init__(self,email,password):
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)


@app.before_first_request
def create_tables():
    db.create_all()



@app.route("/")
def home_get():
    return render_template("index.html")

@app.route('/register', methods=['GET','POST'])
def register():
    email = request.form.get('email')
    u = User.query.filter_by(email=email).first()
    if request.method == "POST":
        if not u:
           user = User(email=request.form.get('email'), password=request.form.get('password'))
           db.session.add(user)
           db.session.commit()
           return redirect(url_for('login'))
        else:
           flash("user mail already exists")
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get('email')).first()

        if user is not None and user.check_password(request.form.get('password')):
            login_user(user)
            next = request.args.get('next')

            if next == None or not next[0]=='/':
                next = url_for('home_get')
            return redirect(next)
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_get'))


@app.route("/", methods=['POST'])
@login_required
def home_post():
    list = []
    alnum = ''
    letters = string.ascii_letters
    numbers = '123456789'
    alnum = letters + numbers 
    list = random.choices(alnum,k=6)
    x = " "
    for i in list:
        x += i 
    shorten_url = request.host_url + x
    original_url = request.form.get('original_url')
    new_url = url(original_url,shorten_url)
    db.session.add(new_url)
    db.session.commit()
    return render_template("index.html",shorten_url=shorten_url)

@app.route("/history")
def history_get():
    urls = url.query.all()
    return render_template("history.html", urls=urls)

@app.route("/<x>")
def fun(x):
    s = url.query.filter_by(shorten_url="{}".format("http://127.0.0.1:5000/"+x)).first()
    if (s):
        return redirect(s.original_url)
    else:
        return "INCORRECT URL"




if __name__=="__main__":
    app.run(debug=True)