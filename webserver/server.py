"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

from datetime import datetime, date
import json
import os
from psycopg2 import connect, sql
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import abort, g, Flask, flash, jsonify, redirect, render_template, request, Response, session
from entities import *

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/static')
app = Flask(__name__, template_folder=tmpl_dir, static_folder=static_dir)

DB_USER = "sl5185"
DB_PASSWORD = ""
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    user = lambda:None
    user.__dict__ = json.loads(session['user'])
    context = dict(data = user.name)
    if user.is_admin:
      return render_template("index-admin-home.html", **context)
    elif user.is_student:
      courses = get_course_by_student_id(user.user_id)
      context['courses'] = courses
      return render_template("index-student-home.html", **context)
    else:
      courses = get_course_by_instructor_id(user.user_id)
      context['courses'] = courses
      return render_template("index-instructor-home.html", **context)

@app.route('/login', methods=['POST'])
def login():

  username = str(request.form['username'])
  hash = str(request.form['password'])

  user = get_user_by_user_id(username)
  print(user.__dict__)
  if user is None or user.hash != hash:
    flash('The input username or password is incorrect!')
  else:
    session['logged_in'] = True
    session['user'] = json.dumps(user.__dict__, cls=DatetimeEncoder)
  return redirect('/')

@app.route("/logout")
def logout():
  session['logged_in'] = False
  session['user'] = None
  return redirect('/')

@app.route('/rooms')
def rooms(error=None):
  user = lambda:None
  user.__dict__ = json.loads(session['user'])
  if user.is_admin:
    rooms = get_all_rooms()
    context = dict(data = rooms)
    if error is not None:
      context['error'] = error
      return render_template("index-admin-rooms.html", **context)
    else:
      return render_template("index-admin-rooms-no-error.html", **context)
  else:
    redirect('/')

@app.route('/add-room', methods=['POST'])
def add_room():
  room_id = request.form['room_id']
  location = request.form['location']
  error = None
  try:
    cmd = 'INSERT INTO rooms VALUES (:room_id, :location)';
    g.conn.execute(text(cmd), room_id = room_id, location = location);
  except Exception as e:
    error = str(e)
  return rooms(error)

@app.route('/update-room', methods=['POST'])
def update_room():
  room_id = request.form['room_id']
  location = request.form['location']
  error = None
  try:
    cmd = 'UPDATE rooms SET location = (:location) WHERE room_id = (:room_id)';
    g.conn.execute(text(cmd), room_id = room_id, location = location);
  except Exception as e:
    error = str(e)
  return rooms(error)

@app.route('/users')
def users(error=None):
  user = lambda:None
  user.__dict__ = json.loads(session['user'])
  if user.is_admin:
    users = get_all_users()
    context = dict(data = users)
    if error is not None:
      context['error'] = error
      return render_template("index-admin-users.html", **context)
    else:
      return render_template("index-admin-users-no-error.html", **context)
  else:
    redirect('/')

@app.route('/add-user', methods=['POST'])
def add_user():
  user_id = request.form['user_id']
  password_hash = request.form['password_hash']
  name = request.form['name']
  birthdate = request.form['birthdate']
  is_admin = request.form['is_admin']
  class_num = None if request.form['class_num'] == '' else request.form['class_num']
  major = None if request.form['major'] == '' else request.form['major']
  concentration = None if request.form['concentration'] == '' else request.form['concentration']
  department = None if request.form['department'] == '' else request.form['department']
  title = None if request.form['title'] == '' else request.form['title']
  error = None
  try:
    cmd = 'INSERT INTO users VALUES (:user_id, :password_hash, :name, :birthdate, :is_admin, :class_num, :major, :concentration, :department, :title)';
    g.conn.execute(text(cmd), user_id = user_id, password_hash = password_hash, name = name, birthdate = birthdate, is_admin = is_admin, class_num = class_num, major = major, concentration = concentration, department = department, title = title);
  except Exception as e:
    error = str(e)
  return users(error)

@app.route('/update-user', methods=['POST'])
def update_user():
  user_id = request.form['user_id']
  password_hash = request.form['password_hash']
  name = request.form['name']
  birthdate = request.form['birthdate']
  is_admin = request.form['is_admin']
  class_num = None if request.form['class_num'] == '' else request.form['class_num']
  major = None if request.form['major'] == '' else request.form['major']
  concentration = None if request.form['concentration'] == '' else request.form['concentration']
  department = None if request.form['department'] == '' else request.form['department']
  title = None if request.form['title'] == '' else request.form['title']
  error = None
  try:
    cmd = 'UPDATE users SET password_hash = (:password_hash), name = (:name), birthdate = (:birthdate), is_admin = (:is_admin), class = (:class_num), major= (:major), concentration = (:concentration), department = (:department), title = (:title) WHERE user_id = (:user_id)';
    g.conn.execute(text(cmd), user_id = user_id, password_hash = password_hash, name = name, birthdate = birthdate, is_admin = is_admin, class_num = class_num, major = major, concentration = concentration, department = department, title = title);
  except Exception as e:
    error = str(e)
  return users(error)

