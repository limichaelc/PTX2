from django.conf.urls import patterns, include, url
from ptx2app import views
from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # admin stuff
    url(r'^admin/scrape/$', 'ptx2app.views.scrape', name = 'scrape'),
    url(r'^admin/', include(admin.site.urls)),

    #everything else
    url(r'^$', RedirectView.as_view(url='/bookshelf/')),
	url(r'^bookshelf/', 'ptx2app.views.index'),
	url(r'^profile/', 'ptx2app.views.profile'),
    url(r'^history/', 'ptx2app.views.history'),
    url(r'^pending/$', 'ptx2app.views.pending'),
	url(r'^sellbook/', 'ptx2app.views.sell_book',  name = 'sell_book'),
	url(r'^(?P<isbn>\d+)/$', 'ptx2app.views.bookpage'),
	url(r'^courses/(?P<course_dpt>\w+)/(?P<course_num>\w+)/', 'ptx2app.views.coursepage'),
	url(r'^(?P<isbn>\d+)/(?P<listingid>\d+)/$', 'ptx2app.views.buybook'),
    url(r'^confirm/$', 'ptx2app.views.confirmbuybook'),
    url(r'^help/$', 'ptx2app.views.help'),
    url(r'^search/', 'ptx2app.views.search'),
    url(r'^searchcourses/', 'ptx2app.views.searchcourses'),
    url(r'^remove/', 'ptx2app.views.removecourse'),
    url(r'^markasowned/', 'ptx2app.views.markasowned'),
    url(r'^addtoneeded/', 'ptx2app.views.addtoneeded'),
    url(r'^removefromneeded/', 'ptx2app.views.removefromneeded'),
    url(r'^removefromselling/', 'ptx2app.views.removefromselling'),
    url(r'^removefromowned/', 'ptx2app.views.removefromowned'),
    url(r'^addcourse/', 'ptx2app.views.addcourse'),
    url(r'^remove_listing/$', 'ptx2app.views.remove_listing'),
    url(r'^buybook/$', 'ptx2app.views.buybook'),

    #CAS
    url(r'^login/$', 'django_cas.views.login'),
    url(r'^logout/$', 'django_cas.views.logout'),
    url(r'^accounts/login', 'django_cas.views.login'),
    url(r'^accounts/logout', 'django_cas.views.logout'),
)
