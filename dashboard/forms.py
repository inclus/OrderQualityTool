import os

from django.core.exceptions import ValidationError
from django.forms import Form, FileField, ChoiceField

from dashboard.helpers import generate_choices


def validate_file_extension(valid_extensions=None):
    if valid_extensions is None:
        valid_extensions = ['.xlsx', '.xls']

    def validate(value):
        ext = os.path.splitext(value.name)[1]

        if ext not in valid_extensions:
            raise ValidationError(u'Unsupported file extension.')

    return validate


class FileUploadForm(Form):
    import_file = FileField(validators=[validate_file_extension()])
    cycle = ChoiceField(choices=generate_choices())


class UserUploadForm(Form):
    import_file = FileField(validators=[validate_file_extension(['.csv'])])
