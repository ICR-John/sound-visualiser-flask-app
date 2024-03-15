""" Create the classes for database interaction """
""" Created by Saeeda Doolan. Isaiah John, Ahmed Mohamud """


import sqlite3
from datetime import datetime
from pathlib import Path
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from my_app import db, photos

DATA_PATH = Path(__file__).parent.parent.joinpath("data")


"""*********************
    User Tables
*********************"""

class User(UserMixin, db.Model):
    """ Class inspired by the lecture notes for COMP0034 """

    conn = sqlite3.connect(str(DATA_PATH.joinpath('example.sqlite')))
    cursor = conn.cursor()
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow())
    profiles = db.relationship('Profile', backref='user', lazy=True)

    def __init__(self, email, firstname, lastname):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.conn = sqlite3.connect(str(DATA_PATH.joinpath('example.sqlite')))
        self.cursor = self.conn.cursor()

    @staticmethod
    def find_all_users():
        """Return all users"""
        User.cursor.execute("SELECT * FROM User")
        result = User.cursor.fetchall()
        for row in result:
            print(row)

    @staticmethod
    def find_by_id(user_id):
        """Return the data for a specific user id"""
        result = User.cursor.execute(
            "SELECT * FROM User WHERE id = ?", (user_id,))
        for row in iter(User.cursor.fetchone, None):
            print(row)

    @staticmethod
    def find_and_delete(user_id):
        """Delete data of a specific user id"""
        mysql = User.cursor.execute(
            "DELETE FROM User WHERE id = ?", (user_id,))
        User.conn.commit()
        print(User.cursor.rowcount, "record(s) deleted")

    def update(self, email, password):
        """Update description or recording for a row in users"""
        updateData = self.cursor.execute("UPDATE User SET firstname = ?, lastname = ?, email = ?, "
                                         "password = ? "
                                         "WHERE id = ?",
                                         (email, password, self.id))
        self.conn.commit()
        result = self.cursor.execute(
            "SELECT * FROM User WHERE id = ?", (self.id,))
        for row in iter(self.cursor.fetchone, None):
            print(row)
        print("rows updated")

    def save(self):
        """Insert a new row in users"""
        mysqlData = self.cursor.execute(
            "INSERT INTO User  VALUES (?,?, ?, ?, ?,?)", (self.id, self.firstname,
                                                          self.lastname, self.email,
                                                          self.password, self.create_time
                                                          ))
        self.conn.commit()
        result = User.cursor.execute(
            "SELECT * FROM User WHERE id = ?", (self.id,))
        for row in iter(self.cursor.fetchone, None):
            print(row)
        print(self.cursor.rowcount, "records inserted")

    def __repr__(self):
        return f"{self.id} {self.firstname} {self.lastname} {self.email} {self.password}"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Profile(db.Model):
    """ Created by Saeeda Doolan and Isaiah John """

    __tablename__ = "Profile"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    photo = db.Column(db.Text)
    bio = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    topic_count = db.Column(db.Integer, default=0, nullable=False)
    post_count = db.Column(db.Integer, default=0, nullable=False)

    # One-to-Many
    topics = db.relationship("Topic", backref="profile", lazy=True)

    # One-to-Many
    posts = db.relationship("Post", backref="profile", lazy=True)

    # Properties

    @property
    def url(self):
        """Returs the URL associated with the profile"""
        return url_for('profile.display_profiles', username=self.username)

    @property
    def photo_url(self):
        """Returns the URL associated with the profile photo"""
        if self.photo:
            return photos.url(self.photo)
        return None

    def __repr__(self):
        return f"{self.id} {self.username} {self.topic_count} {self.post_count}"

    def __str__(self):
        return f"Username: {self.username}"

    # Methods

    @classmethod
    def get_profile(cls, user_id):
        """Returns the profile based on the user ID"""
        if user_id is not None:
            return Profile.query.join(User).filter(User.id == user_id).first()
        return None


"""*********************
    Forum Models
*********************"""


