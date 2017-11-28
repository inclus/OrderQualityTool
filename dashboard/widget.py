from django.db.models import Field
from django.forms import Textarea
from django.template import loader
from django.utils import six
from django.utils.encoding import (
    smart_text,
)
from django.utils.safestring import mark_safe


class TestDefinitionWidget(Textarea):
    template_name = 'test_definition.html'

    def get_context(self, name, value, attrs=None):
        return {'widget': {
            'name': name,
            'value': value,
        }}

    def render(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class TestDefinitionField(Field):
    description = "Text"

    def get_internal_type(self):
        return "TextField"

    def to_python(self, value):
        if isinstance(value, six.string_types) or value is None:
            return value
        return smart_text(value)

    def get_prep_value(self, value):
        value = super(TestDefinitionField, self).get_prep_value(value)
        return self.to_python(value)

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length, 'widget': TestDefinitionWidget}
        defaults.update(kwargs)
        return super(TestDefinitionField, self).formfield(**defaults)
