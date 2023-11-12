from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from flask_session import Session
from .forms import GoodsForm, UserLoginForm, LogoutForm, UserRegistrationForm, CartForm, ProductSettingsForm, CommentSForm,\
    SearchForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///app.db'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'


class Goods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    default_price = db.Column(db.Integer, nullable=False)
    discount_price = db.Column(db.Integer, nullable=True)
    sale = db.Column(db.Boolean, default=False)
    image = db.Column(db.String)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, default='user')

    def gen_pass_hash(self, password):
        self.password = generate_password_hash(password)

    def check_pass_hash(self, password):
        return check_password_hash(self.password, password)


class Comments(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    advantages = db.Column(db.String, nullable=False)
    disadvantages = db.Column(db.String, nullable=False)
    comment = db.Column(db.String, nullable=False)
    user_name = db.Column(db.String, nullable=False)
    image = db.Column(db.String)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.route('/cart/<int:id>', methods=['POST', 'GET'])
def cart(id):
    if session.get('cart', 0) == 0:
        session['cart'] = [id]
    else:
        session['cart'].append(id)
    return redirect('/')


@app.route('/buy/<int:id>', methods=['POST', 'GET'])
def buy(id):
    if session.get('cart', 0) == 0:
        session['cart'] = [id]
    else:
        session['cart'].append(id)
    return redirect('/cart')


@app.route('/sale', methods=['GET', 'POST'])
def sale():
    sale_goods = Goods.query.filter_by(sale=True)
    return render_template('sale.html', products=sale_goods)


@app.route('/cart', methods=['POST', 'GET'])
def cart1():
    total = 0
    cart_list = []
    form = CartForm()
    try:
        cart = session['cart']
        for i in cart:
            cart_list.append(Goods.query.get(i))
        for j in cart_list:
            total += j.default_price
            print(total)
        if form.validate_on_submit():
            session.clear()
            return redirect('/')
    except KeyError:
        return render_template('cart.html', message='Your cart is empty')
    return render_template('cart.html', cart=cart, form=form, cart_list=cart_list, total=total)


@app.route('/check_user', methods=['GET', 'POST'])
def check_user():
    try:
        print(current_user.id)
    except AttributeError:
        return render_template('base.html')
    return render_template('base.html')


@login.user_loader
def user_loader(id):
    return User.query.get(int(id))


@app.route('/product/<int:id>/settings', methods=['GET', 'POST'])
@login_required
def product_settings(id):
    product = Goods.query.get(id)
    form = ProductSettingsForm()
    if form.validate_on_submit():
        # product_new_price = form.discount_price.data
        product_image = form.image.data
        if product_image.filename == '':
            product.name = form.name.data
            product.country = form.country.data
            product.default_price = form.price.data
            product.year = form.price.data
            product.sale = form.sale.data

        # if product_new_price is None:
        #     product.name = form.name.data
        #     product.country = form.country.data
        #     product.price = form.price.data
        #     product.year = form.price.data
        #     product.sale = form.sale.data
        #
        # if product_new_price is not None:
        #     # product.new_price = form.discount_price.data
        #     product.name = form.name.data
        #     product.country = form.country.data
        #     product.price = form.price.data
        #     product.year = form.price.data
        #     product.sale = form.sale.data
        #
        else:
            product_image.save(f'app/static/images/{product_image.filename}')
            product.image = f'/static/images/{product_image.filename}'
            product.name = form.name.data
            product.country = form.country.data
            product.price = form.price.data
            product.year = form.price.data
            product.sale = form.sale.data
        db.session.commit()
        return redirect('/')
    return render_template('product_settings.html', form=form, product=product)


@app.route('/', methods=['POST', 'GET'])
def main_page():
    goods = Goods.query.all()
    users = User.query.all()
    filtered_goods = []
    try:
        cart = session['cart']
    except KeyError:
        return render_template('main_page.html', goods=goods, users=users)
    if request.method == 'POST':
        ukr = request.form['Ukraine']
        print(ukr)
        jap = request.form['Japan']
        usa = request.form['USA']
        chi = request.form['China']
        ger = request.form['Germany']
        products = Goods.query.all()
        for i in products:
            if i.country == ukr or i.country == jap or i.country == usa or i.country == chi or i.country == ger:
                filtered_goods.append(i)
                print(filtered_goods)
                return redirect('/')
    return render_template('main_page.html', goods=goods, users=users, cart=cart)


@app.route('/delete_user/<int:id>')
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/')


@app.route('/delete_comment/<int:id>')
def delete_comment(id):
    comment = Comments.query.get(id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(f'/product/{id}')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        data = request.form['search']
        results = Goods.query.filter(Goods.name.ilike(f'%{data}%')).all()
        return render_template('main_page.html', products=results)
    else:
        return render_template('search.html')


@app.route('/delete_product/<int:id>')
def delete_product(id):
    product = Goods.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return redirect('/')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = LogoutForm()
    if form.validate_on_submit():
        logout_user()
        return redirect('/')
    return render_template('profile.html', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = UserRegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        user = User(name=name, email=email)
        user.gen_pass_hash(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        name = form.name.data
        password = form.password.data
        user = User.query.filter_by(name=name).first()
        if user is None or not user.check_pass_hash(password):
            return redirect('/login')
        else:
            login_user(user, remember=form.remember_me.data)
            return redirect('/profile')
    return render_template('login.html', form=form)


@app.route('/Ukraine', methods=['GET', 'POST'])
def Ukraine_filter():
    Ukraine_goods = Goods.query.filter_by(country='Ukraine')
    return render_template('Ukraine.html', goods=Ukraine_goods)


@app.route('/USA', methods=['GET', 'POST'])
def USA_filter():
    USA_goods_ = Goods.query.filter_by(country='USA')
    return render_template('USA.html', goods=USA_goods_)


@app.route('/Japan', methods=['GET', 'POST'])
def Japan_filter():
    Japan_goods = Goods.query.filter_by(country='Japan')
    return render_template('Japan.html', goods=Japan_goods)


@app.route('/Germany', methods=['GET', 'POST'])
def Germany_filter():
    Germany_goods = Goods.query.filter_by(country='Germany')
    return render_template('Germany.html', goods=Germany_goods)


@app.route('/China', methods=['GET', 'POST'])
def China_filter():
    China_goods = Goods.query.filter_by(country='China')
    return render_template('China.html', goods=China_goods)


# @app.route('/Older', methods=['GET', 'POST'])
# def western_filter():
#     older = Goods.query.filter(year2021)
#     return render_template('Ukraine.html', goods=ukraine_goods)


@app.route('/2021', methods=['GET', 'POST'])
def year1_filter():
    year2021 = Goods.query.filter_by(year='2021')
    return render_template('2021.html', goods=year2021)


@app.route('/2022', methods=['GET', 'POST'])
def year2_filter():
    year2022 = Goods.query.filter_by(country='2022')
    return render_template('Ukraine.html', goods=year2022)


@app.route('/2023', methods=['GET', 'POST'])
def year3_filter():
    year2023 = Goods.query.filter_by(country='2023')
    return render_template('Ukraine.html', goods=year2023)


# @app.route('/New', methods=['GET', 'POST'])
# def western_filter():
#     ukraine_goods_ = Goods.query.filter_by(country='Ukraine')
#     return render_template('Ukraine.html', goods=ukraine_goods)

@app.route('/admin_panel', methods=['GET', 'POST'])
def add_product():
    users = User.query.all()
    form = GoodsForm()
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        year = form.year.data
        country = form.country.data
        image = request.files['image']
        if image.filename == '':
            product = Goods(name=name, default_price=price, year=year, country=country,
                            image='/static/images/no_image.jpg')
        else:
            image.save(f'app/static/images/{image.filename}')
            product = Goods(name=name, default_price=price, year=year, country=country,
                            image=f'/static/images/{image.filename}')
        db.session.add(product)
        db.session.commit()


        return redirect('/')
    return render_template('admin_panel.html', form=form, users=users)


@app.route('/product/<int:id>', methods=['GET', 'POST'])
def product_page(id):
    comments = Comments.query.filter_by(id=id)
    form = CommentSForm()
    product = Goods.query.filter_by(id=id).first()
    if form.validate_on_submit():
        advantages = form.advantages.data
        disadvantages = form.disadvantages.data
        user_name = form.user_name.data
        comment = request.form['comment']
        image = request.files['image']
        if image.filename == '':
            comment = Comments(advantages=advantages, disadvantages=disadvantages,comment=comment, user_name=user_name)
        else:
            image.save(f'app/static/images/{image.filename}')
            comment = Comments(advantages=advantages, disadvantages=disadvantages, comment=comment, user_name=user_name,
                               image=(f'/static/images/{image.filename}'))

        db.session.add(comment)
        db.session.commit()
        return redirect(f'/product/{id}')
    try:
        cart = session['cart']
    except KeyError:
        return render_template('product_page.html', product=product, form=form, comments=comments)
    return render_template('product_page.html', product=product, cart=cart, form=form, user=current_user,
                           comments=comments)
