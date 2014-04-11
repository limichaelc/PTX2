from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
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
	book = {'title': 'Advanced Programming Techniques',
	'course_usedin': 'COS 333',
	'labyrinth_price': '15.00',
	'amazon_price': '12.20',
	'student_price': '13.10'}
	person = {'book': {'owned': True, 'selling': False}}
	t = get_template('book_lookup.html')
	html = t.render(Context({'book': book, 'person': person}))
	return HttpResponse(html)

