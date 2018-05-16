import os

from django_webtest import WebTest
from webtest import Upload

from dashboard.models import DashboardUser


class UserImportViewTestCase(WebTest):

    def get_fixture_path(self, name):
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fixtures", name
        )
        return file_path

    def test_creates_or_updates_user(self):
        user = DashboardUser.objects.create_superuser("a@a.com", "secret")
        user_count = DashboardUser.objects.count()
        url = "/import/users/"
        import_page = self.app.get(url, user=user)
        form = import_page.form
        form["import_file"] = Upload(self.get_fixture_path("users.csv"))
        form.submit()
        self.assertEquals(DashboardUser.objects.count(), user_count + 5)
