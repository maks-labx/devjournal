from django.contrib import admin
from .models import Post, Category, Comment, Rating
from django_mptt_admin.admin import DjangoMpttAdmin

@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title",)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "status", "pinned", "create", "update")
    list_filter = ("status", "pinned", "category", "create")
    search_fields = ("title", "description", "text")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author", "updater", "category")
    date_hierarchy = "create"

@admin.register(Comment)
class CommentAdminPage(DjangoMpttAdmin):
    list_display = ("author", "post", "status", "time_create")
    list_filter = ("status", "time_create")
    search_fields = ("content", "author__username", "post__title")

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "value", "time_create")
    list_filter = ("value", "time_create")
    search_fields = ("post__title", "user__username")
    autocomplete_fields = ("post", "user")