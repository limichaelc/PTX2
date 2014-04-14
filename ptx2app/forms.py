from django import forms

class SellBookForm(forms.Form):
    bookName = forms.CharField(max_length=128, help_text="What is the book you are trying to sell?")
    classId = forms.IntegerField(help_text = "What class is this for?")
    CONDITIONS_CHOICES = (
		('New',  'Brand new, never been used, and in perfect condition. Still in shrink-wrap, if applicable.'),
		('Like New', 'Looks new and in perfect condition. No markings whatsoever.'),
		('Very good', 'Excellent condition with slight wear-and-tear. Very sparse markings.'),
		('Good', 'Clean condition with moderate wear-and-tear. Limited markings.'),
		('Acceptable', 'Usable condition, with heavier signs of wear-and-tear and a considerable amount of markings.')
        )
    choicefield = forms.ChoiceField(choices = CONDITIONS_CHOICES)


