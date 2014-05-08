from django.conf.urls import patterns, include, url
from ptx2app import views
from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ptx2.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # admin stuff
    url(r'^admin/scrape/$', 'ptx2app.views.scrape', name = 'scrape'),
    url(r'^admin/', include(admin.site.urls)),

    #everything else
    url(r'^$', RedirectView.as_view(url='/bookshelf/')),
	#url(r'^$', 'django_cas.views.login', {'next_page' : 'bookshelf'}), # RedirectView.as_view(url='/bookshelf/')),
	url(r'^bookshelf/', 'ptx2app.views.index'),
	url(r'^profile/', 'ptx2app.views.profile'),
    url(r'^history/', 'ptx2app.views.history'),
    #url(r'^markasowned/', 'ptx2app.views.markasowned'),
    url(r'^pending/$', 'ptx2app.views.pending'),
    #url(r'^pending/(?P<id>\d+)/', 'ptx2app.views.pendingtransaction'),
	url(r'^about/$', 'ptx2app.views.about', name = 'about'),
	url(r'^sellbook/', 'ptx2app.views.sell_book',  name = 'sell_book'),
	url(r'^(?P<isbn>\d+)/$', 'ptx2app.views.bookpage'),
	#url(r'^(?P<isbn>\d+)/sell/$', 'ptx2app.views.sellbook'),
	url(r'^courses/(?P<course_dpt>\w+)/(?P<course_num>\w+)/', 'ptx2app.views.coursepage'),
	url(r'^(?P<isbn>\d+)/(?P<listingid>\d+)/$', 'ptx2app.views.buybook'),
    url(r'^(?P<isbn>\d+)/(?P<listingid>\d+)/confirmed/$', 'ptx2app.views.confirmbuybook'),
    url(r'^confirm/$', 'ptx2app.views.confirmbuybook'),
    url(r'^help/$', 'ptx2app.views.help'),
    url(r'^faq/$', 'ptx2app.views.faq'),
    #url(r'^searchform/$', 'ptx2app.views.search_form'),
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
    #url(r'^sellbook/', 'ptx2app.views.sell_book', name = 'sell_book'),
    
	#url(r'^courses/(?P<dept>\w+)/(?P<num>\d+)/$', 'ptx2app.templates.coursepage'),


    #CAS
    url(r'^login/$', 'django_cas.views.login'),
    url(r'^logout/$', 'django_cas.views.logout'),
    url(r'^accounts/login', 'django_cas.views.login'),
    url(r'^accounts/logout', 'django_cas.views.logout'),
    #url(r'^index/$', 'django_cas.views.login', {'next_page' : ''}),
)
