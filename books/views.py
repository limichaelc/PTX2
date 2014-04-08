from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Books says hello world!")

def about(request):
    return HttpResponse("This is the about page!")