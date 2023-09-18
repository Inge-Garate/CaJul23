from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired,Email,EqualTo
from wtforms import ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('pass_confirm', message='Passwords deben coincidir!')])
    pass_confirm = PasswordField('Confirma password', validators=[DataRequired()])
    submit = SubmitField('Registrar!')

def validate_email(self, email):
        if User.query.filter_by(email=self.email.data).first():
            raise ValidationError('Este correo ya ha sido registrado')
          
def validate_username(self, username):
        if User.query.filter_by(username=self.username.data).first():
            raise ValidationError('Este nombre de usuario ya ha sido registrado')

class RegistroAsistenciaForm(FlaskForm):
    id_obra = HiddenField('id_obra', validators=[DataRequired()])  
    id_contrato = SelectField('Contrato', coerce=int, validators=[DataRequired()])
    id_empleado = SelectMultipleField('Empleado', coerce=int, validators=[DataRequired()])
    fecha = DateField('Fecha', validators=[DataRequired()])
    boolean_asistencia = SelectField('¿Asistencia?', validators=[DataRequired()], choices=[("si", 'Si'), ("no", 'No')])
    notas = StringField('Notas')   
    submit = SubmitField('Enviar')