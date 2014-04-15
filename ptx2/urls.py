from django.conf.urls import patterns, include, url
from ptx2.views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ptx2.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^index/', 'ptx2app.views.index', name = 'index'),
	url(r'^$', 'ptx2app.views.index', name = 'index'),
	url(r'^courses/(.{3})/(\d{3})/$', course_lookup),
	url(r'^bookshelf/', bookshelf),
	url(r'^test/', sidebar),
)
