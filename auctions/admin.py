from django.contrib import admin

# Register your models here.

from .models import Listing, Comment, Bid




    

admin.site.register(Listing)
admin.site.register(Comment)
admin.site.register(Bid)