@app.route('/courses')
def courses(error=None):
  user = lambda:None
  user.__dict__ = json.loads(session['user'])
  if user.is_admin:
    courses = get_all_courses()
    context = dict(data = courses)
    if error is not None:
      context['error'] = error
      return render_template("index-admin-courses.html", **context)
    else:
      return render_template("index-admin-courses-no-error.html", **context)
  elif user.is_student:
    courses = get_all_courses()
    waitlists = get_waitlist_by_student_id(user.user_id)
    enrollment = get_course_by_student_id(user.user_id)
    context = dict(courses = courses, waitlists = waitlists, enrollment = enrollment)
    if error is not None:
      context['error'] = error
      return render_template("index-student-courses.html", **context)
    else:
      return render_template("index-student-courses-no-error.html", **context)
  else:
    waitlists = get_waitlist_by_instructor_id(user.user_id)
    enrollment = get_enroll_by_instructor_id(user.user_id)
    context = dict(waitlists = waitlists, enrollment = enrollment)
    if error is not None:
      context['error'] = error
      return render_template("index-instructor-courses.html", **context)
    else:
      return render_template("index-instructor-courses-no-error.html", **context)

@app.route('/add-to-waitlist', methods=['POST'])
def add_to_waitlist():
  user = lambda:None
  user.__dict__ = json.loads(session['user'])
  course_id = request.form['course_id']
  error = None
  if is_enrolled_or_waitlisted(user.user_id, course_id):
    return courses(f"Cannot waitlist classes you have are waitlisted on or enrolled in.")
  try:
    cmd = 'INSERT INTO waitlists VALUES (:course_id, :user_id)';
    g.conn.execute(text(cmd), user_id = user.user_id, course_id = course_id);
  except Exception as e:
    error = str(e)
  return courses(error)

@app.route('/get-off-waitlist', methods=['POST'])
def get_off_waitlist():
  user = lambda:None
  user.__dict__ = json.loads(session['user'])
  course_id = request.form['course_id']
  error = None
  try:
    cmd = 'DELETE FROM waitlists WHERE course_id = (:course_id) AND user_id = (:user_id)';
    g.conn.execute(text(cmd), user_id = user.user_id, course_id = course_id);
  except Exception as e:
    error = str(e)
  return courses(error)

@app.route('/enroll-student-to-class', methods=['POST'])
def enroll_student_to_class():
  user = lambda:None
  user.__dict__ = json.loads(session['user'])
  user_id = request.form['user_id']
  course_id = request.form['course_id']
  if is_user_id_waitlisted_for_course_id(user_id, course_id) == False:
    return courses(f"Student {user_id} is not on the waitlist of {course_id}.")
  error = None
  if is_class_taught_by_the_user(user.user_id, course_id) == False:
    return courses(f"Cannot enroll students to classes that you do not teach.")
  try:
    cmd1 = 'DELETE FROM waitlists WHERE user_id = (:user_id) AND course_id = (:course_id)'
    cmd2 = 'INSERT INTO enrolls VALUES (:course_id, :user_id)';
    g.conn.execute(text(cmd1), user_id = user_id, course_id = course_id);
    g.conn.execute(text(cmd2), user_id = user_id, course_id = course_id);
  except Exception as e:
    error = str(e)
  return courses(error)

@app.route('/add-course', methods=['POST'])
def add_course():
  course_id = request.form['course_id']
  name = request.form['name']
  term = request.form['term']
  description = request.form['description']
  schedule = request.form['schedule']
  is_open = request.form['is_open']
  is_over = request.form['is_over']
  room_id = request.form['room_id']
  user_id = request.form['user_id']
  error = None
  try:
    cmd = 'INSERT INTO courses_uses_teaches VALUES (:course_id, :name, :term, :description, :schedule, :is_open, :is_over, :room_id, :user_id)';
    g.conn.execute(text(cmd), course_id = course_id, name = name, term = term, description = description, schedule = schedule, is_open = is_open, is_over = is_over, room_id = room_id, user_id = user_id);
  except Exception as e:
    error = str(e)
  return courses(error)

@app.route('/update-course', methods=['POST'])
def update_course():
  course_id = request.form['course_id']
  name = request.form['name']
  term = request.form['term']
  description = request.form['description']
  schedule = request.form['schedule']
  is_open = request.form['is_open']
  is_over = request.form['is_over']
  room_id = request.form['room_id']
  user_id = request.form['user_id']
  error = None
  try:
    cmd = 'UPDATE courses_uses_teaches SET name = (:name), term = (:term), description = (:description), schedule = (:schedule), is_open= (:is_open), is_over = (:is_over), room_id = (:room_id), user_id = (:user_id) WHERE course_id = (:course_id)';
    g.conn.execute(text(cmd), course_id = course_id, name = name, term = term, description = description, schedule = schedule, is_open = is_open, is_over = is_over, room_id = room_id, user_id = user_id);
  except Exception as e:
    error = str(e)
  return courses(error)

