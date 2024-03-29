import os
import json
import requests
from countryinfo import CountryInfo
from .config import register_conf
from .constants import (
    DEFAULT_CUSTOMER_EMAIL, DEFAULT_SELLER_EMAIL,
    DEFAULT_USER_IMG, DEFAULT_SELLER_IMG, DEFAULT_CUSTOMER_IMG
)
from flask.json import jsonify
from flask import Blueprint, flash, render_template, request, session, url_for, redirect
from flask_login import login_user, login_required, logout_user, LoginManager, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from ..products.models import Currency
from .forms import LoginForm
from .models import Customer, Seller
from ..extentions import db
from ..settings import UPLOAD_FOLDER
from ..utils import allowed_extension
from werkzeug.datastructures import ImmutableMultiDict


login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(id):
    if not session['role']:
        return Customer.query.get(int(id))
    if session['role'] > 0:
        return Seller.query.get(int(id))


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login_default', methods=(['GET']))
def login_default():
    print(session)
    if session.get('role', None) == 0:
        user = Seller.query.filter_by(email=DEFAULT_SELLER_EMAIL).first()
        img = DEFAULT_CUSTOMER_IMG
    else:
        user = Customer.query.filter_by(email=DEFAULT_CUSTOMER_EMAIL).first()
        img = DEFAULT_SELLER_IMG
    session['role'] = user.role
    session['default_user_img'] = img
    login_user(user)
    return redirect(url_for('main.home'))


def set_user_img(user, img, folder):
    if img and allowed_extension(img.filename):
        path = os.path.join(
            UPLOAD_FOLDER,
            f'img/user_inputs/{folder}/',
            secure_filename(img.filename)
        )
        img.save(path)
        user.img =  os.path.join(
            f'img/user_inputs/{folder}/',
            secure_filename(img.filename)
        )
    else:
        user.img = DEFAULT_USER_IMG


def register_seller(form):
    seller = Seller(
        company_name=form.company_name.data,
        email=form.email.data,
        password=generate_password_hash(form.pwd.data),
        role=1,
        )
    set_user_img(seller, form.img.data, 'seller_logo')
    return seller, 1


def register_customer(form):
    customer = Customer(
        username=form.username.data,
        email=form.email.data,
        password=generate_password_hash(form.pwd.data),
        role=0
    )
    set_user_img(customer, form.img.data, 'customer_avatar')
    return customer, 0


def create_user(user, form):
    if user == 'customer':
        return register_customer(form)
    else:
        return register_seller(form)


@bp.route('/register/<user>', methods=(['GET', 'POST']))
def register(user):
    if not session.get('country', False):
        ip = request.headers.get('X-Forwarded-For', False)
        if ip:
            URL = f'https://ipapi.co/{ip}/json'
            res = requests.get(URL)
            session['country'] = json.loads(res.text)['country_name']
        else:
            session['country'] = 'Georgia'

    session['currency'] = CountryInfo(session['country']).currencies()[0]

    if request.method == "POST":
        data = ImmutableMultiDict(request.form)
        form_data = data.to_dict(flat=True)
        form = register_conf[user](**form_data)
        if form.validate_on_submit():
            try:
                user, role = create_user(user, form)
                db.session.add(user)
                db.session.commit()
                session['role'] = role
                login_user(user)
                return url_for('main.home')
            except Exception as _ex:
                flash(_ex, 'danger')
                print(_ex)
        else:
            valid_field = set(set(form_data.keys())).difference(form.errors.keys())
            data = form.errors
            data.update(dict.fromkeys(valid_field, ''))
            return jsonify(data)
    else:
        form = register_conf[user]()
    return render_template('auth/register.html', form=form, title='', user=user)


@login_required
@bp.route('/profile', methods=('GET', ))
def profile():
    if current_user.role:
        return render_template('auth/profile_seller.html', user=current_user)
    return render_template('auth/profile_customer.html', user=current_user)


