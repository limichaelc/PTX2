from django.db import models

class User(models.Model):
	netid = models.CharField(max_length = 8)
	name = models.CharField(max_length = 50)
	seller_rating = models.IntegerField()
	preferred_meetingplace = models.CharField(max_length = 50)

# Create your models here.