class DatetimeEncoder(json.JSONEncoder):
    def default(self, ob):
        if isinstance(ob, (datetime, date)):
            return str(ob)
        return json.JSONEncoder.default(self, ob)

def get_user_by_user_id(user_id):
  cursor = g.conn.execute("SELECT * FROM users WHERE user_id = %(user_id)s", {'user_id': user_id})
  result = cursor.fetchone()
  cursor.close()
  if result is None:
    return None
  else:
    return User(*result)

def is_user_id_waitlisted_for_course_id(user_id, course_id):
  cursor = g.conn.execute("SELECT * FROM waitlists WHERE user_id = %(user_id)s AND course_id = %(course_id)s", {'user_id': user_id, 'course_id': course_id})
  result = cursor.fetchone()
  cursor.close()
  if result is None:
    return False
  return True

def is_class_taught_by_the_user(user_id, course_id):
  cursor = g.conn.execute("SELECT * FROM courses_uses_teaches WHERE user_id = %(user_id)s AND course_id = %(course_id)s", {'user_id': user_id, 'course_id': course_id})
  result = cursor.fetchone()
  cursor.close()
  if result is None:
    return False
  return True

def is_enrolled_or_waitlisted(user_id, course_id):
  cursor = g.conn.execute("SELECT * FROM waitlists WHERE user_id = %(user_id)s AND course_id = %(course_id)s", {'user_id': user_id, 'course_id': course_id})
  result = cursor.fetchone()
  cursor.close()
  if result is None:
    cursor = g.conn.execute("SELECT * FROM enrolls WHERE user_id = %(user_id)s AND course_id = %(course_id)s", {'user_id': user_id, 'course_id': course_id})
    result = cursor.fetchone()
    cursor.close()
    if result is None:
      return False
  return True

def get_waitlist_by_instructor_id(user_id):
  cursor = g.conn.execute("SELECT * FROM waitlists w INNER JOIN courses_uses_teaches c ON w.course_id = c.course_id WHERE c.user_id = %(user_id)s", {'user_id': user_id})
  entities = []
  for result in cursor:
    entities.append(result)
  cursor.close()
  return entities

def get_enroll_by_instructor_id(user_id):
  cursor = g.conn.execute("SELECT * FROM enrolls e INNER JOIN courses_uses_teaches c ON e.course_id = c.course_id WHERE c.user_id = %(user_id)s", {'user_id': user_id})
  entities = []
  for result in cursor:
    entities.append(result)
  cursor.close()
  return entities

def get_all_courses():
  cursor = g.conn.execute("SELECT * FROM courses_uses_teaches")
  courses = []
  for result in cursor:
    courses.append(result)
  cursor.close()
  return courses

def get_all_users():
  cursor = g.conn.execute("SELECT * FROM users")
  users = []
  for result in cursor:
    users.append(result)
  cursor.close()
  return users

def get_all_rooms():
  cursor = g.conn.execute("SELECT * FROM rooms")
  rooms = []
  for result in cursor:
    rooms.append(result)
  cursor.close()
  return rooms

def get_course_by_student_id(user_id):
  cursor = g.conn.execute("SELECT c FROM courses_uses_teaches c INNER JOIN enrolls e on c.course_id = e.course_id WHERE e.user_id = %(user_id)s", {'user_id': user_id})
  entities = []
  for result in cursor:
    entities.append(result[0])
  cursor.close()
  return entities

def get_waitlist_by_student_id(user_id):
  cursor = g.conn.execute("SELECT c FROM courses_uses_teaches c INNER JOIN waitlists w on c.course_id = w.course_id WHERE w.user_id = %(user_id)s", {'user_id': user_id})
  entities = []
  for result in cursor:
    entities.append(result[0])
  cursor.close()
  return entities

def get_course_by_instructor_id(user_id):
  cursor = g.conn.execute("SELECT * FROM courses_uses_teaches WHERE user_id = %(user_id)s", {'user_id': user_id})
  entities = []
  for result in cursor:
    entities.append(result)
  cursor.close()
  return entities

def get_review_by_course_id(course_id):
  cursor = g.conn.execute("SELECT * FROM reviews WHERE course_id = %(course_id)s", {'course_id': course_id})
  result = cursor.fetchone()
  cursor.close()
  if result is None:
    return None
  else:
    return Review(*result)

def get_review_by_user_id(user_id):
  cursor = g.conn.execute("SELECT * FROM reviews WHERE user_id = %(user_id)s", {'user_id': user_id})
  result = cursor.fetchone()
  cursor.close()
  if result is None:
    return None
  else:
    return Review(*result)

if __name__ == "__main__":
  app.secret_key = os.urandom(12)
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):

    HOST, PORT = host, port
    print(f"running on ${HOST}:${PORT}")
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
