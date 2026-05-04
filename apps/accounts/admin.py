from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'slug')
    list_display_links = ('user', 'slug')
    search_fields = ("user__username", "user__email", "slug")
    list_filter = ("birth_date",)