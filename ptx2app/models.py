from django.db import models

class User(models.Model):
	netid = models.CharField(max_length = 8)
	name = models.CharField(max_length = 50)
	seller_rating = models.IntegerField()
	preferred_meetingplace = models.CharField(max_length = 50)

class Book(models.Model):
	title = models.CharField(max_length = 100)
	author = models.CharField(max_length = 50)
	edition = models.IntegerField()
	isbn = models.CharField(max_length = 30)
	isbn10 = models.CharField(max_length = 30)
	course_usedin = models.IntegerField();
	amazon_price = models.DecimalField(max_digits = 5, decimal_places = 			2)
	labyrinth_price = models.DecimalField(max_digits = 5, decimal_places 			= 2)
	lowest_studentprice = models.DecimalField(max_digits=5,decimal_places 	= 2)

# Create your models here.

