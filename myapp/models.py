from django.db import models

# Create your models here.

class ImageModel(models.Model):
    image = models.ImageField(upload_to='images/')  # 'images/' is the directory where the images will be uploaded

    def __str__(self):
        return self.image.name


class WordModel(models.Model):
    word = models.CharField(max_length=100)

    def __str__(self):
        return self.word
