from django.db import models

# Create your models here.
class Author(models.Model):
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=40)

class Department(models.Model):
	subject_code = models.CharField(max_length=3)

class Course(models.Model):
	department = models.ManyToManyField(Department)
	course_code = models.IntegerField()

class Book(models.Model):
	isbn = models.CharField(max_length=13)
	isbn10 = models.CharField(max_length=10)
	title = models.CharField(max_length=100)
	edition = models.IntegerField()
	authors = models.ManyToManyField(Author)
	course_used_in = models.ForeignKey(Course)
	amazon_price = models.DecimalField()
	labyrinth_price = models.DecimalField()
	lowest_studentprice = models.DecimalField()

class User(models.Model):
	netid = models.CharField(max_length=8)
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=40)
	preferred_meetingplace = models.CharField(max_length=500)
	seller_rating = models.DecimalField()

class Listing(models.Model):
	book_id = models.IntegerField()
	book = models.ForeignKey(Book)
	owner = models.ForeignKey(User)
	SELL_STATUSES = (
		('O', 'Currently offered'),
		('P', 'Sale pending'),
		('S', 'Sold'),
		('C', 'Cancelled'),
	)
	sell_status = models.CharField(max_length=1, choices=SELL_STATUSES, default='O')
	condition = models.IntegerField()
	price = models.DecimalField()
	comment = models.CharField(max_length=500)

class Reading(models.Model):
	book = models.ForeignKey(Book)
	course = models.ForeignKey(Course)
	is_recommended = models.BooleanField()

class Transaction(models.Model):
	tx_id = models.IntegerField()
	buyer = models.ForeignKey(User)
	seller = models.ForeignKey(User)
	book = models.ForeignKey(Book)
	paid = models.DecimalField()
	SELL_STATUSES = (
		('O', 'Currently offered'),
		('P', 'Sale pending'),
		('S', 'Sold'),
		('C', 'Cancelled'),
	)
	sell_status = models.CharField(max_length=1, choices=SELL_STATUSES, default='O')