@login_required
@bp.route('/edit_customer_profile', methods=('GET', 'POST', 'PUT'))
def edit_customer_profile():
    if request.method == 'POST':
        user = Customer.query.get(current_user.id)
        user.username = request.form.get('username')

        email = request.form.get('email')
        if not Seller.query.filter_by(email=email).first() and \
            not Customer.query.filter_by(email=email).first() and \
                user.email != email:
            user.email = request.form.get('email')
        elif user.email == email:
            user.email = request.form.get('email')
        else:
            flash('This email already taken')
            return redirect(url_for('auth.edit_seller_profile'))

        avatar = request.files['avatar']
        if avatar and avatar != user.avatar:
            if avatar and allowed_extension(avatar.filename):
                path = os.path.join(UPLOAD_FOLDER, 'img/user_inputs/customer_avatar/', secure_filename(avatar.filename))
                avatar.save(os.path.join(path))
                user.avatar = os.path.join('img/user_inputs/customer_avatar/', secure_filename(avatar.filename))
        current_pwd = request.form.get('password')
        if current_pwd:
            if check_password_hash(user.password, current_pwd):
                new_password = request.form.get('new_password')
                repeat_password = request.form.get('repeat_password')
                if new_password == repeat_password:
                    if len(new_password) >= 8:
                        user.password = generate_password_hash(new_password)
                    else:
                        flash(f'Password should contain more then 8 letters')
                        return redirect(url_for('auth.edit_seller_profile'))
                else:
                    flash('Password mismutch')
                    return redirect(url_for('auth.edit_seller_profile'))
            else:
                flash(f'Current password is incorrect')
                return redirect(url_for('auth.edit_seller_profile'))

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.profile'))
    return render_template('auth/edit_customer_profile.html', user=current_user)


@login_required
@bp.route('/edit_seller_profile', methods=('GET', 'POST'))
def edit_seller_profile():

    user = current_user
    data = {
        'user': current_user,
    }
    if request.method == 'POST':
        user.company_name = request.form.get('company_name')
        email = request.form.get('email')
        if not Seller.query.filter_by(email=email).first() and \
            not Customer.query.filter_by(email=email).first() and \
                user.email != email:
            user.email = request.form.get('email')
        elif user.email == email:
            user.email = request.form.get('email')
        else:
            flash('This email already taken')
            return redirect(url_for('auth.edit_seller_profile'))

        logo = request.files['logo']
        if logo and logo != user.logo:
            if logo and allowed_extension(logo.filename):
                path = os.path.join(UPLOAD_FOLDER, 'img/user_inputs/customer_avatar/', secure_filename(logo.filename))
                logo.save(os.path.join(path))
                user.logo = os.path.join('img/user_inputs/customer_avatar/', secure_filename(logo.filename))

        current_pwd = request.form.get('password')
        if current_pwd:
            if check_password_hash(user.password, current_pwd):
                new_password = request.form.get('new_password')
                repeat_password = request.form.get('repeat_password')
                if new_password == repeat_password:
                    if len(new_password) >= 8:
                        user.password = generate_password_hash(new_password)
                    else:
                        flash(f'Password should contain more then 8 letters')
                        return redirect(url_for('auth.edit_seller_profile'))
                else:
                    flash('Password mismatch')
                    return redirect(url_for('auth.edit_seller_profile'))
            else:
                flash(f'Current password is incorrect')
                return redirect(url_for('auth.edit_seller_profile'))

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.profile'))
    return render_template('auth/edit_seller_profile.html', **data)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    # return redirect(url_for('main.home'))
    if request.method == "POST":
        data = ImmutableMultiDict(request.form)
        form_data = data.to_dict(flat=True)
        form = LoginForm(**form_data)
        if form.validate_on_submit():
            try:
                login_user(form.user)
                session['role'] = form.user.role
                return url_for('main.home')
            except Exception as _ex:
                print(_ex)
                flash(f"User with such email or password doesn't exist", 'danger')
        valid_field = set(set(form_data.keys())).difference(form.errors.keys())
        data = form.errors
        data.update(dict.fromkeys(valid_field, ''))
        return jsonify(data)
    else:
        form = LoginForm()
    return render_template('auth/register.html', form=form, title='Login')


@bp.route('/logout', methods=('GET', ))
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.home'))


@bp.route('/delete_user', methods=['GET'])
def delete_user():
    user = load_user(current_user.id)
    if user.img != DEFAULT_USER_IMG:
        path = os.path.join(UPLOAD_FOLDER, user.img)
        os.remove(path)
    user.delete()
    return redirect(url_for('main.home'))


# @login_required
# @bp.route('/change_currency', methods=['POST'])
# def change_currency():
#     currency = request.form.get('currency')
#     current_user.display_currency_id = Currency.query.filter_by(abr=currency)[0].id
#     db.session.add(current_user)
#     db.session.commit()
#     return ('', 204)

@bp.route('/createsupeuser', methods=['POST'])
def create_superuser(id):
    load_user(id)
    return ('', 204)
