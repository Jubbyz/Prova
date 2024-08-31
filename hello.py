import os
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name        = StringField('Cadastre o novo Professor:', validators=[DataRequired()])
    role  = SelectField('Disciplina associada:' , choices=[('DSWA5', 'DSWA5'), ('GPSA5', 'GPSA5'), ('IHCA5', 'IHCA5'), ('SODA5', 'SODA5'), ('PJIA5', 'PJIA5'), ('TCOA5', 'TCOA5')])
    submit      = SubmitField('Cadastrar')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/professores', methods=['GET', 'POST'])
def professores():
    form = NameForm()
    user_all = User.query.all();
    role_all = Role.query.all();
    print(user_all);
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()                        
        if user is None:
            user_role = Role.query.filter_by(name=form.role.data).first();
            user = User(username=form.name.data, role=user_role);
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('professores'))
    return render_template('professores.html', form=form, name=session.get('name'),
                           known=session.get('known', False),
                           user_all=user_all, role_all = role_all);


@app.route('/avaliacao')
def avaliacao():
    return render_template('avaliacao.html')



@app.route('/disciplina')
def disc():
    return render_template('disciplina.html')


@app.route('/aluno')
def aluno():
    return render_template('aluno.html')