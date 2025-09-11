"""
Flask-WTF forms for input validation and CSRF protection.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, FloatField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Email, ValidationError
from datetime import datetime, date

class CreateContractForm(FlaskForm):
    """Form for creating a new contract."""
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=5, max=100, message='Title must be between 5 and 100 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        DataRequired(message='Description is required'),
        Length(min=10, max=1000, message='Description must be between 10 and 1000 characters')
    ])
    
    difficulty = SelectField('Difficulty', 
        choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')],
        validators=[DataRequired(message='Difficulty is required')]
    )
    
    expiration_date = DateField('Expiration Date (Optional)')
    
    payout = FloatField('Payout', validators=[
        DataRequired(message='Payout is required'),
        NumberRange(min=1, max=10000, message='Payout must be between $1 and $10,000')
    ])
    
    test_file = FileField('Test File', validators=[
        FileAllowed(['py'], message='Only Python (.py) files are allowed')
    ])
    
    test_code = TextAreaField('Test Code')
    
    dockerfile = FileField('Dockerfile (Optional)')
    
    additional_files = FileField('Additional Files (Optional)')
    
    def validate_expiration_date(self, field):
        """Custom validator to ensure expiration date is in the future."""
        if field.data and field.data <= date.today():
            raise ValidationError('Expiration date must be in the future')
    
    def validate_dockerfile(self, field):
        """Custom validator to ensure dockerfile has correct name when provided."""
        if field.data and field.data.filename and field.data.filename != 'Dockerfile':
            raise ValidationError('Docker file must be named "Dockerfile"')

class AttemptForm(FlaskForm):
    """Form for submitting an attempt to a contract."""
    file = FileField('Attempt File', validators=[
        FileRequired(message='Attempt file is required'),
        FileAllowed(['py'], message='Only Python (.py) files are allowed')
    ])
    
    payment_email = EmailField('Payment Email', validators=[
        DataRequired(message='Payment email is required'),
        Email(message='Please enter a valid email address')
    ])

class RegisterForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=100, message='Password must be at least 8 characters')
    ])
    
    submit = SubmitField('Register')
    
    def validate_username(self, field):
        """Custom validator to check username format."""
        if not field.data.isalnum():
            raise ValidationError('Username can only contain letters and numbers')

class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])