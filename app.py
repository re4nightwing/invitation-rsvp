import os
from flask import Flask, render_template, jsonify, redirect, request, flash, url_for, session
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from flask_wtf import CSRFProtect
from bcrypt import checkpw
from PIL import Image, ImageDraw, ImageFont

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

def create_invitation(image_id, input_image_path, output_dir, name, font_path, y_position, font_size):
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)

    # Load the font
  try:
    font = ImageFont.truetype(font_path, font_size)
  except IOError:
    print("Font file not found. Please check the font path.")
    return

  try:
    image = Image.open(input_image_path)

    if image.mode != 'RGB':
      image = image.convert('RGB')

    draw = ImageDraw.Draw(image)

    image_width, image_height = image.size

    text_bbox = draw.textbbox((0, 0), name, font=font)  # Get bounding box
    text_width = text_bbox[2] - text_bbox[0]  # Width of the text
    x_position = (image_width - text_width) // 2  # Center text horizontally

    draw.text((x_position, y_position), name, font=font, fill="black")

    max_width = 1200
    max_height = 1200
    image.thumbnail((max_width, max_height))  # This will keep the aspect ratio intact

    output_path = os.path.join(output_dir, f"invitation_{image_id}.png")
    image.save(output_path, format='JPEG', quality=80, optimize=True)

    print(f"Saved: {output_path}")
    return 1
  except Exception as e:
    print(f'An error occurred: {str(e)}')
    return 0



######## 404 page
@app.errorhandler(404)
def page_not_found(e):
  context = {
    'msg': e
  }
  return render_template('404.html', context=context), 404

""" 
@app.route('/', methods=['GET', 'POST'])
def home():
  return render_template('index.html') 
"""

@app.route('/<string:id>/<string:username>', methods=['GET', 'POST'])
def home_with_user(id, username):
  user = rsvp_information.query.filter_by(id=id).first()
  if not user:
    context = {
      'msg': "Invalid User"
    }
    return render_template('404.html', context=context), 404
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
  invitees = rsvp_information.query.all()
  context={
    "invitees" : invitees
  }
  return render_template('dashboard.html', context=context)

@app.route('/add-invitee', methods=['POST'])
def add_invitee():
  invitee_name = request.form.get('invitee-name')
  if(invitee_name):
    exist_user = rsvp_information.query.filter_by(username=invitee_name).first()
    if exist_user:
      flash(f"User with the name {exist_user} exists", "danger")
    else:
      try:
        new_id = make_unique()
        new_invitee = rsvp_information(id=new_id, username=invitee_name)
        invitation = create_invitation(new_id, "static/img/template.jpg", "static/img/invitations/", invitee_name, "static/other/Birthstone-Regular.ttf", 850, 70)
        if invitation:
          db.session.add(new_invitee)
          db.session.commit()
          flash(f"User {invitee_name} invited", "success")
        else:
          flash(f"An error occurred while creating the invitation.", "danger")
      except Exception as e:
        print(e)
        flash(f"An error occurred while updating the database.", "danger")
  return redirect(url_for('dashboard_page'))

@app.route('/delete-invitee', methods=['POST'])
def delete_invitee():
  invitee_id = request.form.get('user-id')
  if(invitee_id):
    exist_user = rsvp_information.query.filter_by(id=invitee_id).first()
    if exist_user:
      try:
        db.session.delete(exist_user)
        db.session.commit()
        flash(f"User {exist_user.username} deleted", "success")
      except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    else:
      flash(f"User with the id {invitee_id} does not exist", "danger")
  return redirect(url_for('dashboard_page'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
  app.run(host="0.0.0.0", debug=True)