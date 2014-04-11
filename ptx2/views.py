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

def book_lookup(request):
	testbook = {'title': 'The Practice of Programming',
	'isbn': '9780201615869',
	'course_usedin': {'dept': 'COS', 'course_code': '333'},
	'labyrinth_price': '15.00',
	'amazon_price': '12.20',
	'student_price': '13.10',
	'best_price': '12.20',
	'best_seller': 'Amazon'}
	testperson = {'book': {'owned': False }}
	return render(request, 'book_lookup.html', {'book': testbook, 'person': testperson})