class Topic(db.Model):
    """ Created by Isaiah John """

    __tablename__ = "Topic"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey("Profile.id"))

    date_created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    post_count = db.Column(db.Integer, default=0, nullable=False)

    # One-to-Many
    posts = db.relationship("Post", backref="topic", lazy=True)

    # Properties

    @property
    def url(self):
        """Returns the URL associated with a topic"""
        return url_for("forum.view_topic", topic_id=self.id)

    # Methods

    def __init__(self, title=None, profile=None, content=None, photo=None):
        """Creates a new topic"""
        if title:
            self.title = title
        if profile:
            self.profile_id = profile.id
        if content or photo:
            self._post = Post(topic=self, content=content, photo=photo)
        self.date_created = datetime.now()

    def __repr__(self):
        return f"{self.id} {self.title} {self.profile_id} {self.date_created} {self.posts}"

    @classmethod
    def get_topic(cls, topic_id):
        """Returns topic based on id"""
        return Topic.query.get(topic_id)

    def recalculate(self):
        """Recalculates the number of posts for a topic"""
        post_count = Post.query.filter_by(topic_id=self.id).count
        self.post_count = post_count

    def save(self, profile=None):
        """Saves topic to the database"""
        if profile is None:
            profile = Profile.query.get(self.profile_id)

        profile.topic_count += 1

        db.session.add(profile)
        db.session.add(self)

        db.session.commit()

        self._post.save(topic=self, profile=profile)

        return self


class Post(db.Model):
    """ Created by Isaiah John """

    __tablename__ = "Post"
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("Topic.id"))
    profile_id = db.Column(db.Integer, db.ForeignKey("Profile.id"))

    date_created = db.Column(db.DateTime, default=datetime.now())
    content = db.Column(db.Text, nullable=False)
    photo = db.Column(db.Text)

    # Properties

    @property
    def url(self):
        """ The URL associated with the post"""
        return url_for("forum.view_post", post_id=self.id)

    @property
    def photo_url(self):
        """ The URL of the associated photo"""
        if self.photo:
            return photos.url(self.photo)
        return None

    # Methods

    def __init__(self, topic=None, profile=None, content=None, photo=None):
        """Creates a new post"""
        if topic:
            self.topic_id = topic.id
        if profile:
            self.profile_id = profile.id
        if content:
            self.content = content
        if photo:
            self.photo = photo
        self.date_created = datetime.now()

    def __repr__(self):
        return f"{self.id} {self.topic_id} {self.profile_id} {self.date_created} {self.content}"

    def save(self, profile=None, topic=None):
        """ Saves post to database """
        # New posts will provide the profile and topic separately
        if profile and topic:
            self.profile_id = profile.id

            self.topic_id = topic.id
            self.date_created = datetime.now()

            # Update the post counts
            profile.post_count += 1
            topic.post_count += 1

            db.session.add(profile)
            db.session.add(topic)

        db.session.add(self)
        db.session.commit()

        return self


"""*********************
    Instrument Models
*********************"""


