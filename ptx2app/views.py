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
from django.core.mail import send_mail, EmailMessage

# get the context of this request
def get_context(request):
    context = RequestContext(request)
    try:
        user = request.user
    except:
        HttpResponseRedirect("/login/")
    try:
        #profile = request.user.get_profile()
        profile = request.user.profile_set.get()
    except:
        profile = Profile.objects.create(user = user)
        profile.save()
    first = (not profile.first_name)
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

    num_total = len(profile.books_needed.all()) + len(profile.books_owned.all()) + len(Listing.objects.filter(owner = profile))

    context_dict = {'user' : profile,
                    'books' : books,
                    'num_needed' : len(profile.books_needed.all()),
                    'num_owned' : len(profile.books_owned.all()),
                    'num_selling' : len(Listing.objects.filter(owner = profile)),
                    'num_total' : num_total,
                    'num_pending' : len(Transaction.objects.filter(Q(buyer = profile)|Q(seller=profile), Q(buyerreview=None) | Q(sellerreview=None))),
                    'nums_by_course' : nums_by_course,
                    'user_selling': Listing.objects.filter(owner = profile),
                    'first_visit': first,
                    'user_transactions': Transaction.objects.filter(buyer = profile)
                    }
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
#loads the page for each book
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
#loads the about page
def about(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    
    return render_to_response('ptonptx2/about.html', context)

@login_required
#handles the selling the book once user clicks on specific listing
def sell_book(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    if request.method == 'POST':

        if len(request.POST['price']) == 0:
            messages.error(request, 'No price given. Please try again.')
            return HttpResponseRedirect("/bookshelf/")
        try:
            price = int(float(request.POST['price']))
        except:
            messages.error(request, "Invalid price given. Please use only numbers.")
            return HttpResponseRedirect("/bookshelf/")
        if price < 1:
            messages.error(request, "Invalid price given. Price must be greater than $1.")
            return HttpResponseRedirect("/bookshelf/")

        # if this is an edit, the POST will contain a 'listingpk' field

        if 'listingpk' in request.POST:
            pk = request.POST['listingpk']
            listing = Listing.objects.get(pk = pk)
            if listing.sell_status == 'P':
                messages.error(request, "Someone has already made an offer on this book. You can't edit the listing.")
                return HttpResponseRedirect("/bookshelf")
            listing.price = price
            listing.comment = request.POST['comment']
            listing.save()
            
            #set lowest student price
            #book = listing.book.book
            #lowstud = book.lowest_student_price
            #if not lowstud or price < lowstud:
            #    book.lowest_student_price = price
            #    book.save()
            set_lowest_price(listing.book.book)

            return HttpResponseRedirect("/"+request.POST['next'])

        # if this field doesn't exist, it's a new listing
        listing = Listing()
        user = request.user.profile_set.get()
        book = Book.objects.get(pk = request.POST['bookpk'])

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
        #lowstud = book.lowest_student_price
        #if not lowstud or price < lowstud:
        #    book.lowest_student_price = price
        #    book.save()

        listing.book = physbook
        listing.owner = user
        listing.sell_status = 'O'
        listing.price = price
        listing.comment = request.POST['comment']
        listing.save()
        set_lowest_price(physbook.book)
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
    listing = Listing.objects.get(pk = listingid)
    owner = listing.owner
    # make sure the person can only remove their own listings
    if not owner == request.user.profile_set.get():
        messages.error(request, "You can't remove that listing. Are you trying to break the site?")
        return HttpResponseRedirect("/bookshelf")
    if listing.sell_status == 'P':
        messages.error(request, "Sorry, someone has already purchased this book. You may cancel the transaction if you'd like.")
        return HttpResponseRedirect("/bookshelf/")
    physbook = listing.book
    owner.books_selling.remove(physbook)
    owner.books_owned.add(physbook)
    owner.save()

    listprice = listing.price
    listing.delete()

    set_lowest_price(physbook.book)

    return HttpResponseRedirect("/" + physbook.book.isbn + "/")

@login_required
#allows user to edit their profile
def profile(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    if request.POST:
        if len(request.POST['first_name']) == 0 or len(request.POST['last_name']) == 0 or len(request.POST['pref_meeting_place']) == 0:
            messages.error(request, "Invalid form. No action taken.")
        else:
            profile = request.user.profile_set.get()
            profile.first_name = request.POST['first_name']
            profile.last_name = request.POST['last_name']
            profile.preferred_meetingplace = request.POST['pref_meeting_place']
            profile.save()
            messages.success(request, "Profile updated.")
    return HttpResponseRedirect("/bookshelf")

@login_required
#loads the user's history of transactions
def history(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    transaction = Transaction.objects.all()
    past_transactions = []
    
    for instance in transaction:
    	#if the transaction has both reviews filled make it show up
        if (instance.buyerreview != None) & (instance.sellerreview != None):
            if profile == instance.buyer:
                past_transactions.append(instance)
            if profile == instance.seller:
                past_transactions.append(instance)
    past_transactions.sort(key=lambda tr: tr.pk)
    context_dict['history'] = past_transactions
    return render_to_response('ptonptx2/history.html', context_dict, context)

@login_required
#loads the search page for the search bar
def searchcourses(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    finallist = []

    if 'q' in request.GET:
        q = request.GET['q']
        context_dict['query'] = q
        if len(q) < 3:
            context_dict['too_short'] = True
            return render_to_response('ptonptx2/searcherrorpage.html', context_dict, context)
        if q.lower() == "and" or q.lower() == "the":
            context_dict['too_general'] = True
            return render_to_response('ptonptx2/searcherrorpage.html', context_dict, context)
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
    else:
        return HttpResponseRedirect("/bookshelf")
    
    sortedbynum = sorted(finallist, key=lambda course: course['num'])
    sortedbydeptandnum = sorted(sortedbynum, key=lambda course: course['dept'])
    context_dict = get_context(request)
    context_dict['query'] = q
    context_dict['course_dict'] = sortedbydeptandnum

    
    return render_to_response('ptonptx2/course_page_list.html', context_dict, context)

@login_required
#adds a specific course to user's course_list
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
#removes course from student's course list
def removecourse(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.method == "POST":
        r = request.POST['r']
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
    messages.success(request, "Course %s %s (%s) has been removed." % (r.dept, r.num, r.name))
    return HttpResponseRedirect("/bookshelf")
    #return render_to_response('ptonptx2/bookshelf.html', context_dict, context)

@login_required
#mark book as owned
def markasowned(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.method == "POST":
        m = request.POST['m']
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
        messages.success(request, "Book %s has been marked as owned." % (m.title))
        return HttpResponseRedirect("/bookshelf")

@login_required
#add book to needed
def addtoneeded(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.method == "POST":
        m = request.POST['m']
        m = Book.objects.get(id=m)
        profile.books_needed.add(m)
        profile.save()
        context_dict['m'] = m.title
        context_dict['addedtoneeded'] = True
        messages.success(request, "Book %s has been added to needed." % (m.title))
        return HttpResponseRedirect("/bookshelf")

@login_required
#remove book from needed
def removefromneeded(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.method == "POST":
        rfn = request.POST['n']
        rfn = Book.objects.get(id=rfn)
        profile.books_needed.remove(rfn)
        profile.save()
        messages.success(request, "Book %s has been removed from books needed." % (rfn.title))
    return HttpResponseRedirect("/bookshelf")

@login_required
#remove book from user's selling
def removefromselling(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.method == "POST":
        rfs = request.POST['s']
        rfs = PhysBook.objects.get(id=rfs)


        #delete the listing if it's not pending
        l = rfs.listing_set.get()
        if l.sell_status == 'P':
            messages.error(request, "Sorry, someone has already purchased this book. You may cancel the transaction if you'd like.")
            return HttpResponseRedirect("/bookshelf/")
        l.delete()

        profile.books_selling.remove(rfs)
        profile.books_owned.add(rfs)
        profile.save()

        messages.success(request, "Book %s has been removed from books selling." % (rfs.book.title))

        set_lowest_price(rfs.book)

    return HttpResponseRedirect("/bookshelf")

@login_required
#remove book from user's owned
def removefromowned(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    if request.method == "POST":
        rfo = request.POST['o']
        rfo = PhysBook.objects.get(id=rfo)
        title = rfo.book.title
        rfo.delete()
        messages.success(request, "Book %s has been removed from books owned." % (title))
        return HttpResponseRedirect("/bookshelf")

@login_required
#search query
def search(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')

    profile = request.user.get_profile()
    context_dict = get_context(request)

    if 'q' in request.GET:
        q = request.GET['q']
        context_dict['query'] = q
        #we'll only entertain queries that are at least 3 characters long
        if len(q) < 3:
            context_dict['too_short'] = True
            return render_to_response('ptonptx2/searcherrorpage.html', context_dict, context)
        if q.lower() == "and" or q.lower() == "the":
            context_dict['too_general'] = True
            return render_to_response('ptonptx2/searcherrorpage.html', context_dict, context)
        q_withspaces = q
        q = q.upper().replace(" ", "")
        finallist = []
        
        thiscourse = None
        deptcourses = []
        numcourses = []
        namecourses = []
        for f in Course.objects.all():
            if q == (f.dept + f.num):
                thiscourse = f
            elif len(q) == 3:
                if q == f.dept:
                    deptcourses.append(f)
                if q == f.num:
                    numcourses.append(f)
            if f.name.upper().find(q_withspaces) != -1:
                namecourses.append(f)

        deptcourses.sort(key = lambda course: course.num)
        numcourses.sort(key = lambda course: course.dept)
        namecourses.sort(key = lambda course: course.name)
        courses = deptcourses + numcourses + namecourses

        #the user has searched for a course
        if thiscourse != None:
            finallist = thiscourse.books.all()
            context_dict['book_dict'] = finallist
            context_dict['courses'] = [thiscourse]
            return render_to_response('ptonptx2/booksearchpage.html', context_dict, context)

        for f in Book.objects.all():
            booktitle = f.title.upper().replace(" ", "")
            #if re.search(q, booktitle) != None:
            if booktitle.find(q) != -1:
                finallist.append(f)

        if len(finallist) == 0 and len(courses) == 0:
            return render_to_response('ptonptx2/searcherrorpage.html', context_dict, context)
        context_dict['book_dict'] = sorted(finallist, key=lambda book: book['title'])
        context_dict['courses'] = courses

    else:
        return render_to_response('ptonptx2/searcherrorpage.html', context_dict, context)
    return render_to_response('ptonptx2/booksearchpage.html', context_dict, context)

@login_required
#loads help page
def help(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    profile = request.user.get_profile()
    context_dict = get_context(request)
    return render_to_response('ptonptx2/helppage.html', context_dict, context)

@login_required
#loads selling 
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
#scarpe function
def scrape(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    if request.method == 'POST':
        if request.POST['action'] == 'scrape':
            pagewriter.write('page.txt')
            scrape.scrape('page.txt')
        else:
            scrape_funcs.save()

        return HttpResponse("Your request has been processed. Shine on you crazy diamond.")

    else:
        return render_to_response('ptonptx2/scrape.html', context)
    
@login_required
#loads course page & books for that page
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

    if listing.sell_status == 'P':
        messages.error(request, "Sorry, it looks like someone already bought that book. Please choose another listing.")
        return HttpResponseRedirect("/bookshelf")

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

@login_required
#confirm that you have bought the book
def confirmbuybook(request):
    context = RequestContext(request)

    if not request.POST:
        return HttpResponseRedirect("/bookshelf")
    
    if not request.user.is_authenticated():
        return redirect('/login/')
    
    context_dict = get_context(request)

    listingid=request.POST['listingid']
    listing = Listing.objects.get(id=listingid)
    #the purchase has alread been confirmed, but they might resend the form
    if listing.sell_status == 'P':
        return render_to_response('ptonptx2/afterpurchase.html', context_dict, context)

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
    buyer = transaction.buyer
    seller = transaction.seller
    sellermessage = "Hello " + seller.first_name + "!\n\n" + buyer.first_name + " " + buyer.last_name + " (" + buyer.user.username +"@princeton.edu) has bought your copy of " + transaction.book.book.title + " on PTX2 for $" +  str(transaction.price) + ".\nJust to expedite the selling process, " + buyer.first_name + " has suggested meeting at: " + buyer.preferred_meetingplace + ".\n\nSimply reply to this email to talk to " + buyer.first_name + " and figure out when to meet.\n\nAfter you've completed the transaction, be sure to come back and leave a review.\n\nThanks, \n\n PTX2"
    buyermessage = "Hello " + buyer.first_name + "!\n\nYou have purchased " + transaction.book.book.title + " on PTX2 for $" +  str(transaction.price) + " from " + seller.first_name + " " + seller.last_name + " (" + seller.user.username +"@princeton.edu).\nJust to expedite the buying process, " + seller.first_name + " has suggested meeting at: " + seller.preferred_meetingplace + ".\n\nSimply reply to this email to talk to " + seller.first_name + " and figure out when to meet.\n\nAfter you've completed the transaction, be sure to come back and leave a review.\n\nThanks, \n\n PTX2"
    sellermail = EmailMessage('You sold a book on PTX2!', sellermessage, 'PTX2 <princetonptx2@gmail.com>', [seller.user.username + '@princeton.edu'], headers = {'Reply-To': buyer.user.username + '@princeton.edu'})
    buyermail = EmailMessage('You bought a book on PTX2!', buyermessage, 'PTX2 <princetonptx2@gmail.com>', [buyer.user.username + '@princeton.edu'], headers = {'Reply-To': seller.user.username + '@princeton.edu'})
    sellermail.send(fail_silently=True)
    buyermail.send(fail_silently=True)
    #send_mail('You sold a book on PTX2!', sellermessage, 'princetonptx2@gmail.com', [seller.user.username + '@princeton.edu'], fail_silently=False)
    #send_mail('You bought a book on PTX2!', buyermessage, 'princetonptx2@gmail.com', [buyer.user.username + '@princeton.edu'], fail_silently=False)

    return render_to_response('ptonptx2/afterpurchase.html', context_dict, context)
    
@login_required
#loads pending transactionspage
def pending(request):
    context = RequestContext(request)
    if not request.user.is_authenticated():
        return redirect('/login/')
    context_dict = get_context(request)

    # the user has confirmed a transaction
    if request.POST and request.POST['action'] == 'review':
        rev = Review(comment=request.POST['review'])
        rev.save()
        transaction = Transaction.objects.get(pk = request.POST['pk'])
        if transaction.buyer == context_dict['user']:
             transaction.buyerreview = rev
        if transaction.seller == context_dict['user']:
            transaction.sellerreview = rev
        transaction.save()

        #if both the seller and buyer have confirmed, remove the listing
        if transaction.sellerreview != None and transaction.buyerreview != None:

            book = transaction.book
            listing = Listing.objects.get(book = book)
            buyer = transaction.buyer
            seller = transaction.seller
            buyer.books_owned.add(book)
            seller = transaction.seller
            seller.books_selling.remove(book)
            listing.delete()

        return HttpResponseRedirect("/pending")
    elif request.POST and request.POST['action'] == 'cancel':
        transaction = Transaction.objects.get(pk = request.POST['pk'])
        if transaction.sellerreview or transaction.buyerreview:
            message.error(request, "This transaction has already been reviewed. You can't cancel it.")
            return HttpResponseRedirect("/bookshelf")
        listing = Listing.objects.get(book = transaction.book)
        listing.sell_status = 'O'
        listing.save()
        seller = transaction.seller
        buyer = transaction.buyer
        transaction.delete()
        set_lowest_price(listing.book.book)
        messages.success(request, "Transaction cancelled.")
        sellermessage = "Hello " + seller.first_name + ",\n\nThe transaction for your copy of " + transaction.book.book.title + " on PTX2 has been cancelled. Your listing has been readded to the system.\nIf you no longer wish to sell this book, you can remove the listing on your bookshelf.\n\nThank you for using PTX2!"
    	buyermessage = "Hello " + buyer.first_name + ",\n\nWe regret to inform you that the transaction for " + transaction.book.book.title + " on PTX2 has been cancelled. You can search for another offer on your bookshelf.\n\nThank you for using PTX2!"
        send_mail('Transaction Cancelled', sellermessage, 'PTX2 <princetonptx2@gmail.com>', [seller.user.username + '@princeton.edu'], fail_silently=False)
        send_mail('Transaction Cancelled', buyermessage, 'PTX2 <princetonptx2@gmail.com>', [buyer.user.username + '@princeton.edu'], fail_silently=False)
        return HttpResponseRedirect("/bookshelf/")


    transactions = Transaction.objects.filter(Q(buyer = context_dict['user'])|Q(seller=context_dict['user']), Q(buyerreview=None) | Q(sellerreview=None))
    
    context_dict['transactions'] = transactions
    
    return render_to_response('ptonptx2/pending.html', context_dict, context)
