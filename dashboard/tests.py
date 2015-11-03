from django_webtest import WebTest

class HomeViewTestCase(WebTest):
    def test_correct_template(self):
        home = self.app.get('/')
        self.assertTemplateUsed(home, "home.html")
