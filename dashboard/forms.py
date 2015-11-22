import os

from arrow import Arrow, now
from django.core.exceptions import ValidationError
from django.forms import Form, FileField, ChoiceField


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.xlsx', '.xls']
    if ext not in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


class CustomArrow(Arrow):
    @classmethod
    def _get_frames(cls, name):
        if name in cls._ATTRS:
            return name, '{0}s'.format(name), 1
        elif name in ['week', 'weeks']:
            return 'week', 'weeks', 1
        elif name in ['quarter', 'quarters']:
            return 'quarter', 'months', 3
        elif name in ['months=2']:
            return 'month', 'months', 2
        raise AttributeError()


def format_range(start, end):
    return "%s - %s %s" % (start.format('MMM'), end.format('MMM'), start.format('YYYY'))


def generate_cycles(start, end):
    return [format_range(s, e) for s, e in CustomArrow.span_range("months=2", start, end)]


def generate_choices():
    return [(s, s) for s in generate_cycles(now().replace(years=-2), now())]


class FileUploadForm(Form):
    import_file = FileField(validators=[validate_file_extension])
    cycle = ChoiceField(choices=generate_choices())
