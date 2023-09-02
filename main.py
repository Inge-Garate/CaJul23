from flask import Flask, render_template, request, redirect, url_for, flash
from db import engine, load_obras_from_db, load_asistencias_from_db, load_gastos_from_db, load_nombre_obra_from_db, load_trabajadores_from_db, load_contratos_from_db, load_monto_gastos_from_db, load_monto_contratos_from_db, load_dropdwn_contratos_from_db, load_asistencias_sem_from_db, load_asistencias_empleado_from_db, load_workers_from_db, load_nombre_empleado_from_db, load_estimaciones_from_db, load_monto_est_from_db, load_monto_fg_from_db
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from forms import LoginForm, RegistrationForm, RegistroAsistenciaForm
from datetime import timedelta, date
from collections import defaultdict
import os

# Create a login manager object
login_manager = LoginManager()
app = Flask(__name__)

# Add this line to pass the set function to the Jinja2 environment
app.jinja_env.globals['set'] = set

# Often people will also separate these into a separate config.py file
my_secret = os.environ['DB_CONNECTION_STRING']
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = my_secret
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)

# We can now pass in our app to the login manager
login_manager.init_app(app)

# Tell users what view to go to when they need to login.
login_manager.login_view = "login"

# By inheriting the UserMixin we get access to a lot of built-in attributes
# which we will be able to call in our views!
# is_authenticated()
# is_active()
# is_anonymous()
# get_id()

# The user_loader decorator allows flask-login to load the current user
# and grab their id.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):

    # Create a table in the db
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        # https://stackoverflow.com/questions/23432478/flask-generate-password-hash-not-constant-output
        return check_password_hash(self.password_hash,password)

class Asistencias(db.Model):

    # Create a table in the db
    __tablename__ = 'ASISTENCIAS'

    id_asistencia = db.Column(db.Integer, primary_key = True, index=True)
    id_obra = db.Column(db.Integer, unique=False, index=True)
    id_contrato = db.Column(db.Integer, unique=False, index=True)
    id_empleado = db.Column(db.Integer, unique=False, index=True)
    fecha = db.Column(db.Date, unique=False)
    boolean_asistencia = db.Column(db.String(2), unique=False)
    notas = db.Column(db.Text, unique=False)
  
    def __init__(self, id_obra, id_contrato, id_empleado, fecha, boolean_asistencia, notas):
        self.id_obra = id_obra
        self.id_contrato = id_contrato
        self.id_empleado = id_empleado
        self.fecha = fecha
        self.boolean_asistencia = boolean_asistencia
        self.notas = notas

@app.route('/')
def index():
    return render_template('0.html')

@app.route('/welcome')
@login_required
def welcome_user():
    return render_template('welcome_user.html')

def get_previous_saturday(date):
    days_to_saturday = (date.weekday() - 5) % 7
    return date - timedelta(days=days_to_saturday)

def get_week_ranges(min_date, max_date):
    # Adjust min_date to the nearest Saturday
    min_date = get_previous_saturday(min_date)
    
    # Function to generate date ranges for each week between min and max dates
    start_date = min_date
    week_ranges = []
    while start_date <= max_date:
        end_date = start_date + timedelta(days=6)
        if end_date > max_date:
            end_date = max_date
        week_ranges.append((start_date, end_date))
        start_date = end_date + timedelta(days=1)
    return week_ranges
  
@app.route('/check_asistencias')
@login_required
def check_asistencias():
  id_obra = request.args.get('id_obra')
  nombre_obra = request.args.get('nombre_obra')
  
  # Load data from the database
  asistencias = load_asistencias_sem_from_db(engine, id_obra)
  if not asistencias:
      return render_template('check_asistencias.html', id_obra=id_obra, nombre_obra=nombre_obra)

  # Extract min and max dates from the data
  min_fecha = min(asistencias, key=lambda x: x['fecha'])['fecha']
  print("min_fecha:", min_fecha)
  max_fecha = max(asistencias, key=lambda x: x['fecha'])['fecha']
  
  # Adjust min_fecha to the nearest Saturday
  min_fecha = get_previous_saturday(min_fecha)
  #print("adjusted min_fecha:", min_fecha)
  
  # Get date ranges for each week
  week_ranges = get_week_ranges(min_fecha, max_fecha)
  #print("week_ranges:", week_ranges)

  # Create a dictionary to store the data for each week
  week_data = {week: [] for week in week_ranges}

  # Create a defaultdict to store the data for each week
  week_data = defaultdict(list)

  # Group the data by week
  for asistencia in asistencias:
      fecha = asistencia['fecha']
      for week_range in week_ranges:
          if week_range[0] <= fecha <= week_range[1]:
              week_data[week_range].append(asistencia)
              break
            
  #Print the week_data contents
  #for i, data in enumerate(week_data.values()):
    #print(f"Week {i+1} Data:", data)
    
  # Fill in empty weeks with an empty list
  for week_range in week_ranges:
      if week_range not in week_data:
          week_data[week_range] = []

  week_data = [(week_range, data) for week_range, data in week_data.items()]

  very_early_date = date.min
  
  # Sort week_data by the start date of each week range
  week_data.sort(key=lambda x: x[0][0] if x[0] else very_early_date)
  
  # Pass the timedelta function to the Jinja2 environment as a global variable
  app.jinja_env.globals['timedelta'] = timedelta

  # Render the template with the data for each week
  return render_template('check_asistencias.html', id_obra=id_obra, nombre_obra=nombre_obra, week_data=week_data, week_ranges=week_ranges)
  
  # Load data from the database
  asistencias = load_asistencias_sem_from_db(engine, id_obra)
  if not asistencias:
      return render_template('check_asistencias.html', id_obra=id_obra, nombre_obra=nombre_obra)

