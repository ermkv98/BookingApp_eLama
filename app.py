from flask import Flask, request, redirect, url_for, render_template, g
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user
from forex_python.converter import CurrencyRates
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///common.db'
app.config['SECRET_KEY'] = 'elama'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'asdjweklqwejiocimweqwoe'
db = SQLAlchemy(app)


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


login_manager.init_app(app)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    currency_USD = db.Column(db.Float, default=0)
    currency_RUR = db.Column(db.Float, default=0)
    currency_EUR = db.Column(db.Float, default=0)
    name_first = db.Column(db.String(100))
    name_second = db.Column(db.String(100))
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    entries = db.relationship('Entry', backref='user', lazy='dynamic')
    whishes = db.relationship('Wish', backref='user', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    plans = db.relationship('Plan', backref='user', lazy='dynamic')
    categories = db.relationship('Category', backref='user', lazy='dynamic')
    tags = db.relationship('Tag', backref='user', lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.id


class Entry(db.Model):
    entry_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100))
    cost_USD = db.Column(db.Float)
    cost_RUR = db.Column(db.Float)
    cost_EUR = db.Column(db.Float)
    category = db.Column(db.String(100))
    type = db.Column(db.Boolean)
    date = db.Column(db.DateTime)
    tags = db.relationship('Tag', backref='tag_entry', lazy='dynamic')


class Wish(db.Model):
    name = db.Column(db.String(100))
    wish_id = db.Column(db.Integer, primary_key=True)
    cost_USD = db.Column(db.Float)
    cost_RUR = db.Column(db.Float)
    cost_EUR = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Transaction(db.Model):
    cost_USD = db.Column(db.Float)
    cost_RUR = db.Column(db.Float)
    cost_EUR = db.Column(db.Float)
    id_to_sent = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime)
    transaction_id = db.Column(db.Integer, primary_key=True)


class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    entry = db.Column(db.Integer, db.ForeignKey('entry.entry_id'))


class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Plan(db.Model):
    cost_USD = db.Column(db.Float)
    cost_RUR = db.Column(db.Float)
    cost_EUR = db.Column(db.Float)
    name = db.Column(db.String(100))
    month = db.Column(db.String(20))
    plan_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.before_request
def global_user():
    g.user = current_user


@app.context_processor
def inject_user():
    try:
        return {'user': g.user}
    except AttributeError:
        return {'user': None}


@app.route('/')
@login_required
def redirect_to_home():
    return redirect('/1')


@app.route('/plan_add', methods=['GET', 'POST'])
@login_required
def plan_add():
    plan = Plan()
    plan.cost_USD = request.form.get('EUR')
    plan.cost_RUR = request.form.get('RUR')
    plan.cost_EUR = request.form.get('EUR')
    plan.name = request.form.get('name')
    plan.month = request.form.get('month')
    plan.user_id = g.user.id
    db.session.add(plan)
    db.session.commit()
    return redirect(url_for('redirect_to_home', plan=plan))


@app.route('/<int:page>')
@login_required
def index(page=1):
    entry = Entry.query.filter_by(user_id=g.user.id)
    currency_rate = CurrencyRates()
    entries = Entry.query.paginate(per_page=5, page=page, error_out=True)
    plans = Plan.query.filter_by(user_id=g.user.id)
    return render_template('index.html', entry=entry, plans=plans, entries=entries, currency_rate=currency_rate)


@app.route('/add_entry', methods=['GET', 'POST'])
@login_required
def add_entry():
    if request.method == 'POST':
        entry = Entry()
        entry.user_id = g.user.id
        entry.date = datetime.now()
        entry.cost_EUR = request.form.get("EUR")
        entry.cost_RUR = request.form.get("RUR")
        entry.cost_USD = request.form.get("USD")
        g.user.currency_EUR -= float(request.form.get("EUR"))
        g.user.currency_RUR -= float(request.form.get("RUR"))
        g.user.currency_USD -= float(request.form.get("USD"))
        entry.name = request.form.get("Name")
        entry.category = request.form.get("Category")
        entry.type = False
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('redirect_to_home'))
    return render_template('index.html')


@app.route('/entry_delete<int:entry_id>')
@login_required
def entry_delete(entry_id):
    entry = Entry.query.filter_by(entry_id=entry_id)
    entry.delete()
    db.session.commit()
    return redirect(url_for('redirect_to_home'))