class Instruments(db.Model):
    """ Created by Ahmed Mohamud """
    conn = sqlite3.connect(str(DATA_PATH.joinpath('example.sqlite')))
    cursor = conn.cursor()

    __tablename__ = "Instruments"
    instrument_id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.BLOB)
    name = db.Column(db.VARCHAR(45), nullable=False)
    family = db.Column(db.Text, nullable=False)

    # One-to-many
    sounds = db.relationship('Sounds', backref="instrument", lazy=True)

    # Methods

    def ___repr__(self):
        return f"{self.instrument_id} {self.name} {self.image}"

    @staticmethod
    def find_all_instruments():
        """Return all instruments"""
        Instruments.cursor.execute("SELECT * FROM Instruments")
        result = Instruments.cursor.fetchall()
        for row in result:
            print(row)

    @staticmethod
    def find_by_id(instrument_id):
        """Return the data for a specific instrument id"""
        result = Instruments.cursor.execute(
            "SELECT * FROM Instruments WHERE instrument_id = ?", (instrument_id,))
        for row in iter(Instruments.cursor.fetchone, None):
            print(row)

    @staticmethod
    def find_and_delete(instrument_id):
        """Delete data or a specific instrument id"""
        mysql = Instruments.cursor.execute(
            "DELETE FROM Instruments WHERE instrument_id = ?", (instrument_id,))
        Instruments.conn.commit()
        print(Instruments.cursor.rowcount, "record(s) deleted")

    def update(self, instrument_name, instrument_image):
        """Update description or recording for a row in instruments"""
        updateData = self.cursor.execute("UPDATE Instruments SET name = ?, "
                                         "image = ? "
                                         "WHERE instrument_id = ?",
                                         (instrument_name, instrument_image, self.instrument_id))
        self.conn.commit()
        result = self.cursor.execute(
            "SELECT * FROM Instruments WHERE instrument_id = ?", (self.instrument_id,))
        for row in iter(self.cursor.fetchone, None):
            print(row)
        print("rows updated")

    def save(self):
        """Insert a new row in instruments"""
        mysqlData = self.cursor.execute(
            "INSERT INTO Instruments VALUES (?, ?, ?)", (self.instrument_id,
                                                         self.name,
                                                         self.image))
        self.conn.commit()
        result = Instruments.cursor.execute(
            "SELECT * FROM Instruments WHERE instrument_id = ?", (self.instrument_id,))
        for row in iter(self.cursor.fetchone, None):
            print(row)
        print(self.cursor.rowcount, "records inserted")


class Sounds(db.Model):
    """ Created by Ahmed Mohamud """

    __tablename__ = "Sounds"
    sound_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(45))
    recording = db.Column(db.VARCHAR(200))
    instrument_id = db.Column(db.Integer, db.ForeignKey('Instruments.instrument_id'))
    note = db.Column(db.VARCHAR(5))

    note = db.Column(db.Text)

    # Methods

    def __repr__(self):
        return f"{self.sound_id} {self.name} {self.recording}"

    @classmethod
    def find_sound(cls, instrument_id, note):
        return Sounds.query.filter(Sounds.instrument_id == instrument_id,
                                   Sounds.name.contains(note)).first()

    @staticmethod
    def find_all_sounds():
        """Return all sounds"""
        Sounds.cursor.execute("SELECT * FROM Sounds")
        myresult = Sounds.cursor.fetchall()
        for row in myresult:
            print(row)

    @staticmethod
    def find_by_id(sound_id):
        """Return the data for a specific sound id"""
        result = Sounds.cursor.execute(
            "SELECT * FROM Sounds WHERE sound_id = ?", (sound_id,))
        for row in iter(Sounds.cursor.fetchone, None):
            print(row)

    @staticmethod
    def find_by_instrument_id(instrument_id):
        """Return all table entries for a given instrument"""
        result = Sounds.cursor.execute(
            "SELECT * FROM Sounds WHERE instrument_id = ?", (instrument_id,))
        return result

    @staticmethod
    def find_and_delete(sound_id):
        """Delete data or a specific sound id"""
        mysql = Sounds.cursor.execute(
            "DELETE FROM Sounds WHERE sound_id = ?", (sound_id,))
        Sounds.conn.commit()
        print(Sounds.cursor.rowcount, "record(s) deleted")

    def update(self, recording, sound_name):
        """Update description or recording for a row in sounds"""
        updateData = self.cursor.execute("UPDATE Sounds SET name = ?, recording = ? WHERE sound_id = ?",
                                         (sound_name, recording, self.sound_id))
        self.conn.commit()
        result = self.cursor.execute(
            "SELECT * FROM Sounds WHERE sound_id = ?", (self.sound_id,))
        for row in iter(self.cursor.fetchone, None):
            print(row)
        print("rows updated")

    def save(self):
        """Insert a new row in sounds"""
        mysqlData = self.cursor.execute(
            "INSERT INTO Sounds  VALUES (?, ?, ?, ?)", (self.sound_id,
                                                        self.name,
                                                        self.recording,
                                                        self.instrument_id))
        self.conn.commit()
        result = Sounds.cursor.execute(
            "SELECT * FROM Sounds WHERE sound_id = ?", (self.sound_id,))
        for row in iter(self.cursor.fetchone, None):
            print(row)
        print(self.cursor.rowcount, "records inserted")



