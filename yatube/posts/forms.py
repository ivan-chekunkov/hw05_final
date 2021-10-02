from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            'image'
        )
        widgets = {
            'text': forms.Textarea(
                attrs={
                    'name': "text",
                    'cols': "40",
                    'rows': "10",
                    'class': "form-control",
                    'id': "id_text"
                }
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'text',
        )
        widgets = {
            'text': forms.Textarea(
                attrs={
                    'name': "text",
                    'cols': "40",
                    'rows': "2",
                    'class': "form-control",
                    'id': "id_text"
                }
            ),
        }
