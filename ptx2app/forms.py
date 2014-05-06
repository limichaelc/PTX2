from django import forms
from ptx2app.models import *

class SellBookForm(forms.ModelForm):
    book = forms.ModelChoiceField(queryset = Book.objects.all())
    owner = forms.ModelChoiceField(queryset = Profile.objects.all())
    SELL_STATUSES = (
		('O', 'Currently offered'),
		('P', 'Sale pending'),
		('S', 'Sold'),
		('C', 'Cancelled'),
	)
    CONDITIONS_CHOICES = (
		('New',  'Brand new, never been used, and in perfect condition. Still in shrink-wrap, if applicable.'),
		('Like New', 'Looks new and in perfect condition. No markings whatsoever.'),
		('Very good', 'Excellent condition with slight wear-and-tear. Very sparse markings.'),
		('Good', 'Clean condition with moderate wear-and-tear. Limited markings.'),
		('Acceptable', 'Usable condition, with heavier signs of wear-and-tear and a considerable amount of markings.')
        )
    choicefield = forms.ChoiceField(choices = CONDITIONS_CHOICES)
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

