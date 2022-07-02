from django.contrib.auth.models import AbstractUser
from django.db import models




class User(AbstractUser):
    watchlist = []

class Category(models.Model): 
    name = models.CharField(max_length=100)


class Listing(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null = True)
    #current_bid = models.CharField(max_length=5)
    #some more attributes
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings", null = True)
    image = models.ImageField(upload_to='images/', null = True) 
    watchers = models.ManyToManyField(User, blank=True, related_name="watched_listings") 
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings_won", null = True)
    is_active = models.BooleanField(default = True)

class Comment(models.Model):
    content = models.CharField(max_length=1000, null = True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    which_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    

class Bid(models.Model):
    how_much = models.CharField(max_length=5)
    #some more attributes
    which_listing = models.OneToOneField(Listing, on_delete=models.CASCADE) #relatedname = listing.bid
    owner =  models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")



