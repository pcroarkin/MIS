from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, DateField, IntegerField, SubmitField, HiddenField, FileField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, Email
from flask_wtf.file import FileAllowed
from app.models import OrderStatus

class CustomerForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    contact_person = StringField('Contact Person', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    city = StringField('City', validators=[DataRequired(), Length(max=50)])
    state = StringField('State/Province', validators=[DataRequired(), Length(max=50)])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(max=20)])
    country = StringField('Country', validators=[DataRequired(), Length(max=50)])
    tax_id = StringField('Tax ID', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Customer')

class OrderForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()], format='%Y-%m-%d')
    notes = TextAreaField('Notes', validators=[Optional()])
    status = SelectField('Status', validators=[DataRequired()], 
                        choices=[(status.name, status.value) for status in OrderStatus])
    submit = SubmitField('Save Order')

class JobForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    width = DecimalField('Width (mm)', validators=[Optional()])
    height = DecimalField('Height (mm)', validators=[Optional()])
    pages = IntegerField('Number of Pages', validators=[Optional(), NumberRange(min=1)])
    colors = StringField('Colors (e.g., 4/4, 4/1)', validators=[Optional()])
    paper_type = StringField('Paper Type', validators=[Optional()])
    finishing = TextAreaField('Finishing Options', validators=[Optional()])
    estimated_hours = DecimalField('Estimated Hours', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Notes', validators=[Optional()])
    file_upload = FileField('Upload File', validators=[
        Optional(),
        FileAllowed(['pdf', 'ai', 'psd', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'eps', 'indd'], 
                    'Only graphics and design files are allowed!')
    ])
    submit = SubmitField('Save Job')

class QuoteForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    due_date = DateField('Requested Due Date', validators=[DataRequired()], format='%Y-%m-%d')
    notes = TextAreaField('Project Description', validators=[DataRequired()])
    submit = SubmitField('Create Quote')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    search_type = SelectField('Search Type', choices=[
        ('customer', 'Customer'),
        ('order', 'Order'),
        ('job', 'Job')
    ])
    submit = SubmitField('Search')
