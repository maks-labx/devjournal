from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Post, Category, Rating
from .forms import PostCreateForm, PostUpdateForm, CommentCreateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from ..services.mixins import AuthorRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.formats import date_format
from django.utils.timezone import localtime
from taggit.models import Tag
from django.db.models import Q
from django.urls import reverse_lazy

class PostListView(ListView):
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 4
    queryset = Post.custom.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Main page'
        page = context['page_obj']
        context['paginator_range'] = page.paginator.get_elided_page_range(page.number)
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = Post.objects.select_related("author", "category")

        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return queryset

            return queryset.filter(
                Q(status="published") |
                Q(status="draft", author=self.request.user)
            )

        return queryset.filter(status="published")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['form'] = CommentCreateForm
        return context

class PostFromCategory(ListView):
    template_name='blog/post_list.html'
    context_object_name = 'posts'
    category = None
    paginate_by = 4

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        queryset = Post.custom.filter(category=self.category)
        if not queryset:
            sub_cat = Category.objects.filter(parent=self.category)
            queryset = Post.custom.filter(category__in=sub_cat)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Записи из категории: {self.category.title}'
        page = context['page_obj']
        context['paginator_range'] = page.paginator.get_elided_page_range(page.number)
        return context
    
class MyPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/my_posts.html"
    context_object_name = "posts"
    paginate_by = 8
    login_url = 'login'

    def get_queryset(self):
        return (
            Post.objects
            .select_related("author", "category")
            .filter(author=self.request.user)
            .order_by("-create")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "My posts"

        page = context["page_obj"]
        context["paginator_range"] = page.paginator.get_elided_page_range(page.number)

        return context
    
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_create.html'
    form_class = PostCreateForm
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add post'
        return context
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
class PostUpdateView(AuthorRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Post
    template_name = 'blog/post_update.html'
    context_object_name = 'post'
    form_class = PostUpdateForm
    login_url = 'login'
    success_message = 'Post updated successfully!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update post: {self.object.title}'
        return context
    
    def form_valid(self, form):
        form.instance.updater = self.request.user
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
    
class PostDeleteView(AuthorRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    context_object_name = "post"
    success_url = reverse_lazy("my_posts")
    login_url = "login"
    success_message = "Post deleted successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Delete post: {self.object.title}"
        return context
    
class CommentCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentCreateForm
    login_url = 'login'

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)
    
    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post_id = self.kwargs.get('pk')
        comment.author = self.request.user
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.id,
                'author': comment.author.username,
                'parent_id': comment.parent_id,
                'time_create': date_format(
                    localtime(comment.time_create),
                    format='DATETIME_FORMAT',
                    use_l10n=True,
                ),
                'avatar': comment.author.profile.avatar.url,
                'content': comment.content,
                'get_absolute_url': comment.author.profile.get_absolute_url()
            }, status=200)
        
        return redirect(comment.post.get_absolute_url())
    
    def handle_no_permission(self):
        if self.is_ajax():
            return JsonResponse(
                {"error": "You need to sign in to add comments."},
                status=403,
            )
        return super().handle_no_permission()
    
class PostByTagListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 4
    tag = None

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["tag"])
        queryset = Post.custom.filter(tags__slug=self.tag.slug)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Posts by tag: {self.tag.name}'

        page = context['page_obj']
        context['paginator_range'] = page.paginator.get_elided_page_range(page.number)

        return context
    
class RatingCreateView(LoginRequiredMixin, View):
    model = Rating

    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')

        try:
            value = int(request.POST.get('value'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid rating value.'}, status=400)
        
        if value not in (Rating.LIKE, Rating.DISLIKE):
            return JsonResponse({'error': 'Invalid rating value.'}, status=400)
        
        post = get_object_or_404(Post, id=post_id)

        rating, created = self.model.objects.get_or_create(
            post=post,
            user=request.user,
            defaults={'value': value},
        )

        if not created:
            if rating.value == value:
                rating.delete()
            else:
                rating.value = value
                rating.save()

        return JsonResponse({'rating_sum': post.get_sum_rating()})
    
def tr_handler404(request, exception):
    return render(request=request, template_name='errors/error_page.html', status=404, context={
        'title': 'Page Not Found (404)',
        'error_message': 'Sorry, the page you’re looking for was not found or has been moved.',
    })

def tr_handler500(request):
    return render(request=request, template_name='errors/error_page.html', status=500, context={
        'title': 'Server Error (500)',
        'error_message': 'Something went wrong on our end. Please return to the homepage. We’ve been notified and are working on a fix.',
    })

def tr_handler403(request, exception):
    return render(request=request, template_name='errors/error_page.html', status=403, context={
        'title': 'Access Denied (403)',
        'error_message': 'You don’t have permission to access this page.',
    })
