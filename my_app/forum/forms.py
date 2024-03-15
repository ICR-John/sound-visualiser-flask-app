""" Stores all the forms used by the forum
    Created by Isaiah John """


from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, Optional
from my_app import photos


class PostForm(FlaskForm):
    """ Generic Form used as a template for post """
    content = TextAreaField(label="Post Content", validators=[DataRequired()])

    photo = FileField(label='Optional Picture',
                      validators=[Optional(strip_whitespace=True), FileAllowed(photos, 'Images only')])

    submit = SubmitField(label="Submit post")


class ReplyPostForm(PostForm):
    """ Reply Form for use within a topic to hold a post """
    submit = SubmitField(label="Reply")


class TopicForm(PostForm):
    """ Generic Form used as a template to store a topic """
    title = StringField(label="Title", validators=[DataRequired()])
    submit = SubmitField(label="Post topic")


class NewTopicForm(TopicForm):
    """ Form used to hold a new topic. Same as TopicForm"""
    pass


