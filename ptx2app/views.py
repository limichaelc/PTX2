from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response


# Create your views here.
def index(request):
	context = RequestContext(request)
	
	context_dict = {'boldmessage': This is a book!'}

	return render_to_response('ptonptx2/index.html', context_dict, context)

