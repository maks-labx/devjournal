from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from apps.accounts.models import Profile


class AccountsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="author",
            password="password123"
        )

        self.profile = self.user.profile
        self.profile.bio = "Test bio"
        self.profile.save()

    def test_profile_is_created_for_user(self):
        self.assertTrue(
            Profile.objects.filter(user=self.user).exists()
        )

        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.bio, "Test bio")
        self.assertTrue(self.profile.slug)

    def test_profile_get_absolute_url(self):
        expected_url = reverse(
            "profile_detail",
            kwargs={"slug": self.profile.slug}
        )

        self.assertEqual(self.profile.get_absolute_url(), expected_url)

    def test_profile_detail_page_opens(self):
        url = reverse(
            "profile_detail",
            kwargs={"slug": self.profile.slug}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_cannot_access_profile_edit_page(self):
        url = reverse("profile_edit")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_access_profile_edit_page(self):
        self.client.login(username="author", password="password123")

        url = reverse("profile_edit")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)