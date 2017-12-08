from flask import Flask, request, redirect, url_for, render_template, session, g
from flask_login import login_manager, LoginManager, AnonymousUserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user


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
    currency_USD = db.Column(db.Float)
    currency_RUR = db.Column(db.Float)
    currency_EUR = db.Column(db.Float)
    name_first = db.Column(db.String(100))
    name_second = db.Column(db.String(100))
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    entries = db.relationship('Entry', backref='user', lazy='dynamic')

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


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@login_manager.user_loader
def load_user(id):
    try:
        return User.query.get(int(id))
    except (TypeError, ValueError):
        pass


@app.before_request
def global_user():
    g.user = current_user


# Make current user available on templates
@app.context_processor
def inject_user():
    try:
        return {'user': g.user}
    except AttributeError:
        return {'user': None}


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html')


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
    return render_template('profile_edit.html', user=g.user)


@app.route('/list')
@login_required
def list():
    cursor = db.session.cursor(buffered=True)
    select=("SELECT * FROM user")
    cursor.execute(select)
    data = cursor.fetchall()
    db.session.commit()
    return render_template('list.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)