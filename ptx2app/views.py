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
from django_cas.decorators import login_required
from helpers import set_lowest_price
from django.core.mail import send_mail

# get the context of this request
def get_context(request):
    context = RequestContext(request)
    first=False
    try:
        user = request.user
    except:
        HttpResponseRedirect("/login/")
    try:
        #profile = request.user.get_profile()
        profile = request.user.profile_set.get()
    except:
        profile = Profile.objects.create(user = user)
        #messages.success(request, 
            #'<strong>Welcome!</strong> This appears to be your first visit. You can get started by <a href="#" data-toggle="modal" data-target="#newcoursemodal" class="alert-link">adding a new course</a>.')
        first=True
        profile.save()
    books = Book.objects.all()
    transaction = Transaction.objects.all()

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
                    'books' : books,
                    'num_needed' : len(profile.books_needed.all()),
                    'num_owned' : len(profile.books_owned.all()),
                    'num_selling' : len(profile.books_selling.all()),
                    'num_total' : num_total,
                    'num_pending' : len(Transaction.objects.filter(Q(buyer = profile)|Q(seller=profile), Q(buyerreview=None) | Q(sellerreview=None))),
                    'nums_by_course' : nums_by_course,
                    'user_selling': Listing.objects.filter(owner = profile),
                    'first_visit': first,
                    }
    print first 
    return context_dict

#the main bookshelf page
@login_required
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

    #contextdict = get_context(request)


    return render_to_response('ptonptx2/bookshelf.html', context_dict, context)

@login_required
def bookpage(request, isbn):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    
    context_dict = get_context(request)
    book = Book.objects.get(isbn=isbn)
    listings = Listing.objects.filter(book__book__isbn = isbn, sell_status = 'O')
    
    context_dict['listings'] = listings
    context_dict['book'] = book
    context_dict['courses'] = Course.objects.filter(books = book)
    
    return render_to_response('ptonptx2/book_lookup.html', context_dict, context)
    
