from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib import messages
from ptx2app.models import *
from ptx2app.forms import *
from scraper import scrape as scrape_funcs
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.urlresolvers import resolve
import re
from operator import itemgetter

# get the context of this request
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
    form = SellBookForm() #this is not the right approach

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

    num_total = len(profile.books_needed.all()) + len(profile.books_owned.all()) + len(profile.books_selling.all())

    context_dict = {'user' : profile,
                    #'form'  : form,
                    'books' : books,
                    'num_needed' : len(profile.books_needed.all()),
                    'num_owned' : len(profile.books_owned.all()),
                    'num_selling' : len(profile.books_selling.all()),
                    'num_total' : num_total,
                    'num_pending' : len(Transaction.objects.filter(Q(buyer = profile)|Q(seller=profile), Q(buyerreview=None) | Q(sellerreview=None))),
                    'nums_by_course' : nums_by_course,
                    'user_selling': Listing.objects.filter(owner = profile),
                    'first_visit': len(profile.course_list.all()) == 0 and num_total == 0 }
    return context_dict

#the main bookshelf page
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

    contextdict = get_context(request)


    return render_to_response('ptonptx2/bookshelf.html', contextdict, context)

def bookpage(request, isbn):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    
    context_dict = get_context(request)
    book = Book.objects.get(isbn=isbn)
    listings = Listing.objects.filter(book__book__isbn = isbn)
    
    context_dict['listings'] = listings
    context_dict['book'] = book
    context_dict['courses'] = Course.objects.filter(books = book)
    
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
        listing = Listing()
        user = request.user.profile_set.get()
        book = Book.objects.get(pk = request.POST['bookpk'])
        price = int(request.POST['price'])

        #if there is already a physbook, use it. If not, check to see if the user has any of this book
        #marked as owned. If not, make a new physbook
        try:
            physbook = PhysBook.objects.get(pk = request.POST['pk'])
            user.books_owned.remove(physbook)
        except:
            try:
                physbook = user.books_owned.filter(book__pk = request.POST['bookpk'])[0]
                user.books_owned.remove(physbook)
            except IndexError:
                physbook = PhysBook()
                physbook.owner = user
                physbook.book = book
                physbook.save()

        #add book to user's list of books for sale
        user.books_selling.add(physbook)
        user.save()

        #set lowest student price
        lowstud = book.lowest_student_price
        if not lowstud or price < lowstud:
            book.lowest_student_price = price
            book.save()

        listing.book = physbook
        listing.owner = user
        listing.sell_status = 'O'
        listing.price = request.POST['price']
        listing.comment = request.POST['comment']
        listing.save()
        return HttpResponseRedirect('/bookshelf/')

    else:
        return HttpResponseRedirect("/bookshelf/")

    return render_to_response('forms/newlisting.html', context)

#remove the listing with the given id, return the book to the seller's owned books
def remove_listing(request, listingid):
    context = RequestContext(request)

    listing = Listing.objects.get(pk = listingid)
    owner = listing.owner
    physbook = listing.book
    owner.books_selling.remove(physbook)
    owner.books_owned.add(physbook)
    owner.save()

    listprice = listing.price
    listing.delete()

    #set lowest student price, if necessary
    book = physbook.book
    if book.lowest_student_price <= listprice:
        if not Listing.objects.filter(book__book__pk = book.pk):
            book.lowest_student_price = None
        else:
            book.lowest_student_price = 1000000
            for listing in Listing.objects.filter(book__book__pk = book.pk):
                print listing.price
                if listing.price < book.lowest_student_price:
                    book.lowest_student_price = listing.price
        book.save()

    return HttpResponseRedirect("/" + physbook.book.isbn + "/")

def profile(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance = profile)
        if form.is_valid():
            
            link = form.save()    
            return index(request)
        else:
            print form.errors
    else:
        form = ProfileForm(instance = profile)
    context_dict['form'] = form
        
    return render_to_response('ptonptx2/bookshelf.html', context_dict, context)
    
