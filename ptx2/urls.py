from django.conf.urls import patterns, include, url
from ptx2.views import current_datetime, course_lookup, book_lookup

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ptx2.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^index/', 'ptx2app.views.index', name = 'index'),
	url(r'^$', 'ptx2app.views.index', name = 'index'),
	url(r'^time/$', current_datetime),
	url(r'^courses/(.{3})/(\d{3})/$', course_lookup),
	url(r'^book/', book_lookup),
)
