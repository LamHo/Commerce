from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required

from .models import User, Category, Listing, Bid, Comment

class create_form(forms.Form):
    name = forms.CharField(label = 'Name', max_length = 100)
    description = forms.CharField(label = mark_safe("Description<br />"), widget=forms.Textarea)
    category = forms.CharField(label = "Category", max_length = 20)
    starting_bid = forms.CharField(label = "Starting bid", max_length = 4)
    image = forms.ImageField(label = "Image")  
    
    


def index(request):
    if request.user.is_authenticated:
        listings_won = request.user.listings_won.all()[::-1]
        return render(request, "auctions/index.html",{
            "listings": Listing.objects.filter(is_active = True).all().order_by('-id'),
            "listings_won": listings_won
        })
    else:
        return render(request, "auctions/index.html",{
            "listings": Listing.objects.filter(is_active = True).all().order_by('-id'),
            
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='login')
def create(request):
    if (request.method == "POST"):
        form = create_form(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES  # multivalued dict
            in_image = files.get("image")
            in_name = form.cleaned_data['name']
            in_description = form.cleaned_data['description']
            in_starting_bid = form.cleaned_data['starting_bid']
            in_category = form.cleaned_data['category']
            
            creator = User.objects.get(pk = request.user.id)
            query_category = Category.objects.filter(name = in_category)
            print(query_category)
            if (not query_category):
                category = Category(name = in_category)
                category.save()
            else:  
                category = Category.objects.get(name = in_category)

            new_listing = Listing(name = in_name, description = in_description, owner = creator, category = category, image = in_image)
            new_listing.save()
            new_bid = Bid(how_much = in_starting_bid, which_listing = new_listing, owner = creator)
            new_bid.save()
            
            return HttpResponseRedirect(reverse("index"))
           


    else:
        form = create_form()
        return render(request, "auctions/create.html",{
            "form": form
        })


def listing(request, listing_id):
    listing = Listing.objects.all().get(pk = listing_id)
    comments = listing.comments.all().order_by('-id')
    is_bidder = (listing.bid.owner.username == request.user.username)
    is_owner = (listing.owner.username == request.user.username)
    is_active = listing.is_active
    if (is_active == False):
        return render(request,"auctions/listing.html",{
            "listing": listing,
            "comments": comments,
            "is_active": is_active
        })
    else:
        if not request.user.is_authenticated:
            already = False
        else:
            already = request.user.watched_listings.filter(pk = listing_id)
        if (request.method == "POST"):
            if (request.POST['state'] == "place_bid"):
                if (request.POST['bid'] <= Listing.objects.get(pk = listing_id).bid.how_much):
                    
                    
                    return render(request, "auctions/listing.html",{
                        "listing": listing,
                        "is_owner": is_owner,
                        "is_bidder": is_bidder,
                        "comments": comments,
                        "already": already,
                        "error": True,
                        "is_active": is_active
                    })
                else:
                    
                    listing.bid.delete()
                    created_bid = Bid(how_much=request.POST['bid'], which_listing=listing, owner=request.user)
                    created_bid.save()
                    
                    return render(request, "auctions/listing.html",{
                        "listing": listing,
                        "is_owner": is_owner,
                        "is_bidder": True,
                        "comments": comments,
                        "already": already,
                        "error": False,
                        "is_active": is_active  
                    })


            elif (request.POST['state'] == "comment"):
                content = request.POST['comment']
                cmt = Comment(content=content,owner=request.user,which_listing=listing)
                cmt.save()
                return render(request, "auctions/listing.html",{
                        "listing": listing,
                        "is_owner": is_owner,
                        "is_bidder": is_bidder,
                        "comments": comments,
                        "already": already,
                        "error": False,
                        "is_active": is_active
                    })

            elif (request.POST['state'] == "close_listing"):
                listing.is_active = False
                listing.winner = listing.bid.owner
                listing.save()
                return HttpResponseRedirect(reverse("index"))    
        else:
            
            
            return render(request, "auctions/listing.html",{
                "listing": listing,
                "is_owner": is_owner,
                "is_bidder": is_bidder,
                "comments": comments,
                "already": already,
                "error": False,
                "is_active": is_active   
            })

@login_required(login_url='login')
def watchlist(request):
    if (request.method == "POST"):
        
        if (request.POST["state"] == "add"):
            received_listing_id = request.POST['added_listing_id']
            received_listing = Listing.objects.get(pk = received_listing_id)
            request.user.watched_listings.add(received_listing)
            return render(request,"auctions/watchlist.html",{
                "listings": request.user.watched_listings.filter(is_active=True).all()[::-1]
        })
        else: 
            received_listing_id = request.POST['removed_listing_id']
            received_listing = Listing.objects.get(pk = received_listing_id)
            request.user.watched_listings.remove(received_listing)

        
        return render(request,"auctions/watchlist.html",{
            "listings": request.user.watched_listings.filter(is_active=True).all()[::-1]
        })
    else:
        
        return render(request,"auctions/watchlist.html",{
            "listings": request.user.watched_listings.filter(is_active=True).all()[::-1]
        })

def categories(request):
    list = Category.objects.all()
    return render(request, "auctions/categories.html",{
        "categories_list": list
    })

def category_listings(request,name):
    listings = Category.objects.get(name = name).listings.filter(is_active = True).all()
    return render(request, "auctions/category_listing.html",{
        "category": name,
        "listings": listings
    })