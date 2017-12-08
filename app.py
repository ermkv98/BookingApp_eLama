from flask import Flask, request, redirect, url_for, render_template
from flask_login import login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///common.db'
app.config['SECRET_KEY'] = 'elama'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'asdjweklqwejiocimweqwoe'
db = SQLAlchemy(app)


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


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/profile/<id>')
@login_required
def profile(id):
    id = current_user.get_id()
    user = User.query.filter_by(id=id).first()
    return render_template('profile.html', user=user)


@app.route('/post_user', methods=['POST'])
def post_user():
    user = User(request.form['username'], request.form['email'])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
        id = current_user.get_id()
        new_first_name = request.form.get("new")
        user = User.query.filter_by(id=id).first()
        user.name_first = new_first_name
        db.session.commit()
        return render_template('profile_edit.html', user=user)


@app.route('/list')
def list():
    cursor = db.session.cursor(buffered=True)
    select=("SELECT * FROM user")
    cursor.execute(select)
    data = cursor.fetchall()
    db.session.commit()
    return render_template('list.html', data=data)


@app.route('/complete/<id>')
def complete():
    pass


if __name__ == '__main__':
    app.run(debug=True)