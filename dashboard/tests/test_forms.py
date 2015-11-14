from unittest import TestCase
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from dashboard.forms import FileUploadForm

class FileUploadFormTestCase(TestCase):
    def get_fixture_path(self, name):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', name)
        return file_path

    def test_xls_file_is_required(self):
        wrong_file = self.get_fixture_path('wrong_file.txt')
        upload_file = open(wrong_file, 'rb')
        post_dict = {}
        file_dict = {'import_file': SimpleUploadedFile(upload_file.name, upload_file.read())}
        form = FileUploadForm(post_dict, file_dict)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'import_file': ['Unsupported file extension.']
        })

    def test_xls_file_is_valid(self):
        wrong_file = self.get_fixture_path('c.xlsx')
        upload_file = open(wrong_file, 'rb')
        post_dict = {}
        file_dict = {'import_file': SimpleUploadedFile(upload_file.name, upload_file.read())}
        form = FileUploadForm(post_dict, file_dict)
        self.assertTrue(form.is_valid())
