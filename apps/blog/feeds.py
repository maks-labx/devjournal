from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Post

class LatestPostFeed(Feed):
    title = "My Django Blog - Latest Posts"
    link = "/feeds/"
    description = "New posts on my blog."

    def items(self):
        return Post.custom.order_by('-update')[:5]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.description
    
    def item_link(self, item):
        return item.get_absolute_url()