@login_required
def about(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    
    return render_to_response('ptonptx2/about.html', context)

@login_required
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
@login_required
def remove_listing(request):
    context = RequestContext(request)
    if not request.POST:
        return HttpResponseRedirect("/bookshelf")
    listingid=request.POST['listingid']
    print listingid
    listing = Listing.objects.get(pk = listingid)
    owner = listing.owner
    # make sure the person can only remove their own listings
    if not owner == request.user.profile_set.get():
        messages.error("You can't remove that listing. Are you trying to break the site?")
        return HttpResponseRedirect("/bookshelf")
    physbook = listing.book
    owner.books_selling.remove(physbook)
    owner.books_owned.add(physbook)
    owner.save()

    listprice = listing.price
    listing.delete()

    #set lowest student price, if necessary
    #book = physbook.book
    #if book.lowest_student_price <= listprice:
    #    if not Listing.objects.filter(book__book__pk = book.pk):
    #        book.lowest_student_price = None
    #    else:
    #        book.lowest_student_price = 1000000
    #        for listing in Listing.objects.filter(book__book__pk = book.pk):
    #            if listing.price < book.lowest_student_price:
    #                book.lowest_student_price = listing.price
    #    book.save()
    set_lowest_price(physbook.book)

    return HttpResponseRedirect("/" + physbook.book.isbn + "/")

@login_required
def profile(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    if request.POST:
        profile = request.user.profile_set.get()
        profile.first_name = request.POST['first_name']
        profile.last_name = request.POST['last_name']
        profile.preferred_meetingplace = request.POST['pref_meeting_place']
        profile.save()
        messages.success(request, "Profile updated")
    return HttpResponseRedirect("/bookshelf")

@login_required
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

@login_required
def searchcourses(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    finallist = []

    if request.GET['q']:
        q = request.GET['q']
        for f in Course.objects.all():
            if q.upper().replace(" ", "") == (f.dept + f.num):
                finallist.append(f)
        if len(finallist) == 0:
            for f in Course.objects.all():
                if q.upper().replace(" ", "") == f.dept:
                    finallist.append(f)
                if q == f.num:
                    finallist.append()
                if re.search(q.upper().replace(" ",""), f.name.upper().replace(" ","")) != None:
                    finallist.append(f)
    
    sortedbynum = sorted(finallist, key=lambda course: course['num'])
    sortedbydeptandnum = sorted(sortedbynum, key=lambda course: course['dept'])
    context_dict = get_context(request)
    context_dict['query'] = q
    context_dict['course_dict'] = sortedbydeptandnum

    
    return render_to_response('ptonptx2/course_page_list.html', context_dict, context)

@login_required
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
            try:
                return HttpResponseRedirect(request.POST['prevpage'])
            except:
                return HttpResponseRedirect("/bookshelf")
        else:
            return HttpResponse("form error")


    else:
        return HttpResponseRedirect("/bookshelf")


@login_required
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
            incourse = False
            for course in profile.course_list.all():
                for coursebook in course.books.all():
                    if book == coursebook:
                        incourse = True
            if not incourse:
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

@login_required
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
        physbook.save()
        profile.books_owned.add(physbook)
        profile.save()
        context_dict['m'] = m.title
        context_dict['markedasowned'] = True
        messages.success(request, "Book %s has been marked as owned" % (m.title))
        return HttpResponseRedirect("/bookshelf")

@login_required
def addtoneeded(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.GET['m']:
        m = request.GET['m']
        m = Book.objects.get(id=m)
        profile.books_needed.add(m)
        profile.save()
        context_dict['m'] = m.title
        context_dict['addedtoneeded'] = True
        messages.success(request, "Book %s has been added to needed" % (m.title))
        return HttpResponseRedirect("/bookshelf")

@login_required
def removefromneeded(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.GET['n']:
        rfn = request.GET['n']
        rfn = Book.objects.get(id=rfn)
        profile.books_needed.remove(rfn)
        profile.save()
        context_dict['rfn'] = rfn.title
        context_dict['removefromneeded'] = True
        messages.success(request, "Book %s has been removed from books needed" % (rfn.title))
    return HttpResponseRedirect("/bookshelf")

@login_required
def removefromselling(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.GET['s']:
        rfs = request.GET['s']
        rfs = PhysBook.objects.get(id=rfs)
        profile.books_selling.remove(rfs)
        profile.books_owned.add(rfs)
        profile.save()

        #delete the listing
        l = rfs.listing_set.get()
        l.delete()

        context_dict['rfs'] = rfs.book.title
        context_dict['removefromselling'] = True
        messages.success(request, "Book %s has been removed from books selling" % (rfs.book.title))

        set_lowest_price(rfs.book)

    return HttpResponseRedirect("/bookshelf")

@login_required
def removefromowned(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.GET['o']:
        rfo = request.GET['o']
        rfo = PhysBook.objects.get(id=rfo)
        title = rfo.book.title
        rfo.delete()
        context_dict['rfo'] = title
        context_dict['removefromowned'] = True
        messages.success(request, "Book %s has been removed from books owned" % (title))
        return HttpResponseRedirect("/bookshelf")

@login_required
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

@login_required
def help(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    return render_to_response('ptonptx2/helppage.html', context_dict, context)

@login_required
def selling(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    books_selling = profile.books_selling.objects.all()
    context_dict['selling'] = books_selling

    return render_to_response('ptonptx2/selling.html', context_dict, context)

@login_required
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
    
@login_required
def coursepage(request, course_dpt, course_num):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    course = Course.objects.get(dept=course_dpt, num=course_num)

    books = course.books

    fields = Book._meta.fields

    context_dict = get_context(request)
    context_dict['course'] = course


    return render_to_response('ptonptx2/course_page.html', context_dict, context)


@login_required
def buybook(request):
    context = RequestContext(request)
    
    if not request.user.is_authenticated():
        return redirect('/login/')

    if not request.POST:
        return HttpResponseRedirect("/bookshelf")

    listingid = request.POST['listingid']
    isbn = request.POST['isbn']
    
    context_dict = get_context(request)

    listing = Listing.objects.get(id=listingid)

    context_dict['listing'] = listing

    return render_to_response('ptonptx2/confirmpurchase.html', context_dict, context)

#not used
@login_required
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
    
#not used
@login_required
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


@login_required
def confirmbuybook(request):
    context = RequestContext(request)

    if not request.POST:
        return HttpResponseRedirect("/bookshelf")
    
    if not request.user.is_authenticated():
        return redirect('/login/')
    
    context_dict = get_context(request)

    listingid=request.POST['listingid']
    listing = Listing.objects.get(id=listingid)
    sellerprofile = listing.owner

    context_dict['listing'] = listing
    context_dict['sellerprofile'] = sellerprofile

    #mark the listing as pending
    listing.sell_status = 'P'
    listing.save()

    #set lowest price, if necessary
    set_lowest_price(listing.book.book)
    
    transaction = Transaction(buyer = context_dict['user'], seller=listing.owner, price=listing.price, book = listing.book)
    transaction.save()

    return render_to_response('ptonptx2/afterpurchase.html', context_dict, context)
    
@login_required
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
            if transaction.sellerreview != None and transaction.buyerreview != None:

                book = transaction.book
                listing = Listing.objects.get(book = book)
                buyer = transaction.buyer
                seller = transaction.seller
            	buyer.books_owned.add(book)
                sellermessage = "Hi! \n\n Someone has bought your book on PTX2. The user's details are: \n Name:" + buyer.first_name + " " + buyer.last_name + "\n Buyer email: " + buyer.user.username +"@princeton.edu \n Preferred meeting place: " + buyer.preferred_meetingplace + "\n\n Thanks, \n\n PTX2"
            	buyermessage = "Hi! \n You have bought someone else's book on PTX2. The user's details are: \n Name:" + seller.first_name + " " + seller.last_name + "\n Seller email: " + seller.user.username +"@princeton.edu \n Preferred meeting place: " +seller.preferred_meetingplace + "\n\n Thanks, \n\n PTX2"
            	send_mail('Pending transaction', sellermessage, 'princetonptx2@gmail.com', [seller.user.username + '@princeton.edu'], fail_silently=False)
            	send_mail('Pending transaction', buyermessage, 'princetonptx2@gmail.com', [buyer.user.username + '@princeton.edu'], fail_silently=False)
            	listing.delete()
            return HttpResponseRedirect("/bookshelf")
        else:
            print form.errors
    else:
        form = ReviewForm()
    context_dict['form'] = form
        

    return render_to_response('ptonptx2/pendingtransaction.html', context_dict, context)
    
@login_required
def pending(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    context_dict = get_context(request)
    
    transactions = Transaction.objects.filter(Q(buyer = context_dict['user'])|Q(seller=context_dict['user']), Q(buyerreview=None) | Q(sellerreview=None))
    
    context_dict['transactions'] = transactions
    
    return render_to_response('ptonptx2/pending.html', context_dict, context)
