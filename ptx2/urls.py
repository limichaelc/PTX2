from django.conf.urls import patterns, include, url
from ptx2.views import current_datetime, course_lookup, book_lookup

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ptx2.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^$', 'ptx2app.views.index', name = 'index'),
	url(r'^about/$', 'ptx2app.views.about', name = 'about'),
	url(r'^courses/(?P<dept>\w+)/(?P<num>\d+)/$', 'ptx2app.templates.coursepage'),
	url(r'^book/', book_lookup),
	url(r'^*/sellbook/', 'ptx2app.views.sell_book', name = 'sell_book'),
)