def history(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    transaction = Transaction.objects.all()
    past_transactions = []
    
    for instance in transaction:
        if (instance.buyerreview != None) & (instance.sellerreview != None):
            if profile == instance.buyer:
                past_transactions.append(instance)
            if profile == instance.seller:
                past_transactions.append(instance)        
    context_dict['history'] = past_transactions
    return render_to_response('ptonptx2/history.html', context_dict, context)

def searchcourses(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    finallist = []
    if request.method == 'POST':
        form = AddCourseForm(request.POST)
        if form.is_valid():
            newcourse = form.cleaned_data['course']
            newcourse = Course.objects.get(id=newcourse)
            books = newcourse.books.all()
            profile.course_list.add(newcourse)
            for book in books:
                if not book in profile.books_owned.all():
                    if not book in profile.books_selling.all():
                        profile.books_needed.add(book)
            profile.save()
        else:
            return HttpResponse("form error")
    if request.GET['q']:
        q = request.GET['q']
        for f in Course.objects.all():
            if q.upper().replace(" ", "") == (f.dept + f.num):
                finallist.append(f)
        if len(finallist) == 0:
            for f in Course.objects.all():
                if q == f.num:
                    finallist.append()
                elif q.upper().replace(" ", "") == f.dept:
                    finallist.append(f)
                elif re.search(q.upper().replace(" ",""), f.name.upper().replace(" ","")) != None:
                    finallist.append(f)
    
    sortedbydept = sorted(finallist, key=lambda course: course['dept'])
    sortedbydeptandnum = sorted(sortedbydept, key=lambda course: course['num'])
    context_dict = get_context(request)
    context_dict['query'] = q
    context_dict['course_dict'] = sortedbydeptandnum

    
    return render_to_response('ptonptx2/course_page_list.html', context_dict, context)

def addcourse(request):
    context = RequestContext(request)
    profile = request.user.get_profile()
    if request.POST:
        form = AddCourseForm(request.POST)
        if form.is_valid():
            newcourse = form.cleaned_data['course']
            newcourse = Course.objects.get(id=newcourse)
            books = newcourse.books.all()
            profile.course_list.add(newcourse)
            for book in books:
                if not book in profile.books_owned.all():
                    if not book in profile.books_selling.all():
                        profile.books_needed.add(book)
            profile.save()
            print request.path
            try:
                return HttpResponseRedirect(request.POST['prevpage'])
            except:
                return HttpResponseRedirect("/bookshelf")
        else:
            return HttpResponse("form error")


    else:
        return HttpResponseRedirect("/bookshelf")


def removecourse(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.GET['r']:
        r = request.GET['r']
        r = Course.objects.get(id=r)
        booklist = r.books.all()
        profile.course_list.remove(r)
        for book in profile.books_needed.all():
            if book in booklist:
                profile.books_needed.remove(book)
        profile.save()
    context_dict = get_context(request)
    context_dict['r'] = r.name
    context_dict['dept'] = r.dept
    context_dict['num'] = r.num
    context_dict['just_removed'] = True
    messages.success(request, "Course %s %s (%s) has been removed" % (r.dept, r.num, r.name))
    return HttpResponseRedirect("/bookshelf")
    #return render_to_response('ptonptx2/bookshelf.html', context_dict, context)

def markasowned(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.GET['m']:
        m = request.GET['m']
        m = Book.objects.get(id=m)
        profile.books_needed.remove(m)
        physbook = PhysBook()
        physbook.book = m
        physbook.owner = profile
        profile.books_owned.add(physbook)
        profile.save()
        context_dict['m'] = m.title
        context_dict['markedasowned'] = True
        messages.success(request, "Book %s has been marked as owned" % (m.title))
        return HttpResponseRedirect("/bookshelf")

def search(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.GET['q']:
        q = request.GET['q']
        context_dict['query'] = q
        if len(q) < 3:
            context_dict['too_short'] = True
            return render_to_response('ptonptx2/searcherrorpage.html', context_dict, context)
        q = q.upper().replace(" ", "")
        finallist = []
        thiscourse = None
        for f in Course.objects.all():
            if q.upper().replace(" ", "") == (f.dept + f.num):
                thiscourse = f
        if thiscourse != None:
            finallist = thiscourse.books.all()
            context_dict['book_dict'] = finallist
            return render_to_response('ptonptx2/booksearchpage.html', context_dict, context)
        for f in Book.objects.all():
            booktitle = f.title.upper().replace(" ", "")
            if re.search(q, booktitle) != None:
                finallist.append(f)
        if len(finallist) == 0:
            return render_to_response('ptonptx2/searcherrorpage.html', context_dict, context)
        context_dict['book_dict'] = sorted(finallist, key=lambda book: book['title'])
    else:
        return render_to_response('ptonptx2/searcherrorpage.html', context_dict, context)
    return render_to_response('ptonptx2/booksearchpage.html', context_dict, context)

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
        #pagewriter.write('page.txt')
        #scrape.scrape('page.txt')
        scrape_funcs.save()

    else:
        pass

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

def sellbook(request, isbn):
    context = RequestContext(request)
    
    if not request.user.is_authenticated():
        return redirect('/login/')
    
    context_dict = get_context(request)
    book = Book.objects.get(isbn=isbn)
    context_dict['book'] = book
    if request.method == 'POST':
        form = PhysBookForm(request.POST)
        if form.is_valid():
            
            form = form.save(commit=False)    
            form.book = book
            form.save()
            return setpricelisting(request, isbn, form.id)
        else:
            print form.errors
    else:
        form = PhysBookForm()
    context_dict['form'] = form
	
    return render_to_response('ptonptx2/sellbook.html', context_dict, context)
    
def setpricelisting(request, isbn, physbookid):
    context = RequestContext(request)
    
    if not request.user.is_authenticated():
        return redirect('/login/')
    
    context_dict = get_context(request)
    physbook = PhysBook.objects.get(id=physbookid)
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            
            form = form.save(commit=False)    
            form.book = physbook
            form.owner = request.user.get_profile()
            form.sell_status = 'O'
            form.save()
            return index(request)
        else:
            print form.errors
    else:
        form = ListingForm()
    context_dict['form'] = form
    context_dict['physbook'] = physbook
	
    return render_to_response('ptonptx2/setprice.html', context_dict, context)
    
    
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
    
def pendingtransaction(request, id):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    context_dict = get_context(request)
    context_dict['id'] = id

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():

            form = form.save()    
            transaction = Transaction.objects.get(id=id)
            if transaction.buyer == context_dict['user']:
                 transaction.buyerreview = form
            if transaction.seller == context_dict['user']:
                transaction.sellerreview = form
            transaction.save()
            return index(request)
        else:
            print form.errors
    else:
        form = ReviewForm()
    context_dict['form'] = form
        

    return render_to_response('ptonptx2/pendingtransaction.html', context_dict, context)
    
def pending(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    context_dict = get_context(request)
    
    transactions = Transaction.objects.filter(Q(buyer = context_dict['user'])|Q(seller=context_dict['user']), Q(buyerreview=None) | Q(sellerreview=None))
    
    context_dict['transactions'] = transactions
    
    return render_to_response('ptonptx2/pending.html', context_dict, context)
