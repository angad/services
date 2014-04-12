from flask import Flask
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
import json
import calendar, datetime
from sqlalchemy.orm import class_mapper

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/enc_todo'
db = SQLAlchemy(app)

""" 
CREATE TABLE IF NOT EXISTS `tasks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `task` mediumtext NOT NULL,
  `task_status` int(11) NOT NULL,
  `created_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pubkey` text NOT NULL,
  `created_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pubkey` (`pubkey`(255))
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;
"""


class Task(db.Model):
  """ Task model"""
  __tablename__ = 'tasks'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
  task = db.Column(db.String(65535))
  task_status = db.Column(db.Integer)
  created_timestamp = db.Column(db.DateTime)


class User(db.Model):
  """ User model """
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  pubkey = db.Column(db.String(65535))
  created_timestamp = db.Column(db.DateTime)


@app.route("/register", methods=['POST'])
def register():
  """ register a new user with public key """
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
  """ create a new task """
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
  """ list all tasks
  returns a json of all tasks
  """
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
  columns = [c.key for c in class_mapper(model.__class__).columns]
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
