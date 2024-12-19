from flask import render_template, flash, url_for, redirect, request, jsonify, session
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, admin, bcrypt, login_manager
from .forms import LoginForm, RegisterForm
from .models import User, Product, Cart
from flask_admin.contrib.sqla import ModelView
import json

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Cart, db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def index():
    app.logger.info('index route request')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Logged in successfully.')
                return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/men')
def men():
    products = Product.query.filter_by(category='men').all()
    return render_template('men.html', products=products)

@app.route('/women')
def women():
    products = Product.query.filter_by(category='women').all()
    return render_template('women.html', products=products)

@app.route('/kids')
def kids():
    products = Product.query.filter_by(category='kids').all()
    return render_template('kids.html', products=products)

def get_product_by_id(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product:
        return product
    return None
        
@app.route('/product/<int:product_id>')
def product_page(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found")
        return redirect(url_for('kids'))
    return render_template('product_page.html', product=product)

@app.route('/cart', methods=['GET'])
@login_required
def cart():
    items = Cart.query.filter_by(user_id=current_user.id).all()
    price = sum(item.product.price * item.quantity for item in items)
    return render_template('cart.html', items=items, price=price)


@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    data = json.loads(request.data)
    
    product_id = int(data.get('product_id'))
    quantity = int(data.get('quantity')) 

    product = Product.query.get(product_id)

    if not product:
        return json.dumps({'status': 'error', 'message': 'Product not found'})

    if product.stock < quantity:
        return json.dumps({'status': 'error', 'message': 'Not enough stock available'})

    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    product.stock -= quantity
    db.session.commit()

    return json.dumps({'status': 'OK', 'message': f'Added {product.title} to cart'})


@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if not cart_item:
        return jsonify({'error': 'Item not found in cart'})
    
    product = Product.query.get(product_id)

    if product:
        product.stock += cart_item.quantity

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({'message': 'Item removed from cart'})