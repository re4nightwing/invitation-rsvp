from app import db, app, admin_info

with app.app_context():
  db.drop_all()
  db.create_all()
  new_user = admin_info(username="upekshasavindu@gmail.com", password="$2b$12$LeJThDEg10HJ3zMVmlLx6uWGhaBgUIRvfImJD2fvZhCYSw.pAlXpq")
  db.session.add(new_user)
  db.session.commit()