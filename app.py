import os
from flask import Flask, render_template, jsonify, redirect, request, flash, url_for, session
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from flask_wtf import CSRFProtect
from bcrypt import checkpw

load_dotenv()
DB_USER=os.environ.get("DB_USER")
DB_PASS=os.environ.get("DB_PASS")
DB_HOST=os.environ.get("DB_HOST")
DB_NAME=os.environ.get("DB_NAME")

app = Flask(__name__)
db = SQLAlchemy()

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'

db.init_app(app)
csrf = CSRFProtect(app) 

class rsvp_information(db.Model):
  id = db.Column(db.String(100), primary_key=True)
  username = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(100), nullable=True)
  phonenumber = db.Column(db.String(100), nullable=True)
  status = db.Column(db.String(100), nullable=True)
  created = db.Column(db.DateTime, server_default=db.func.now())
  updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

  def __repr__(self):
    return f"<User {self.username}>"
  
class admin_info(db.Model):
  username = db.Column(db.String(100), nullable=False, primary_key=True)
  password = db.Column(db.String(100), nullable=False)
  created = db.Column(db.DateTime, server_default=db.func.now())
  updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

  def __repr__(self):
    return f"<User {self.username}>"

def make_unique():
    ident = uuid4().__str__()
    return ident

######## 404 page
@app.errorhandler(404)
def page_not_found(e):
  context = {
    'msg': e
  }
  return render_template('404.html', context=context), 404

""" @app.route('/', methods=['GET', 'POST'])
def home():
  return render_template('index.html') """

@app.route('/<string:id>/<string:username>', methods=['GET', 'POST'])
def home_with_user(id, username):
  user = rsvp_information.query.filter_by(id=id).first()
  if not user:
    return redirect(url_for("page_not_found"))
  context = {
    'id': user.id,
    'username': user.username,
    'email': user.email,
    'phonenumber': user.phonenumber,
    'status': user.status,
  }
  return render_template('index.html', context=context)

@app.route('/submit', methods=['POST'])
def submit_data():
  user_id = request.form.get('userID')
  name = request.form.get('nameInput')
  email = request.form.get('inputEmail')
  phone = request.form.get('inputPhoneNo')
  attendance_status = request.form.get('btnradio')

  user = rsvp_information.query.filter_by(id=user_id).first()
  
  if(user):
    user.username = name
    user.email = email if email else user.email  # Only update if provided
    user.phonenumber = phone
    user.status = attendance_status  # Assuming there's a field for this
    try:
      db.session.commit()
      flash('Record updated successfully!', 'success')
    except Exception as e:
      db.session.rollback()  # Rollback in case of an error
      flash(f'An error occurred: {str(e)}', 'danger')
  else:
    flash('User not found!', 'danger')
  
  return redirect(url_for("home_with_user", id=user_id, username=name))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
  if 'username' in session:
    return redirect(url_for('dashboard_page'))
  if request.method == "POST":
    username = request.form.get('username')
    password = request.form.get('password')
    b_password = password.encode('utf-8')
    admin_user = admin_info.query.filter_by(username=username).first()
    if admin_user and checkpw(b_password, (admin_user.password).encode('utf-8')):
      session['username'] = admin_user.username
      flash("User Logged In Successfully.", "success")
      return redirect(url_for('admin_login'))
    else:
      flash("Invalid user", "danger")
      return redirect(url_for('admin_login'))
  context={}
  return render_template('admin.html', context=context)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard_page():
  if 'username' not in session:
    return redirect(url_for('admin_login'))
  context={}
  return render_template('dashboard.html', context=context)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
  app.run(host="0.0.0.0", debug=True)