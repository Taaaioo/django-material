import json
import pytz

from datetime import datetime
from django import forms
from django_webtest import WebTest
from django.core.exceptions import ValidationError
from . import build_test_urls


def validate_xxi_century(value):
    utc = pytz.timezone("UTC")
    if value > datetime(2100, 1, 1, tzinfo=utc) or value < datetime(2000, 1, 1, tzinfo=utc):
        raise ValidationError('Date should be in XXI century')


class SplitDateTimeForm(forms.Form):
    test_field = forms.SplitDateTimeField(
        validators=[validate_xxi_century],
        widget=forms.SplitDateTimeWidget(attrs={'data-test': 'Test Attr'}))


class Test(WebTest):
    default_form = SplitDateTimeForm
    urls = 'tests.integration.tests.test_splitdatetime'

    def test_default_usecase(self):
        page = self.app.get(self.test_default_usecase.url)

        self.assertIn('id="id_test_field_container"', page.body.decode('utf-8'))
        self.assertIn('id="id_test_field_0"', page.body.decode('utf-8'))
        self.assertIn('id="id_test_field_1"', page.body.decode('utf-8'))
        self.assertIn('data-test="Test Attr"', page.body.decode('utf-8'))

        form = page.form
        self.assertIn('test_field_0', form.fields)
        self.assertIn('test_field_1', form.fields)

        form['test_field_0'] = '2012-01-31'
        form['test_field_1'] = '12:34'
        response = json.loads(form.submit().body.decode('utf-8'))

        self.assertIn('cleaned_data', response)
        self.assertIn('test_field', response['cleaned_data'])
        self.assertEquals('2012-01-31T12:34:00Z', response['cleaned_data']['test_field'])

    def test_missing_value_error(self):
        form = self.app.get(self.test_missing_value_error.url).form
        response = form.submit()

        self.assertIn('has-error', response.body.decode('utf-8'))
        self.assertIn('This field is required.', response.body.decode('utf-8'))

    def test_render_with_value(self):
        form = self.app.get(self.test_render_with_value.url).form
        form['test_field_0'] = '3000-01-31'
        form['test_field_1'] = '12:34'
        response = form.submit()

        self.assertIn('value="3000-01-31"', response.body.decode('utf-8'))
        self.assertIn('value="12:34"', response.body.decode('utf-8'))
        self.assertIn('Date should be in XXI century', response.body.decode('utf-8'))

    def test_part_group_class(self):
        page = self.app.get(self.test_part_group_class.url)

        self.assertIn('class="input-field col s12 yellow"', page.body.decode('utf-8'))

    test_part_group_class.template = '''
        {% form %}
             {% part form.test_field group_class %}input-field col s12 yellow{% endpart %}
        {% endform %}
    '''

    def test_part_add_group_class(self):
        page = self.app.get(self.test_part_add_group_class.url)

        self.assertIn('class="input-field col s6 required deep-purple lighten-5"', page.body.decode('utf-8'))

    test_part_add_group_class.template = '''
        {% form %}
             {% part form.test_field add_group_class %}deep-purple lighten-5{% endpart %}
        {% endform %}
    '''

    def test_part_prefix(self):
        response = self.app.get(self.test_part_prefix.url)
        self.assertIn('<i class="mdi-communication-email prefix"></i>', response.body.decode('utf-8'))

    test_part_prefix.template = '''
        {% form %}
             {% part form.test_field prefix %}<i class="mdi-communication-email prefix"></i>{% endpart %}
        {% endform %}
    '''

    def test_part_add_control_class(self):
        response = self.app.get(self.test_part_add_control_class.url)
        self.assertIn('class="orange"', response.body.decode('utf-8'))

    test_part_add_control_class.template = '''
        {% form %}
             {% part form.test_field add_control_class %}orange{% endpart %}
        {% endform %}
    '''

    def test_part_label(self):
        response = self.app.get(self.test_part_label.url)
        self.assertIn('<label for="id_test_field">My label</label>', response.body.decode('utf-8'))

    test_part_label.template = '''
        {% form %}
             {% part form.test_field label %}<label for="id_test_field">My label</label>{% endpart %}
        {% endform %}
    '''

    def test_part_add_label_class(self):
        response = self.app.get(self.test_part_add_label_class.url)
        self.assertIn('<label for="id_test_field_0" class="green-text">Test field</label>', response.body.decode('utf-8'))

    test_part_add_label_class.template = '''
        {% form %}
             {% part form.test_field add_label_class %}green-text{% endpart %}
        {% endform %}
    '''

    def test_part_help_text(self):
        response = self.app.get(self.test_part_help_text.url)
        self.assertIn('<small class="help-block">My help</small>', response.body.decode('utf-8'))

    test_part_help_text.template = '''
        {% form %}
             {% part form.test_field help_text %}<small class="help-block">My help</small>{% endpart %}
        {% endform %}
    '''

    def test_part_errors(self):
        response = self.app.get(self.test_part_errors.url)
        self.assertIn('<div class="errors"><small class="error">My Error</small></div>', response.body.decode('utf-8'))

    test_part_errors.template = '''
        {% form %}
             {% part form.test_field  errors%}<div class="errors"><small class="error">My Error</small></div>{% endpart %}
        {% endform %}
    '''

urlpatterns = build_test_urls(Test)
