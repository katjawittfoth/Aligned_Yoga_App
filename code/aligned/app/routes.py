from app import application, classes, db

# FLASK & WEB
from flask import flash, render_template, redirect, url_for, Response, request
from flask_login import current_user, login_user, login_required, logout_user

# UPLOADING & FILE PROCESSING
from werkzeug import secure_filename
import os
import time
import ffmpy

# APP CODE
from process_openpose_user import *
from modeling import *
from process_label import ProcessLabel


@application.route('/index')
@application.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('poses'))
    else:
        return render_template('index.html')


@application.route('/register', methods=('GET', 'POST'))
def register():
    registration_form = classes.RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        password = registration_form.password.data
        email = registration_form.email.data

        user_count = classes.User.query.filter_by(username=username).count() \
            + classes.User.query.filter_by(email=email).count()
        if user_count > 0:
            flash('Error - Existing user : ' + username + ' OR ' + email)

        else:
            user = classes.User(username, email, password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', form=registration_form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('poses'))

    login_form = classes.LogInForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        # Look for it in the database.
        user = classes.User.query.filter_by(username=username).first()

        # Login and validate the user.
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for('poses'))
        else:
            flash('Invalid username and password combination!')
    return render_template('login.html', form=login_form)


@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@application.route('/poses', methods=['GET'])
@login_required
def poses():
    return render_template('poses.html')


@application.route('/poses/<pose_id>', methods=['GET'])
@login_required
def pose(pose_id):
    # select * from poses where id = pose_id
    pose_name = "Warrior II"
    pose_desc = "Good choice. Warrior II is a great pose to open your hips," \
        + " chest, and shoulders while strengthening your leg and abdomen."
    return render_template('pose.html',
                           pose_name=pose_name,
                           pose_desc=pose_desc)


@application.route('/video', methods=['POST'])
def video():
    if request.method == 'POST':
        file = request.files['file']

        filename = secure_filename(file.filename)
        print(type(file))
        file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
        print(filename, application.config['UPLOAD_FOLDER'])
        timestr = time.strftime("%Y%m%d-%H%M%S")
        local_path = f"/tmp/user_video_{timestr}.avi"

        ff = ffmpy.FFmpeg(inputs={os.path.join(
                                  application.config['UPLOAD_FOLDER'],
                                  filename): None},
                          outputs={local_path: '-q:v 0 -vcodec mjpeg -r 30'})
        ff.run()
        timestr = time.strftime("%Y%m%d-%H%M%S")
        # filepath = push2s3(name, '') #filename without tmp

        # Process video with openpose on same server & return df
        df = process_openpose(local_path)
        # pull csv from s3, run through rules-based system
        labels, values = warrior2_label_csv(df)
        # user = load_user(uid)
        # user.labels = labels
        comma_separated = ','.join([str(int(c)) for c in labels])
        print(comma_separated)
        return url_for('feedback', labels_str=comma_separated)
    # return render_template('video.html')

# @application.route('/audio')
# def done_audio():
#     return send_file('done.m4a',
#                      mimetype="audio/m4a",
#                      as_atachment=True,
#                      attachment_filename='done.m4a')


@application.route('/feedback/<labels_str>', methods=['GET'])
@login_required
def feedback(labels_str):
    labels = list(labels_str.split(','))
    labels = [int(float(c)) for c in labels]
    pose_name = "Warrior II"
    # feedback = ProcessLabel.to_text([1, 1, 1, 1, 0, 0, 0, 0, 0])
    feedback_text = ProcessLabel.to_text(labels)
    return render_template('feedback.html',
                           feedback=feedback_text, pose_name=pose_name)
