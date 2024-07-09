'''
Defines the NonNegativeFloat validator, which checks if a field's value is a non-negative float.
'''

from wtforms import ValidationError

def NonNegativeFloat(form, field):
    try:
        value = float(field.data)
        if value < 0:
            raise ValueError
    except ValueError:
        raise ValidationError('Field must be a non-negative float')
