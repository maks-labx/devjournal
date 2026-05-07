from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from apps.blog.models import Category, Post, Rating
from django.db import IntegrityError

class BlogTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            password='password123'
        )

        self.category = Category.objects.create(
            title='Django',
            description='Category for Django posts'
        )

        self.post = Post.objects.create(
            title='First post',
            description='Short test description',
            text='Full test post text',
            category=self.category,
            author=self.user,
            status='published',
        )

        self.post.tags.add('django')

        self.draft_post = Post.objects.create(
            title="Draft post",
            description="Draft test description",
            text="Draft test post text",
            category=self.category,
            author=self.user,
            status="draft",
        )

    def test_post_can_be_created(self):
        self.assertTrue(
            Post.objects.filter(
                title="First post",
                status="published",
                author=self.user,
                category=self.category,
            ).exists()
        )
        self.assertEqual(self.post.title, 'First post')
        self.assertEqual(self.post.description, 'Short test description')
        self.assertEqual(self.post.text, 'Full test post text')
        self.assertEqual(self.post.category, self.category)
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.status, 'published')
        self.assertTrue(self.post.slug)

    def test_post_get_absolute_url(self):
        expected_url = reverse(
            'post_detail',
            kwargs={'slug': self.post.slug}
        )

        self.assertEqual(self.post.get_absolute_url(), expected_url)

    def test_category_get_absolute_url(self):
        expected_url = reverse(
            'post_by_category',
            kwargs={'slug': self.category.slug}
        )

        self.assertEqual(self.category.get_absolute_url(), expected_url)

    def test_user_cannot_rate_same_post_twice(self):
        Rating.objects.create(
            post=self.post,
            user=self.user,
            value=Rating.LIKE,
        )

        with self.assertRaises(IntegrityError):
            Rating.objects.create(
                post=self.post,
                user=self.user,
                value=Rating.DISLIKE,
            )

    def test_published_post_detail_page_opens(self):
        url = reverse("post_detail", kwargs={"slug": self.post.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_home_page_opens(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_category_page_opens(self):
        url = reverse("post_by_category", kwargs={"slug": self.category.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_cannot_access_post_create_page(self):
        url = reverse("post_create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_cannot_access_my_posts_page(self):
        url = reverse("my_posts")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_access_post_create_page(self):
        self.client.login(username="author", password="password123")
        url = reverse("post_create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_in_user_can_access_my_posts_page(self):
        self.client.login(username="author", password="password123")
        url = reverse("my_posts")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_author_can_access_post_update_page(self):
        self.client.login(username="author", password="password123")
        url = reverse("post_update", kwargs={"slug": self.post.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_author_can_access_post_delete_page(self):
        self.client.login(username="author", password="password123")
        url = reverse("post_delete", kwargs={"slug": self.post.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_non_author_cannot_access_post_update_page(self):
        other_user = User.objects.create_user(
            username="other_user",
            password="password123"
        )
        self.client.login(username="other_user", password="password123")
        url = reverse("post_update", kwargs={"slug": self.post.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_non_author_cannot_access_post_delete_page(self):
        other_user = User.objects.create_user(
            username="other_user",
            password="password123"
        )
        self.client.login(username="other_user", password="password123")
        url = reverse("post_delete", kwargs={"slug": self.post.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_anonymous_user_cannot_access_draft_post_detail_page(self):
        url = reverse("post_detail", kwargs={"slug": self.draft_post.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_author_can_access_own_draft_post_detail_page(self):
        self.client.login(username="author", password="password123")
        url = reverse("post_detail", kwargs={"slug": self.draft_post.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_tag_page_opens(self):
        url = reverse("post_by_tags", kwargs={"tag": "django"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_tag_page_contains_post_with_tag(self):
        url = reverse("post_by_tags", kwargs={"tag": "django"})
        response = self.client.get(url)
        self.assertContains(response, "First post")

    def test_logged_in_user_can_like_post(self):
        self.client.login(username="author", password="password123")

        url = reverse("rating")
        response = self.client.post(
            url,
            {
                "post_id": self.post.id,
                "value": Rating.LIKE,
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["rating_sum"], 1)
        self.assertEqual(Rating.objects.count(), 1)

    def test_repeated_same_rating_removes_rating(self):
        self.client.login(username="author", password="password123")
        url = reverse("rating")
        self.client.post(
            url,
            {
                "post_id": self.post.id,
                "value": Rating.LIKE,
            }
        )

        response = self.client.post(
            url,
            {
                "post_id": self.post.id,
                "value": Rating.LIKE,
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["rating_sum"], 0)
        self.assertEqual(Rating.objects.count(), 0)