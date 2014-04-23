from django.conf.urls import patterns, include, url
from ptx2app import views
from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ptx2.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	(r'^$', RedirectView.as_view(url='/bookshelf/')),
	url(r'^bookshelf/', 'ptx2app.views.index'),
	url(r'^profile/', 'ptx2app.views.profile'),
	url(r'^about/$', 'ptx2app.views.about', name = 'about'),
	url(r'^sellbook/', 'ptx2app.views.sell_book',  name = 'sell_book'),
	url(r'^courses/?P<course_dpt>\w+/?P<course_num>\d+/', 'ptx2app.views.coursepage'),

    #url(r'^sellbook/', 'ptx2app.views.sell_book', name = 'sell_book'),
    
	#url(r'^courses/(?P<dept>\w+)/(?P<num>\d+)/$', 'ptx2app.templates.coursepage'),

    url(r'^scrape/', 'ptx2app.views.scrape', name = 'scrape'),

    #CAS
    url(r'^login/$', 'django_cas.views.login'),
    url(r'^logout/$', 'django_cas.views.logout'),
    url(r'^index/$', 'django_cas.views.login', {'next_page' : ''}),
)