@app.route('/modifica_asistencias')
@login_required
def modifica_asistencias():
    return render_template('modifica_asistencias.html')

@app.route('/alta_asistencias', methods=['GET', 'POST'])
@login_required
def alta_asistencias():
  id_obra = request.args.get('id_obra')
  contratos = load_dropdwn_contratos_from_db(id_obra)
  empleados = load_trabajadores_from_db(id_obra)
  nombre_obra = request.args.get('nombre_obra')
  form = RegistroAsistenciaForm() 
  # Set the choices for the id_empleado field
  form.id_empleado.choices = [(empleado['id_empleado'], empleado['empleado']) for empleado in empleados]
  # Set the choices for the id_contrato field
  form.id_contrato.choices = [(contrato['id_contrato'], contrato['nombre_contrato']) for contrato in contratos]

  if request.method == 'POST':
      # Process the form with the data from the request
      form.process(request.form)
  # Set the id_obra field with the correct value
  form.id_obra.data = id_obra

  if form.validate_on_submit():
      id_contrato = form.id_contrato.data
      fecha = form.fecha.data
      boolean_asistencia = form.boolean_asistencia.data
      notas = form.notas.data

      # Loop through each selected employee
      for id_empleado in form.id_empleado.data:
          asistencia = Asistencias(
              id_obra=id_obra,
              id_contrato=id_contrato,
              id_empleado=id_empleado,
              fecha=fecha,
              boolean_asistencia=boolean_asistencia,
              notas=notas)
          db.session.add(asistencia)
      db.session.commit()
      flash('Asistencias registradas')
      return redirect(url_for("CA", obra=id_obra))
    
  return render_template('alta_asistencias.html', form=form, id_obra=id_obra, nombre_obra=nombre_obra, contratos=contratos, empleados=empleados)

@app.route("/obras", methods=["POST", "GET"])
@login_required
def obras():
  obras = load_obras_from_db()
  if request.method == "POST":
    obra = request.form["obra"]
    return redirect(url_for("CA", obra=obra))
  else:
    return render_template('select_obra.html', obras=obras)

@app.route('/<obra>', methods=["POST", "GET"])
@login_required
def CA(obra):
  id_obra = obra
  contratos = load_contratos_from_db(obra)
  nombre_obra = load_nombre_obra_from_db(obra)
  trabajadores = load_trabajadores_from_db(obra)
  asistencias = load_asistencias_from_db(obra)
  gastos = load_gastos_from_db(obra)
  monto_gastos = load_monto_gastos_from_db(obra)
  monto_contratos = load_monto_contratos_from_db(obra)
  estimaciones = load_estimaciones_from_db(obra)
  monto_estimaciones = load_monto_est_from_db(obra)
  monto_fg = load_monto_fg_from_db(obra)
  return render_template('home.html',
                         id_obra = id_obra,
                         monto_contratos = monto_contratos,
                         monto_gastos = monto_gastos,
                         contratos=contratos,
                         nombre_obra=nombre_obra,
                         trabajadores=trabajadores,
                         asistencias=asistencias,
                         gastos=gastos,
                         estimaciones=estimaciones,
                         monto_estimaciones=monto_estimaciones,
                         monto_fg=monto_fg)
  
@app.route("/select_empleado", methods=["POST", "GET"])
@login_required
def select_empleado():
  empleados = load_workers_from_db()
  if request.method == "POST":
    id_empleado = request.form["id_empleado"]
    return redirect(url_for("calendario_asistencias", id_empleado=id_empleado))
  else:
    return render_template('select_empleado.html', empleados=empleados)

@app.route('/calendario_asistencias/<int:id_empleado>', methods=["GET"])
@login_required
def calendario_asistencias(id_empleado):
  id_empleado = id_empleado
  nombre_empleado=load_nombre_empleado_from_db(id_empleado)

  # Load data from the database
  asistencias = load_asistencias_empleado_from_db(engine, id_empleado)
  if not asistencias:
      return render_template('calendario_asistencias.html', id_empleado=id_empleado)
  
  return render_template('calendario_asistencias.html', id_empleado=id_empleado, asistencias=asistencias, nombre_empleado=nombre_empleado)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user.check_password(form.password.data) and user is not None:
            #Log in the user

            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0]=='/':
                next = url_for('obras')

            return redirect(next)
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering! Now you can login!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

if __name__ == "__main__":
  app.run('0.0.0.0', debug=True)