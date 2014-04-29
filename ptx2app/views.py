from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from ptx2app.models import *
from ptx2app.forms import *
from scraper import pagewriter, scrape
from django.http import HttpResponseRedirect
from django.shortcuts import redirect


def get_context(request):
    context = RequestContext(request)
    try:
        user = request.user
    except:
        HttpResponseRedirect("/login/")
    try:
        profile = request.user.get_profile()
    except:
        profile = Profile.objects.create(user = user)
        profile.save()
    books = Book.objects.all()
    transaction = Transaction.objects.all()
    form = SellBookForm()
    nums_by_course = {}
    for course in profile.course_list.all():
        current_course = []
        for book in profile.books_owned.all():
            if book.book in course.books.all():
                if book.book not in current_course:
                    current_course.append(book.book)
        for book in profile.books_selling.all():
            if book.book in course.books.all():
                if book.book not in current_course:
                    current_course.append(book.book)
        nums_by_course[course] = len(current_course)

    user_selling = []



    context_dict = {'user' : profile,
					'form'  : form,
					'books' : books,
                    'num_needed' : len(profile.books_needed.all()),
                    'num_owned' : len(profile.books_owned.all()),
                    'num_selling' : len(profile.books_selling.all()),
                    'num_total' : len(profile.books_needed.all())
                    + len(profile.books_owned.all())
                    + len(profile.books_selling.all()),
                    'nums_by_course' : nums_by_course,
                    'user_selling': Listing.objects.filter(owner = profile) }
    return context_dict

# Create your views here.
def index(request):

    context = RequestContext(request)
    
    if not request.user.is_authenticated():
        return redirect('/login/')
    context_dict = get_context(request)
    
    profile = context_dict['user']
    nums_by_course = {}
    for course in profile.course_list.all():
        num = 0
        for book in profile.books_owned.all():
            if course.books.all() == book:
                num += 1
        nums_by_course[course] = num

    context = get_context(request)


    return render_to_response('ptonptx2/bookshelf.html', context)

def bookpage(request, isbn):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    
    context_dict = get_context(request)
    book = Book.objects.get(isbn=isbn)
    listings = Listing.objects.filter(book__book__isbn = isbn)
    
    context_dict['listings'] = listings
    context_dict['book'] = book
    
    return render_to_response('ptonptx2/book_lookup.html', context_dict, context)
    

def about(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    
    return render_to_response('ptonptx2/about.html', context)

def sell_book(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
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
    if not request.user.is_authenticated():
        return redirect('/login/')
    if request.method == 'POST':
        form = AddCourseForm(request.POST)
        if form.is_valid():
            form.save(commit = True)

            return index(request)
        else:
            print form.errors
    else:
        form = AddCourseForm()

    return render_to_response('forms/newcourse.html', context_dict, context)
    
def profile(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
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
    
def history(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    transaction = Transaction.objects.all()
    past_transactions = []
    
    for instance in transaction:
        if profile == instance.buyer:
            past_transactions.append(instance)
        elif profile == instance.seller:
            past_transactions.append(instance)
        
    context_dict['history'] = past_transactions
    
    return render_to_response('ptonptx2/history.html', context_dict, context)

#def search_form(request):
 #   return render(request, 'nav.html')

def search(request):
    if request.GET['q']:
        message = 'You searched for: %r' % request.GET['q']
    else:
        message = 'You submitted an empty form.'
    return HttpResponse(message)

def selling(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    books_selling = profile.books_selling.objects.all()
    context_dict['selling'] = books_selling

    return render_to_response('ptonptx2/selling.html', context_dict, context)

def scrape(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    if request.method == 'POST':
        pagewriter.write('page.txt')
        scrape.scrape('page.txt')

    return render_to_response('ptonptx2/scrape.html', {'form': None}, context)
    
def coursepage(request, course_dpt, course_num):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    course = Course.objects.get(dept=course_dpt, num=course_num)
	
    books = course.books
	
    fields = Book._meta.fields
	
    context_dict = get_context(request)
    context_dict['course'] = course

	
    return render_to_response('ptonptx2/course_page.html', context_dict,
	                                                         context)
	                                                         
	                                                         
	
def buybook(request, isbn, listingid):
    context = RequestContext(request)
    
    if not request.user.is_authenticated():
        return redirect('/login/')
    
    context_dict = get_context(request)
	
    listing = Listing.objects.get(id=listingid)
	
    context_dict['listing'] = listing
	
    return render_to_response('ptonptx2/confirmpurchase.html', context_dict, context)
    
    
def confirmbuybook(request, isbn, listingid):
    context = RequestContext(request)
    
    if not request.user.is_authenticated():
        return redirect('/login/')
    
    context_dict = get_context(request)
	
    listing = Listing.objects.get(id=listingid)
    sellerprofile = listing.owner
	
    context_dict['listing'] = listing
    context_dict['sellerprofile'] = sellerprofile

    
    transaction = Transaction(buyer = context_dict['user'], seller=listing.owner, price=listing.price, book = listing.book)
    transaction.save()
	
    return render_to_response('ptonptx2/afterpurchase.html', context_dict, context)
