""" Handles all of the routing for the forum.
    Created by Isaiah John """

from sqlite3 import IntegrityError

from flask import Blueprint, url_for, render_template, flash, redirect, request
from flask_login import login_required, current_user

from my_app import db, photos
from my_app.forum.forms import NewTopicForm, ReplyPostForm
from my_app.models import Topic, Profile, Post

forum_bp = Blueprint('forum', __name__, url_prefix='/forum')


@forum_bp.route('/')
@login_required
def index():
    """ Provides the home page for the forum """
    topics = Topic.query.order_by(Topic.date_created.desc())
    return render_template('forum.html', title="Forum page", topics=topics)


@forum_bp.route('/search', methods=['GET', 'POST'], defaults={'term': None})
@forum_bp.route('/search=<term>', methods=['GET', 'POST'])
@login_required
def search_topics(term):
    """ Allows the user to search topics by their title """
    # Inspired by code from FlaskBB
    # Reference: https://flaskbb.readthedocs.io/en/latest/

    if term is None:
        # Checks if the user entered a term into the search bar
        if request.method == 'POST':
            term = request.form['search_term']
            # Redirects them to this page with the term properly set
            if term != "":
                return redirect(url_for("forum.search_topics", term=term))
        flash("Enter a topic to search for")
        # Redirects them to the home page
        return redirect(url_for("forum.index"))

    # Searches the topic table for items that contain the term in the title
    results = Topic.query.filter(Topic.title.contains(term)).all()
    return render_template('forum.html', title="Search Results", topics=results)


@forum_bp.route('/new-topic', methods=['GET', 'POST'])
@login_required
def new_topic():
    """ Allows user to start a new forum discussion """
    # Inspired by code from FlaskBB
    # Reference: https://flaskbb.readthedocs.io/en/latest/

    # Obtains the profile for the current user
    profile = Profile.get_profile(current_user.id)
    # Redirects to the profile creation if they do not yet have one
    if profile is None:
        flash(f"You need to update your profile before you can use forum")
        return redirect(url_for('profile.create_profile'))

    # Creates a new form to hold the topic
    form = NewTopicForm()
    if form.validate_on_submit():
        # Defaults to no file uploaded
        filename = None
        if 'photo' in request.files:
            if request.files['photo'].filename != '':
                filename = photos.save(request.files['photo'])
        # Creates the topic using the form data
        topic = Topic(title=form.title.data, profile=profile,
                      content=form.content.data, photo=filename)

        # Attempts to save the topic to the database, and does rollback if it cannot
        try:
            topic.save()
            flash(f"Your Topic has been posted to the forum")
        except IntegrityError:
            db.session.rollback()
            flash(f"Error, unable to post topic")
            return redirect(url_for('forum.new_topic'))

        # Sends the user to the forum homepage once completed
        return redirect(url_for('forum.index'))

    return render_template('new_topic.html', title='New Topic', form=form)


@forum_bp.route('/topic/<topic_id>', methods=['GET', 'POST'])
@login_required
def view_topic(topic_id):
    """ Allows the user to view the posts associated with a topic """
    # Inspired by code from FlaskBB
    # Reference: https://flaskbb.readthedocs.io/en/latest/

    # Obtains the profile for the current user
    profile = Profile.get_profile(current_user.id)
    # Redirects to the profile creation if they do not yet have one
    if profile is None:
        flash(f"You need to update your profile before you can use forum")
        return redirect(url_for('profile.create_profile'))

    # Obtains the topic for use in the HTML
    topic = Topic.get_topic(topic_id)
    # Obtains all posts associated with the topic
    posts = Post.query.filter_by(topic_id=topic_id).order_by(Post.date_created)

    # Creates a new form to hold replies
    form = ReplyPostForm()

    if form.validate_on_submit():
        # Defaults to no file uploaded
        filename = None
        if 'photo' in request.files:
            if request.files['photo'].filename != '':
                filename = photos.save(request.files['photo'])

        # Adds form data to a post
        post = Post(content=form.content.data, photo=filename)
        try:
            post.save(topic=topic, profile=profile)
            flash("Your reply has successfully been posted")
            # Redirects user to clear the form, so that it would not resubmit on reload
            return redirect(url_for("forum.view_post", post_id=post.id))
        except IntegrityError:
            db.session.rollback()
            flash("Could not save reply")

    return render_template('topic.html', topic=topic, posts=posts, form=form)


@forum_bp.route("/topic/post=<post_id>")
@login_required
def view_post(post_id):
    """ Redirects user to the topic that contains a specific post """
    post = Post.query.get(post_id)
    return redirect(url_for("forum.view_topic", topic_id=post.topic_id))
