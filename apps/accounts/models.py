from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from apps.services.utils import unique_slugify
from django.core.cache import cache

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    slug = models.SlugField(verbose_name='URL', max_length=255, blank=True, unique=True)
    avatar = models.ImageField(verbose_name='Avatar', upload_to='images/avatars/%Y/%m/%d/', default='images/avatars/default.png', blank=True, validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))])
    bio = models.TextField(max_length=500, blank=True, verbose_name='About yourself')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Date of birth')

    class Meta:
        ordering = ('user',)
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.user.username, self.slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return reverse('profile_detail', kwargs={'slug': self.slug})
    
@property
def is_online(self):
    cache_key = f'last-seen-{self.user.id}'
    last_seen = cache.get(cache_key)

    return bool(last_seen)
