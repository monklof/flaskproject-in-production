#coding=utf-8
"""authentication logic
"""
from sqlalchemy.orm.exc import NoResultFound
from flask import request, flash, render_template, redirect, url_for, Blueprint
import flask.ext.login as flask_login
from model import db_session, User

login_manager = flask_login.LoginManager()

auth = Blueprint('auth', __name__)
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    with db_session() as session:
        try:
            user = session.query(User).filter_by(
                email = request.form['email'],
                pwd = request.form['pwd']).one()
        except NoResultFound:
            flash('validate not passed!')
            return render_template("login.html")
    flask_login.login_user(user)
    return redirect(request.args.get('next') or url_for('index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if not request.form['email']:
        flash('email not set properly!')
        return render_template('register.html')
    if not request.form['pwd']:
        flash('pwd not set properly!')
        return render_template('register.html')
    if not request.form['nickname']:
        flash('nickname not set properly')
        return render_template('register.html')
    with db_session() as session:
        if session.query(User).filter_by(email=request.form['email']).count():
            flash('user %s already exists, please use another email' % request.form['email'])
            return render_template('register.html')
        user = User(email=request.form['email'], pwd=request.form['pwd'], nickname=request.form['nickname'])
        session.add(user)
        session.commit()
        flask_login.login_user(user)

        return redirect(request.args.get('next') or url_for('index'))

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))

@login_manager.user_loader
def user_loader(email):
    with db_session() as session:
        return session.query(User).filter_by(email=email).one()

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('auth.login', next=request.url))



