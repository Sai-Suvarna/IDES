from django import forms
from .models import ImageModel
from .models import WordModel

class ImageForm(forms.ModelForm):
    class Meta:
        model = ImageModel
        fields = [ 'image']


class WordForm(forms.ModelForm):
    class Meta:
        model = WordModel
        fields = ['word']
