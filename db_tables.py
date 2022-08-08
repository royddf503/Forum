from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)  # Standard start
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'

db = SQLAlchemy(app)


class User(db.Model):
    """
    Represents User db
    """
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(10), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    date_birth = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(20))
    gender = db.Column(db.String(1), nullable=False)
    posts = db.relationship('BlogPost', backref='user')

    def __repr__(self):
        return 'User ' + str(self.id)


class BlogPost(db.Model):
    """
    Represents blog post db
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    likes = db.relationship('Like', backref='blogpost')

    def __repr__(self):
        return 'Blog post ' + str(self.id)


class Like(db.Model):
    """
    Represents Like db
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(BlogPost.id), nullable=False)

    def __repr__(self):
        return 'Like ' + str(self.id)
