from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from app.models import InvoiceStatus

class InvoiceForm(FlaskForm):
    due_date = DateField('Due Date', validators=[DataRequired()], format='%Y-%m-%d')
    amount = DecimalField('Amount (before tax)', validators=[DataRequired(), NumberRange(min=0)])
    tax_amount = DecimalField('Tax Amount', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Notes', validators=[Optional()])
    status = SelectField('Status', validators=[DataRequired()], 
                        choices=[(status.name, status.value) for status in InvoiceStatus])
    submit = SubmitField('Save Invoice')

class PaymentForm(FlaskForm):
    amount = DecimalField('Payment Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    payment_date = DateField('Payment Date', validators=[DataRequired()], format='%Y-%m-%d')
    payment_method = SelectField('Payment Method', validators=[DataRequired()], choices=[
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('cash', 'Cash'),
        ('other', 'Other')
    ])
    reference_number = StringField('Reference Number', validators=[Optional(), Length(max=100)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Payment')

class InvoiceSearchForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('all', 'All'),
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled')
    ])
    start_date = DateField('Start Date', validators=[Optional()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[Optional()], format='%Y-%m-%d')
    customer_id = SelectField('Customer', coerce=int, validators=[Optional()])
    submit = SubmitField('Search')

class InvoiceReportForm(FlaskForm):
    report_type = SelectField('Report Type', choices=[
        ('outstanding', 'Outstanding Invoices'),
        ('paid', 'Paid Invoices'),
        ('overdue', 'Overdue Invoices'),
        ('monthly', 'Monthly Summary')
    ])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Generate Report')
