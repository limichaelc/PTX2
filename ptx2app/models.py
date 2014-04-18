from django.db import models

# Create your models here.
class Author(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    def __unicode__(self):
        return self.last_name + self.first_name

class Course(models.Model):
    name = models.CharField(max_length = 100)
    dept = models.CharField(max_length = 3)
    num = models.IntegerField()
    year = models.IntegerField()
    TERMS = (
            ('F', 'Fall'),
            ('S', 'Spring')
    )
    term = models.CharField(max_length = 1, choices = TERMS)
    # readings = models.ManyToManyField('Reading', blank=true) # use name since class Reading isn't defined yet
    def __unicode__(self):
        return self.name + ' (' + self.dept + ' ' + self.num + ') ' + ' (' + self.term + ' ' + self.year + ') ' + self.bb_id


class Book(models.Model):
    isbn = models.CharField(max_length=13)
    isbn10 = models.CharField(max_length=10)
    title = models.CharField(max_length=100)
    edition = models.CharField(max_length = 20, blank=True)
    authors = models.ManyToManyField(Author)
    amazon_price = models.DecimalField(max_digits = 3, decimal_places = 2)
    labyrinth_price = models.DecimalField(max_digits = 3, decimal_places = 2)
    lowest_student_price = models.IntegerField()
    picture_link = models.CharField(max_length = 200)
    def __unicode__(self):
        return self.title

class PhysBook(models.Model):
    book = models.ForeignKey(Book)
    missing_cover = models.BooleanField()
    bent_corners = models.BooleanField()
    has_markings = models.BooleanField()
    has_scratches = models.BooleanField()
    has_missing_pages = models.BooleanField()
    has_creases = models.BooleanField()
    comment = models.CharField(max_length = 500)
    def __unicode__(self):
        return self.book.title

class Review(models.Model):
    on_time = models.BooleanField()
    right_price = models.BooleanField()
    as_advertised = models.BooleanField()

class User(models.Model):
    netid = models.CharField(max_length=8)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    preferred_meetingplace = models.CharField(max_length=500)
    reviews = models.ManyToManyField(Review)
    #prof_pic = models.FileField()
    books_needed = models.ManyToManyField('Reading')
    books_owned = models.ManyToManyField(PhysBook)
    books_selling = models.ManyToManyField('Listing')
    course_list = models.ManyToManyField(Course)
    def __unicode__(self):
        return self.netid

class Listing(models.Model):
    book = models.ForeignKey(PhysBook)
    owner = models.ForeignKey(User)
    SELL_STATUSES = (
        ('O', 'Currently offered'),
        ('P', 'Sale pending'),
    )
    sell_status = models.CharField(max_length=1, choices=SELL_STATUSES, default='O')
    price = models.DecimalField(max_digits = 3, decimal_places = 2)
    def __unicode__(self):
        return self.book.book.title + " for $" + str(self.price)

class Reading(models.Model):
    book = models.ForeignKey(Book)
    is_recommended = models.BooleanField()
    used_in = models.ManyToManyField(Course)
    def __unicode__(self):
        return self.book + ' (recommended: ' + self.is_recommended + ')'

class Transaction(models.Model):
    buyer = models.ForeignKey(User, related_name = "transcation_buyer")
    seller = models.ForeignKey(User, related_name = "transcation_seller")
    book = models.ForeignKey(PhysBook)
    price = models.DecimalField(max_digits = 3, decimal_places = 2)
