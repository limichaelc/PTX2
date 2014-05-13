from django import forms
from ptx2app.models import *

class SellBookForm(forms.ModelForm):
    book = forms.ModelChoiceField(queryset = Book.objects.all())
    owner = forms.ModelChoiceField(queryset = Profile.objects.all())
    class Meta:
        model = Listing
        exclude = ['book', 'owner', 'sell_status']
        
class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		exclude = ['reviews', 'user']

class AddCourseForm(forms.Form):
    course = forms.CharField(max_length = 100)

class RemoveCourseForm(forms.Form):
    r = forms.CharField(max_length = 100)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review

class PhysBookForm(forms.ModelForm):
	class Meta:
		model = PhysBook
		exclude = ['book']
		
class ListingForm(forms.ModelForm):
	class Meta:
		model = Listing
		fields= ['price']

