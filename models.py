from flask_sqlalchemy import SQLAlchemy
from flask import current_app


class User(SQLAlchemy.Model):
    id = SQLAlchemy.Column(SQLAlchemy.Integer, primary_key=True)
    first_name = SQLAlchemy.Column(SQLAlchemy.String(100))
    last_name = SQLAlchemy.Column(SQLAlchemy.String(100))
    login = SQLAlchemy.Column(SQLAlchemy.String(80), unique=True)
    email = SQLAlchemy.Column(SQLAlchemy.String(120))
    password = SQLAlchemy.Column(SQLAlchemy.String(64))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username



def build_init_db(db):
  try:
    db.drop_all()
    db.create_all()
  except Exception as e:
    current_app.logger.exception(e)
  return