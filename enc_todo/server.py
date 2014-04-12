from flask import Flask
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
import json
import calendar, datetime
from sqlalchemy.orm import class_mapper

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:angadsingh@localhost/enc_todo'
db = SQLAlchemy(app)


class Task(db.Model):
  __tablename__ = 'tasks'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
  task = db.Column(db.String(65535))
  task_status = db.Column(db.Integer)
  created_timestamp = db.Column(db.DateTime)


class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  pubkey = db.Column(db.String(65535))
  created_timestamp = db.Column(db.DateTime)


@app.route("/register", methods=['POST'])
def register():
  pubkey = request.form['pubkey']
  try:
    u = User(pubkey=pubkey)
    db.session.add(u)
    db.session.commit()
  except:
    # already exists
    pass
  return ""


@app.route("/new", methods=['POST'])
def new():
  pubkey = request.form['pubkey']
  u = User.query.filter_by(pubkey=pubkey).first()
  if u:
    user_id = u.id
  else:
    return "", 404
  task = request.form['task']
  t = Task(user_id=int(user_id), task=task, task_status=1)
  db.session.add(t)
  db.session.commit()
  return ""


@app.route("/list", methods=['POST'])
def list_tasks():
  pubkey = request.form['pubkey']
  u = User.query.filter_by(pubkey=pubkey).first()
  if u:
    user_id = u.id
  else:
    return "", 404
  res = [serialize(task) for task in Task.query.filter_by(user_id=user_id).all()]
  return json.dumps(res, default=default)


def serialize(model):
  """Transforms a model into a dictionary which can be dumped to JSON."""
  # first we get the names of all the columns on your model
  columns = [c.key for c in class_mapper(model.__class__).columns]
  # then we return their values in a dict
  return dict((c, getattr(model, c)) for c in columns)

def default(obj):
  """Default JSON serializer."""
  if isinstance(obj, datetime.datetime):
      if obj.utcoffset() is not None:
          obj = obj - obj.utcoffset()
  millis = int(
      calendar.timegm(obj.timetuple()) * 1000 +
      obj.microsecond / 1000
  )
  return millis

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5005)
