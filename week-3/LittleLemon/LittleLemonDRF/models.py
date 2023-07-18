from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Rating(models.Model):
    menuitem_id = models.SmallIntegerField()
    rating = models.SmallIntegerField()
    category = models.ForeignKey(User, on_delete=models.CASCADE)