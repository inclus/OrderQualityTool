from django.db.models import TextField
from django.forms import Textarea, Field
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.html import format_html


class TestDefinitionField(TextField):
    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length, 'widget': TestDefinitionWidget}
        defaults.update(kwargs)
        return super(TextField, self).formfield(**defaults)


class TestDefinitionWidget(Textarea):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        return format_html('<textarea id="asd" {}>\r\n{}</textarea>',
                           flatatt(final_attrs),
                           force_text(value))
