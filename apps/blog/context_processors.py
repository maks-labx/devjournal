from .models import Category


def sidebar_categories(request):
    return {
        "sidebar_categories": Category.objects.all(),
    }