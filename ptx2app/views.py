from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from ptx2app.models import *
from ptx2app.forms import *


# Create your views here.
def index(request):
	context = RequestContext(request)
	
	user_list = User.objects.all()
	context_dict = {'users' : user_list}

	return render_to_response('ptonptx2/index.html', context_dict, context)

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
	