@app.route('/entry_edit?<int:entry_id>', methods=['POST', 'GET'])
@login_required
def entry_edit(entry_id):
    entry = Entry.query.filter_by(entry_id=entry_id).first()
    if request.method == 'POST':
        entry.name = request.form.get('Name')
        entry.category = request.form.get('Category')
        entry.cost_USD = request.form.get('USD')
        entry.cost_RUR = request.form.get('RUR')
        entry.cost_EUR = request.form.get('EUR')
        db.session.commit()
        return redirect(url_for('redirect_to_home'))
    return render_template('entry_edit.html', entry_id=entry_id, entry=entry)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    tags = Tag.query.filter_by(user_id=g.user.id).all()
    categories = Category.query.filter_by(user_id=g.user.id).all()
    return render_template('profile.html', tags=tags, categories=categories)


@app.route('/profile/edit', methods=['POST', 'GET'])
@login_required
def edit():
    user = g.user
    if request.method == 'POST':
        user.name_first = request.form.get("new first name")
        user.name_second = request.form.get("new second name")
        user.email = request.form.get("new email")
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('profile.html', user=g.user)


@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    transaction = Transaction.query.filter_by(user_id=g.user.id, id_to_sent=g.user.id)
    return render_template('transactions.html', transaction=transaction)


@app.route('/tag_remove<tag_id>', methods=['GET', 'POST'])
@login_required
def tag_remove(tag_id):
    tag = Tag.query.filter_by(tag_id=tag_id)
    tag.delete()
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/category', methods=['GET', 'POST'])
@login_required
def category():
    category = Category()
    category.category_name = request.form.get('category')
    category.user_id = g.user.id
    db.session.add(category)
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/category_remove<category_id>', methods=['GET', 'POST'])
@login_required
def category_remove(category_id):
    category = Category.query.filter_by(category_id=category_id)
    category.delete()
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/tag', methods=['GET', 'POST'])
@login_required
def tag():
    tag = Tag()
    tag.tag_name = request.form.get('tag')
    tag.user_id = g.user.id
    db.session.add(tag)
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        entry = Entry()
        entry.user_id = g.user.id
        entry.date = datetime.now()
        entry.cost_EUR = request.form.get("EUR")
        entry.cost_RUR = request.form.get("RUR")
        entry.cost_USD = request.form.get("USD")
        g.user.currency_EUR += float(request.form.get("EUR"))
        g.user.currency_RUR += float(request.form.get("RUR"))
        g.user.currency_USD += float(request.form.get("USD"))
        entry.name = "Popolnenie"
        entry.category = "Transacia"
        entry.type = True
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('redirect_to_home'))
    return render_template('index.html')


@app.route('/transactions/decrease', methods=['GET', 'POST'])
@login_required
def decrease():
    if request.method == 'POST':
        entry = Entry()
        entry.user_id = g.user.id
        entry.date = datetime.now()
        entry.cost_EUR = request.form.get("EUR")
        entry.cost_RUR = request.form.get("RUR")
        entry.cost_USD = request.form.get("USD")
        g.user.currency_EUR -= float(request.form.get("EUR"))
        g.user.currency_RUR -= float(request.form.get("RUR"))
        g.user.currency_USD -= float(request.form.get("USD"))
        entry.name = "Trata"
        entry.category = "Transacia"
        entry.type = False
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('redirect_to_home'))
    return render_template('index.html')


@app.route('/transactions/send', methods=['GET', 'POST'])
@login_required
def send():
    if request.method == 'POST':
        send = Transaction()
        send.cost_EUR = request.form.get("EUR")
        send.cost_RUR = request.form.get("RUR")
        send.cost_USD = request.form.get("USD")
        send.date = datetime.now()
        send.id_to_sent = request.form.get("id to sent")
        user_recipient = User.query.filter_by(id=send.id_to_sent).first()
        if user_recipient != None :
            send.user_id = g.user.id
            g.user.currency_RUR -= float(send.cost_RUR)
            g.user.currency_EUR -= float(send.cost_EUR)
            g.user.currency_USD -= float(send.cost_USD)
            user_recipient.currency_RUR += float(send.cost_RUR)
            user_recipient.currency_EUR += float(send.cost_EUR)
            user_recipient.currency_USD += float(send.cost_USD)
            db.session.add(send)
            db.session.commit()
            return redirect(url_for('profile'))
        return render_template('transactions.html')
    return render_template('transactions.html')


@app.route('/transactions/exchange')
@login_required
def exchange():
    if request.method == 'POST':
        currency = CurrencyRates()
        first = request.form.get('first_currency')
        second = request.form.get('second_currency')
        input_currency = request.form.get('input_currency')
        if first == "EUR":
            if second == "USD":
                g.user.currency_EUR -= input_currency
                g.user.currency_USD += currency.convert(input_currency, first, second)
            if second == "RUR":
                g.user.currency_EUR -= input_currency
                g.user.currency_RUR += currency.convert(input_currency, first, second)
        return redirect(url_for('redirect_to_home'), first=first, second=second, input_currency=input_currency)
    return redirect(url_for('redirect_to_home'))


if __name__ == '__main__':
    app.run(debug=True)