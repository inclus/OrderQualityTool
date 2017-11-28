import os

from django.core.exceptions import ValidationError
from django.forms import Form, FileField, ChoiceField, ModelForm

from dashboard.helpers import generate_choices
from dashboard.models import FacilityTest
from dashboard.widget import TestDefinitionField


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

class MappingUploadForm(Form):
    import_file = FileField(validators=[validate_file_extension()])

class UserUploadForm(Form):
    import_file = FileField(validators=[validate_file_extension(['.csv'])])


class TestDefinitionForm(ModelForm):
    class Meta:
        model = FacilityTest
        fields = '__all__'

    add = TestDefinitionField('definition')