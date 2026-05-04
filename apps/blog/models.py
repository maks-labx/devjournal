from django.db import models
from django.db.models import Sum
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from apps.services.utils import unique_slugify
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field

class PostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('author', 'category').filter(status='published')

class Post(models.Model):
    STATUS_OPTIONS = (
        ('published', 'Published'),
        ('draft', 'Draft')
    )

    title = models.CharField(verbose_name='Post title', max_length=255)
    slug = models.SlugField(verbose_name='URL', max_length=255, blank=True, unique=True)
    description = CKEditor5Field(config_name='extends', verbose_name='Brief description', max_length=500)
    text = CKEditor5Field(config_name='extends', verbose_name='Post content')
    category = TreeForeignKey(to='Category', on_delete=models.PROTECT, related_name='posts', verbose_name='Category')
    thumbnail = models.ImageField(default='default.jpg', verbose_name='Thumbnail image', blank=True, upload_to='images/thumbnails/%Y/%m/%d/', 
                                  validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'webp', 'jpeg', 'gif'))])
    status = models.CharField(choices=STATUS_OPTIONS, default='published', verbose_name='Post status', max_length=10)
    create = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    update = models.DateTimeField(auto_now=True, verbose_name='Last updated')
    author = models.ForeignKey(to=User, verbose_name='Author', on_delete=models.PROTECT, related_name='author_posts')
    updater = models.ForeignKey(to=User, verbose_name='Updater', on_delete=models.SET_NULL, null=True, related_name='updater_posts', blank=True)
    pinned = models.BooleanField(verbose_name='Pinned', default=False)

    objects = models.Manager()
    custom = PostManager()
    tags = TaggableManager()

    class Meta:
        db_table = 'blog_post'
        ordering = ['-pinned', '-create']
        indexes = [models.Index(fields=['-pinned', '-create', 'status'])]
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, self.title, self.slug)
        super().save(*args, **kwargs)

    def get_sum_rating(self):
        return self.ratings.aggregate(total=Sum("value"))["total"] or 0

class Category(MPTTModel):
    title = models.CharField(max_length=255, verbose_name='Category name')
    slug = models.SlugField(max_length=255, verbose_name='Category URL', blank=True, unique=True)
    description = models.TextField(verbose_name='Category description', max_length=300)
    parent = TreeForeignKey(to='self', on_delete = models.CASCADE, null=True, blank=True, db_index=True, related_name='children', verbose_name='Parent category')

    class MPTTMeta:
        order_insertion_by = ('title',)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        db_table='app_categories'

    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, self.title, self.slug)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post_by_category', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title
    
class Comment(MPTTModel):
    STATUS_OPTIONS = (
        ('published', 'Published'),
        ('draft', 'Draft')
    )

    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, verbose_name='Post', related_name='comments')
    author = models.ForeignKey(to=User, verbose_name='Comment author', on_delete=models.CASCADE, related_name='comments_author')
    content = models.TextField(verbose_name='Comment text', max_length=3000)
    time_create = models.DateTimeField(verbose_name='Created at', auto_now_add=True)
    time_update = models.DateTimeField(verbose_name='Updated at', auto_now=True)
    status = models.CharField(choices=STATUS_OPTIONS, default='published', verbose_name='Comment status', max_length=10)
    parent = TreeForeignKey(to='self', verbose_name='Parent comment', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    class MPTTMeta:
        order_insertion_by = ('-time_create',)

    class Meta:
        ordering = ['-time_create']
        indexes = [models.Index(fields=['post', 'status', '-time_create']),]
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f'{self.author}: {self.content[:50]}'
    
class Rating(models.Model):
    LIKE = 1
    DISLIKE = -1

    RATING_CHOICES = (
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
    )

    post = models.ForeignKey(to=Post, verbose_name='Post', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(to=User, verbose_name='User', on_delete=models.CASCADE, related_name='ratings')
    value = models.SmallIntegerField(verbose_name='Value', choices=RATING_CHOICES)
    time_create = models.DateTimeField(verbose_name='Created', auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "user"],
                name="unique_user_rating_per_post",
            )
        ]
        ordering = ('-time_create',)
        indexes = [
            models.Index(fields=["post", "value"]),
        ]
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'

    def __str__(self):
        return self.post.title
