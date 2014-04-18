from django.contrib import admin
from ptx2app.models import Author, Course, Book, PhysBook, Review, User, Listing, Reading, Transaction

# Register your models here.
admin.site.register(Author)
admin.site.register(Course)
admin.site.register(Book)
admin.site.register(PhysBook)
admin.site.register(Review)
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Reading)
admin.site.register(Transaction)
