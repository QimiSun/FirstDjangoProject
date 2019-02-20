from django.db import models

# Create your models here.

class awehomeinfos(models.Model):
    web_site = models.CharField(max_length=10)
    refer = models.CharField(max_length=100)
    awehome = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    time_now = models.DateTimeField(auto_now_add=True,)

