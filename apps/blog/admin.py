from django.contrib import admin
from .models import Post, Category, Comment, Rating
from django_mptt_admin.admin import DjangoMpttAdmin

@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('title',)}

@admin.register(Comment)
class CommentAdminPage(DjangoMpttAdmin):
    pass

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    pass