from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect

class AuthorRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        self.object = self.get_object()

        if self.object.author != request.user and not request.user.is_staff:
            messages.info(request, "Only the author can edit this post!")
            return redirect("home")

        return super().dispatch(request, *args, **kwargs)