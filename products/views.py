import os
from .models import Product
from flask import Blueprint, flash, render_template, redirect, session, url_for, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from ..extentions import db
from ..settings import UPLOAD_FOLDER
from ..utils import allowed_extension
from ..products.forms import CreateProductForm
from ..products.models import Product, ProductCategory, ProductImage, Card, Order


pr = Blueprint('', __name__, url_prefix='/')

@pr.route('/api/health', methods=['GET', 'POST', 'PUT'])
def az_webhook():
    return ('', 200)


@pr.route('/product/<id>', methods=['GET', 'POST'])
def product_page(id):

    product = Product.query.get(id)

    if request.method == 'POST':
        user = current_user
        def create_order(quantity):
            order = Order(
                product=product.id,
                quantity=int(quantity)
                )
            product.quantity -= int(quantity)
            product.save()
            return order

        try:
            if not user.cart_id:
                order = create_order(request.form.get('quantity'))
                order.save()

                card = Card(customer=user.email)
                card.product_order.extend([order])
                card.save()

                user.cart_id = card.id
                db.session.add(user)
                db.session.commit()

            else:
                card = Card.query.filter_by(customer=user.email)[0]
                if card.product_order:
                    num = 0
                    for order in card.product_order:
                        if product == order.product_obj:
                            order.quantity += int(request.form.get('quantity'))
                            product.quantity -= int(request.form.get('quantity'))
                            product.save()
                            order.save()
                            num = 1
                    if not num:
                        order = create_order(request.form.get('quantity'))
                        card.product_order.extend([order])
                else:
                    order = create_order(request.form.get('quantity'))
                    card.product_order.extend([order])

                card.save()

            flash(f"Product {product.name} was added to card")
        except Exception as _ex:
            flash(f'{_ex}')
    return render_template('products/product-page.html', product=product)


@pr.route('/create_product', methods=['GET', 'POST'])
def create_product():

    form = CreateProductForm()
    if form.validate_on_submit():
        try:
            product = Product(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                quantity=form.quantity.data,
                owner=current_user.email,
                # owner_name=current_user.name if current_user.name else \
                #     current_user.company_name
            )
            product.product_category.extend([ProductCategory.query.get(category) for category in form.category.data])

            images = request.files.getlist('image')

            if images:
                for image in images:
                    if allowed_extension(image.filename):
                        path = os.path.join(UPLOAD_FOLDER, 'img/user_inputs/products/', secure_filename(image.filename))
                        image.save(os.path.join(path))
                        product_image = Image(path=os.path.join('img/user_inputs/products/', secure_filename(image.filename)))
                        db.session.add(product_image)
                        product.images.extend([product_image])
                    else:
                        flash(f'You can appload only png, jpg or jpeg extensions. The file {image} is not available')
            else:
                flash('You have not choose any images')

            db.session.add(product)
            db.session.commit()
            flash(f'Product {product} created successfully')
            return redirect(url_for('main.home'))

        except Exception as _ex:
            flash(f'{_ex}')
            db.session.rollback()
            return render_template('products/create_product.html', form=form)
        finally:
            db.session.close()
    return render_template('products/create_product.html', form=form)

@login_required
@pr.route('/edit_product/<id>', methods=['GET', 'POST'])
def edit_product(id):

    product = Product.query.get(id)
    data = {
        'form': CreateProductForm(),
        'product': product,
        'categories': ProductCategory.query.all()
    }
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = request.form.get('price')
        product.quantity = request.form.get('quantity')

        categories = [ProductCategory.query.filter_by(name=category).first() for category in request.form.getlist('category')]
        product.product_category = categories

        images = request.files.getlist('images')
        new_images = []
        for image in images:
            if image.filename != '':
                if allowed_extension(image.filename):
                    path = os.path.join(
                        UPLOAD_FOLDER,
                        'img/user_inputs/products/',
                        secure_filename(image.filename)
                        )
                    image.save(os.path.join(path))
                    product_image = Image(
                        path=os.path.join('img/user_inputs/products/',
                        secure_filename(image.filename))
                        )
                    db.session.add(product_image)
                    new_images.append(product_image)
                else:
                    flash(f'You can appload only png, jpg or jpeg extensions. The file {image} is not available')
        if new_images:
            product.images = []
            product.images.extend(new_images)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('product_page', id=id))
    return render_template('products/edit_product.html', **data)


@pr.route('/delete_product/<id>', methods=['GET', 'POST', 'DELETE'])
def delete_product(id):
    Product.query.get(id).delete()
    return redirect(url_for('product_page', id=id))


@pr.route('/card', methods=['GET', 'POST'])
def card(id=None):
    [session.pop(key) for key in list(session.keys()) if key[0:4] == 'RATE']
    data = {
        'card': None,
        'products_with_disc': None
    }
    if current_user.cart_id:
        card = Card.query.get(current_user.cart_id)
        data = {
            'card': card,
        }
        if current_user.active_discount:
            for order in card.product_order:
                if order.product_obj in current_user.coupons[-1].promotion.products:
                    data['products_with_disc'] = True
                    break

    return render_template('products/card.html', **data)


@pr.route('/checkout/<cart_id>', methods=['GET', 'POST'])
def checkout(cart_id):
    cart = Card.query.get(cart_id)
    data = {
        'cart': cart
    }
    return render_template('products/checkout-page.html', **data)


@pr.route('/save_product', methods=['GET', 'PUT'])
def save_product():
    if request.method == 'PUT':
        current_user.save_product(request.form.get('id'))
        return ('', 204)


@pr.route('/change_product_amount', methods=['POST'])
def change_product_amount():
    if request.method == 'POST':
        order = Order.query.get(request.form.get('order_id'))
        product = Product.query.get(order.product)
        operator = request.form.get('operator')
        if operator == '+':
            order.quantity += 1
            product.quantity -= 1
        else:
            order.quantity -= 1
            product.quantity += 1
        order.save()
        product.save()
        return ('', 204)


@pr.route('/delete_order', methods=['POST'])
def delete_order():
    if request.method == 'POST':
        order = Order.query.get(request.form.get('order_id'))
        product = Product.query.get(order.product)
        product.quantity += order.quantity
        order.delete()
        return ('', 204)


@pr.route('/delete_cart', methods=['POST'])
@pr.route('/delete_cart/<cart_id>', methods=['GET'])
def delete_cart(cart_id=None):
    print(cart_id)
    if not cart_id:
        if request.method == 'POST':
            cart_id = request.form.get('cart_id')
    cart = Card.query.get(cart_id)
    for product in cart.product_order:
        product.product_obj.quantity += product.quantity
        db.session.add(product)
    db.session.commit()
    current_user.cart_id = 0
    db.session.add(current_user)
    cart.delete()
    return redirect(url_for('card'))