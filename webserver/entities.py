class Course:
  def __init__(self, course_id, name, term, description, schedule, is_open, is_over, room_id, user_id):
    self.course_id = course_id
    self.name = name
    self.term = term
    self.description = description
    self.schedule = schedule
    self.is_open = is_open
    self.is_over = is_over
    self.room_id = room_id
    self.user_id = user_id

class Enroll:
  def __init__(self, course_id, user_id):
    self.course_id = course_id
    self.user_id = user_id

class Review:
  def __init__(self, does_recommend, content, user_id, course_id):
    self.does_recommend = does_recommend
    self.content = content
    self.user_id = user_id
    self.course_id = course_id

class Room:
  def __init__(self, room_id, location):
    self.room_id = room_id
    self.location = location

class User:
  def __init__(self, user_id, hash, name, birthdate, is_admin, class_year, major, concentration, department, title, is_student = None, is_instructor = None):
    self.user_id = user_id
    self.hash = hash
    self.name = name
    self.birthdate = birthdate
    self.is_admin = is_admin
    self.class_year = class_year
    self.major = major
    self.concentration = concentration
    self.department = department
    self.title = title
    if is_student is None:
      if self.is_admin:
        self.is_student = False
        self.is_instructor = False
      elif self.class_year is not None:
        self. is_student = True
        self.is_instructor = False
      else:
        self. is_student = False
        self.is_instructor = True
    else:
      self.is_student = is_student
      self.is_instructor = is_instructor

class Waitlist:
  def __init__(self, course_id, user_id):
    self.course_id = course_id
    self.user_id = user_id
