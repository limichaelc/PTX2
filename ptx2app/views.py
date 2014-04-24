from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from ptx2app.models import *
from ptx2app.forms import *
from scraper import pagewriter, scrape
from django.http import HttpResponseRedirect

# Create your views here.
def index(request):
    context = RequestContext(request)
    try:
        user = request.user
    except:
   	    HttpResponseRedirect('/login/')
    try:
        profile = request.user.get_profile()
    except:
        profile = Profile.objects.create(user = user)
        profile.save()
    books = Book.objects.all()
    form = SellBookForm()
    nums_by_course = {}
    for course in profile.course_list.all():
        nums_by_course[course] = len(profile.books_owned.get(course_list = course).all())

    context_dict = {'user' : profile,
					'form'  : form,
					'books' : books,
                    'num_needed' : len(profile.books_needed.all()),
                    'num_owned' : len(profile.books_owned.all()),
                    'num_selling' : len(profile.books_selling.all()),
                    'num_total' : len(profile.books_needed.all())
                    + len(profile.books_owned.all())
                    + len(profile.books_selling.all()),
                    'nums_by_course' : nums_by_course  }

    return render_to_response('ptonptx2/bookshelf.html', context_dict, context)

def about(request):
    context = RequestContext(request)
    
    return render_to_response('ptonptx2/about.html', context)

def sell_book(request):
    context = RequestContext(request)

    if request.method == 'POST':
        print "haha"
        form = SellBookForm(request.POST)
        if form.is_valid():
            form.save(commit = True)
            
            return index(request)
        else:
            print form.errors
    else:
        form = SellBookForm()

    return render_to_response('forms/newlisting.html', {'form': form}, context)

def add_course(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = AddCourseForm(request.POST)
        if form.is_valid():
            form.save(commit = True)

            return index(request)
        else:
            print form.errors
    else:
        form = AddCourseForm()

    return render_to_response('ptonptx2/bookshelf.html', context_dict, context)
    
def profile(request):
    context = RequestContext(request)
    profile = request.user.get_profile()

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance = profile)
        if form.is_valid():
        	
            link = form.save()    
            return index(request)
        else:
            print form.errors
    else:
        form = ProfileForm(instance = profile)
        
    return render_to_response('forms/newprofile.html', {'form': form}, context)
    
def scrape(request):
    context = RequestContext(request)

    if request.method == 'POST':
        pagewriter.write('page.txt')
        scrape.scrape('page.txt')

    return render_to_response('ptonptx2/scrape.html', {'form': None}, context)
    
def coursepage(request, course_dpt, course_num):
	context = RequestContext(request)
	
	course = Course.objects.get(dept=course_dpt, num=course_num)
	
	books = course.books
	
	fields = Book._meta.fields

	
	return render_to_response('ptonptx2/course_page.html', {'course': course, 
	                                                        'fields': fields},
	                                                         context)
	
	
	
