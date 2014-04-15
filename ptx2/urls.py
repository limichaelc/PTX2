from django.conf.urls import patterns, include, url
from ptx2.views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ptx2.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^$', 'ptx2app.views.index', name = 'index'),
<<<<<<< HEAD
	url(r'^courses/(.{3})/(\d{3})/$', course_lookup),
	url(r'^bookshelf/', bookshelf),
	url(r'^test/', sidebar),
=======
	url(r'^about/$', 'ptx2app.views.about', name = 'about'),
	url(r'^courses/(?P<dept>\w+)/(?P<num>\d+)/$', 'ptx2app.templates.coursepage'),
	url(r'^book/', book_lookup),
	url(r'^*/sellbook/', 'ptx2app.views.sell_book', name = 'sell_book'),
>>>>>>> FETCH_HEAD
)
