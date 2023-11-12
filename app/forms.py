from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SubmitField, StringField, PasswordField, EmailField, BooleanField, SelectField, IntegerField, \
        FileField, TextAreaField



class GoodsForm(FlaskForm):
    name = StringField('Enter item\'s name', validators=[DataRequired()])
    country = SelectField('Select item\'s country', choices=[('USA', 'USA'),('China', 'China'), ('Ukraine', 'Ukraine'),
        ('Germany', 'Germany'), ('Japan', 'Japan')],
                          validators=[DataRequired()])
    year = IntegerField('Enter year of production', validators=[DataRequired()])
    price = IntegerField('Enter item\'s price', validators=[DataRequired()])
    submit = SubmitField('Add')


class UserRegistrationForm(FlaskForm):
    name = StringField('Enter your name', validators=[DataRequired()])
    email = EmailField('Enter your email', validators=[DataRequired()])
    password = PasswordField('Enter your password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me?')
    submit = SubmitField('Confirm')


class UserLoginForm(FlaskForm):
    name = StringField('Enter your name', validators=[DataRequired()])
    password = PasswordField('Enter your password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me?')
    submit = SubmitField('Confirm')


class LogoutForm(FlaskForm):
    submit = SubmitField('Log Out')


class CartForm(FlaskForm):
    submit = SubmitField('Buy')


class ProductSettingsForm(FlaskForm):
    name = StringField('Enter name', validators=[DataRequired()])
    country = StringField('Enter country', validators=[DataRequired()])
    price = IntegerField('Enter price', validators=[DataRequired()])
    year = IntegerField('Enter year', validators=[DataRequired()])
    image = FileField('Enter new photo')
    sale = BooleanField('Sale?')
    discount_price = IntegerField('Enter new price')
    submit = SubmitField('Change')


class CommentSForm(FlaskForm):
    advantages = StringField('Advantages', validators=[DataRequired()])
    disadvantages = StringField('Disadvantages', validators=[DataRequired()])
    # comment = TextAreaField('Comment', validators=[DataRequired()])
    user_name = StringField('Name', validators=[DataRequired()])
    # image = FileField('')
    submit = SubmitField('Leave a review')


class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Submit')