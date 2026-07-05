from django.test import Client, TestCase
from django.urls import reverse


class StoreSmokeTests(TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST="127.0.0.1")

    def test_homepage(self):
        response = self.client.get(reverse("store_home"))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get(reverse("store_login"))
        self.assertEqual(response.status_code, 200)

    def test_staff_login_redirects_to_shop_login(self):
        response = self.client.get(reverse("staff_login"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_healthz(self):
        response = self.client.get("/healthz/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")

    def test_protected_staff_requires_login(self):
        response = self.client.get(reverse("staff_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])
