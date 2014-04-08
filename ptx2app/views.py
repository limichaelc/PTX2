from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from ptx2app.models import *


# Create your views here.
def index(request):
	context = RequestContext(request)
	
	user_list = User.objects.all()
	context_dict = {'users' : user_list}

	return render_to_response('ptonptx2/index.html', context_dict, context)

