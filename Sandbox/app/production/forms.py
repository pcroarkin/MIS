from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, DateField, DecimalField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional, NumberRange
from app.models import JobStatus

class UpdateJobStatusForm(FlaskForm):
    status = SelectField('Status', validators=[DataRequired()], 
                         choices=[(status.name, status.value) for status in JobStatus])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Update Status')

class ProductionScheduleForm(FlaskForm):
    start_date = DateField('Start Date', validators=[Optional()], format='%Y-%m-%d')
    completion_date = DateField('Expected Completion Date', validators=[Optional()], format='%Y-%m-%d')
    estimated_hours = DecimalField('Estimated Hours', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Production Notes', validators=[Optional()])
    submit = SubmitField('Schedule Job')

class JobCompletionForm(FlaskForm):
    actual_hours = DecimalField('Actual Hours Spent', validators=[DataRequired(), NumberRange(min=0)])
    completion_date = DateField('Completion Date', validators=[DataRequired()], format='%Y-%m-%d')
    notes = TextAreaField('Completion Notes', validators=[Optional()])
    submit = SubmitField('Mark as Completed')

class MaterialUsageForm(FlaskForm):
    material_id = SelectField('Material', coerce=int, validators=[DataRequired()])
    quantity = DecimalField('Quantity Used', validators=[DataRequired(), NumberRange(min=0)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Usage')

class QualityCheckForm(FlaskForm):
    passed = SelectField('Quality Check Result', choices=[
        ('pass', 'Pass - Meets Quality Standards'), 
        ('fail', 'Fail - Requires Rework')
    ], validators=[DataRequired()])
    notes = TextAreaField('Quality Check Notes', validators=[DataRequired()])
    submit = SubmitField('Submit Quality Check')

class ProductionReportForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    status = SelectField('Job Status', choices=[
        ('all', 'All Statuses'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ])
    submit = SubmitField('Generate Report')
