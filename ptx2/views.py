from django.shortcuts import render
import datetime

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

def course_lookup(request, dept, code):
	try: 
		code = int(code)
	except ValueError:
		raise Http404()
	html = "<html><body>You are looking at course %s %s.</body></html>" % (dept.upper(), code)
	return HttpResponse(html)

def sidebar(request):
	cos333 = {'dept': 'cos', 'code': 333, 'books': 1}
	person = {'books_total': 4, 'books_needed': 2, 'courses': [cos333]}
	return render(request, 'sidebar.html', {'person': person})

def book_lookup(request):
	testlisting = {'price': 15.00, 'condition': 'New: Brand new, never been used, and in perfect condition. Still in shrink-wrap, if applicable.', 'comment': 'Mreh'}
	testbook = {'title': 'The Practice of Programming',
	'isbn': '9780201615869',
	'course_usedin': {'dept': 'COS', 'course_code': '333'},
	'labyrinth_price': '15.00',
	'amazon_price': '12.20',
	'student_price': '13.10',
	'best_price': '12.20',
	'best_seller': 'Amazon',
	'listings':[testlisting]}
	return render(request, 'book_lookup.html', {'book': testbook})

def bookshelf(request):
	needed_book1 = {'title': 'The Practice of Programming',
	'isbn': '9780201615869',
	'course_usedin': {'dept': 'COS', 'course_code': '333'},
	'labyrinth_price': '15.00',
	'amazon_price': '12.20',
	'student_price': '13.10',
	'best_price': '12.20',
	'best_seller': 'Amazon'}
	needed_book2 = {'title': 'Sen to Chihiro no Kamikakushi',
	'isbn': '9784198614065',
	'course_usedin': {'dept': 'JPN', 'course_code': '302'},
	'labyrinth_price': '19.60',
	'amazon_price': '8.60',
	'student_price': '0',
	'best_price': '8.60',
	'best_seller': 'Amazon'}
	selling_book1 = {'title': 'Language Files',
	'isbn': '9780814251799',
	'course_usedin': {'dept': 'LIN', 'course_code': '201'},
	'selling_for': '40.00'}
	owned_book1 = {'title': 'Kiite Oboeru Hanashikata Nihongo Nama Chukei Chu-Jokyu Hen',
	'isbn': '9784874243008',
	'course_usedin': {'dept': 'JPN', 'course_code': '302'}}
	cos333 = {'dept': 'cos', 'code': 333, 'books': 1}
	person = {'books_total': 4, 'books_needed': 2, 'books_selling': 1, 'books_owned': 1, 'courses': [cos333], 'first_name': 'Michael', 'last_name': 'Li'}
	return render(request, 'bookshelf.html', {'books_needed': [needed_book1, needed_book2], 'books_selling': [selling_book1], 'books_owned': [owned_book1], 'person': person })
