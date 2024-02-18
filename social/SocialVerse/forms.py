from django import forms
from .models import User, Post, Comment, PostImage

class Search(forms.Form):
    query = forms.CharField(label="Search",
                            max_length=64,
                            widget=forms.TextInput(attrs=
                                                    {'placeholder': 'Search for anything',
                                                    'style': 'width: 380px'
                                                    }
                                                  )
                            )

class CommentForm(forms.ModelForm):
    text = forms.CharField(label='Comment', widget=forms.Textarea(attrs={'class': 'expandable-textarea', 'rows': 3, 'cols': 54}))
    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    caption = forms.CharField(label='Caption', widget=forms.Textarea(attrs={'rows': 4}))
    image = forms.ImageField(label="Image(s)")

    class Meta:
        model = Post
        fields = ('caption','image')
    
    def save(self, commit=True):
        post = super().save(commit=commit)
        images = self.cleaned_data.get('images')
        if images:
            for image in images:
                PostImage.objects.create(post=post, image=image)

        return post

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False




class UserForm(forms.ModelForm):
    prof_pic = forms.ImageField(label="Profile Picture", required=False)

    class Meta:
        model = User
        fields = ('prof_pic',)