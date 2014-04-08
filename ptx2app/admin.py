from django.contrib import admin
from ptx2app.models import User, Book, Author, Department, Course, Listing, Reading

# Register your models here.
admin.site.register(User)
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Listing)
admin.site.register(Reading)
