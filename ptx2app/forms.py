from django import forms
from ptx2app.models import *

class SellBookForm(forms.ModelForm):
    book = forms.ModelChoiceField(queryset = Book.objects.all())
    owner = forms.ModelChoiceField(queryset = User.objects.all())
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
        
class ProfileForm(forms.ModelForm):

	
	class Meta:
		model = Profile
		exclude = ['reviews', 'user']

class AddCourseForm(form.ModelForm):
    course = forms.ModelChoiceField(queryset = Course.objects.all())
    class Meta:
        model = Profile
        fields = ('course_list',)

