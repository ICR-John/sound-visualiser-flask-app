"""Created by Saeeda Doolan"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from my_app import photos, db
from my_app.profile.forms import ProfileForm
from my_app.models import Profile, User, Post, Topic

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/')
@login_required
def index():
    return render_template('community.html', title="Menu")


@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Check if the profile is created and redirect to profile or profile form
    """
    profile = Profile.get_profile(current_user.id)
    if profile:
        return redirect(url_for('profile.display_profiles', username=profile.username))
    else:
        return redirect(url_for('profile.create_profile'))


@profile_bp.route('/create_profile', methods=['GET', 'POST'])
@login_required
def create_profile():
    pro_form = ProfileForm()
    if request.method == 'POST' and pro_form.validate_on_submit():
        # Set the filename for the photo to a default image.
        filename = 'default.png'
        # Check if the form contains a photo
        if 'photo' in request.files:
            # If filename isn't empty then save the photo
            if request.files['photo'].filename != '':
                filename = photos.save(request.files['photo'])
        # Creating a profile from the form fields
        pro = Profile(username=pro_form.username.data, photo=filename, bio=pro_form.bio.data,
                      user_id=current_user.id)
        # Add to database
        db.session.add(pro)  
        # Save to database
        db.session.commit() 
        return redirect(url_for('profile.display_profiles', username=pro.username))
    return render_template('profile.html', form=pro_form)


@profile_bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    # Query database to find user id
    session_user = Profile.query.join(User).filter_by(id=current_user.id).first()
    form = ProfileForm(obj=profile)
    if request.method == 'POST' and form.validate_on_submit():
        if 'photo' in request.files:
            if request.files['photo'].filename != '':
                filename = photos.save(request.files['photo'])
                profile.photo = filename
            else:
                filename = 'default.png'  # Add default image if user does not update the image
                session_user.photo = filename
        session_user.bio = form.bio.data
        session_user.username = form.username.data
        pro = Profile(username=form.username.data, photo=filename, bio=form.bio.data,
                      user_id=current_user.id)  # Create Profile using data submitted on form
        db.session.commit()
        return redirect(url_for('profile.display_profiles', username=pro.username))
    return render_template('profile.html', form=form)


@profile_bp.route('/display_profiles', methods=['POST', 'GET'], defaults={'username': None})
@profile_bp.route('/display_profiles/<username>/', methods=['POST', 'GET'])
@login_required
def display_profiles(username):
    users_found = None
    posts = None
    posts_count = None
    topic_count = None
    # Find the profile for the username in the search bar
    if username is None:
        if request.method == 'POST':
            term = request.form['search_term']
            if term == "":
                flash("Enter a name to search for")
                return redirect(url_for("profile.index"))
            users_found = Profile.query.filter(Profile.username.contains(term)).all()
    else:
        users_found = Profile.query.filter_by(username=username).all()
    if not users_found:
        flash("Username does not exist")
        return redirect(url_for("profile.index"))
    urls = []
    for user in users_found:
        if user.photo:
            url = photos.url(user.photo)
            urls.append(url)
        # Find the posts for the session user
        posts = Post.query.filter_by(profile_id=user.id).order_by(Post.date_created.desc()).limit(3)
        # Find total number of posts by session user
        posts_count = db.session.query(Post).filter_by(profile_id=user.id).count()
        # Find total number of discussions started by session user
        topic_count = db.session.query(Topic).filter_by(profile_id=user.id).count()

    return render_template('display_profile.html', profiles=zip(users_found, urls),
                           posts=posts, posts_count=posts_count, topic_count=topic_count)
