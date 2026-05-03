from django import forms
from .models import Post, Comment
from django_ckeditor_5.widgets import CKEditor5Widget

class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'category', 'description', 'text', 'thumbnail', 'status')

        widgets = {
            'description': CKEditor5Widget(config_name='extends'),
            'text': CKEditor5Widget(config_name='extends'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ('description', 'text'):
                self.fields[field].widget.attrs.update({
                    'class': 'form-control',
                    'autocomplete': 'off'
                      })

class PostUpdateForm(PostCreateForm):
    class Meta:
        model = Post
        fields = PostCreateForm.Meta.fields + ('pinned',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pinned'].widget.attrs.update({
            'class': 'form-check-input'
        })

class CommentCreateForm(forms.ModelForm):
    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)
    content = forms.CharField(label='', widget=forms.Textarea(attrs={'col': 30, 'rows': 5, 'placeholder': 'Comments', 'class': 'form-control'}))

    class Meta:
        model = Comment
        fields = ('content',)