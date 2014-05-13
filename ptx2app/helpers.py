from ptx2app.models import *

def set_lowest_price(book):
    # if there are none of this book being sold
    if not Listing.objects.filter(book__book__pk = book.pk, sell_status='O'):
        book.lowest_student_price = None
    else: #find the lowest price among those being sold
        book.lowest_student_price = float('inf')
        for listing in Listing.objects.filter(book__book__pk = book.pk, sell_status='O'):
            if listing.price < book.lowest_student_price:
                book.lowest_student_price = listing.price
    book.save()

