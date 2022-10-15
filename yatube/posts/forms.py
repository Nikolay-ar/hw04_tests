from .models import Post
from django.forms import ModelForm


class PostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = "Группа не выбрана"

    class Meta:
        model = Post
        fields = ('text', 'group')
