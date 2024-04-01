from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import ChatBox, Demand, Offering, Deal, Grievance, Notification
from lendIt.form import Offer, AskFor, PutGrievance


def index(request):
    return redirect('/community/borrow')

def borrow(request):
    if request.method=='POST':
        offering_form = Offer(data=request.POST, files=request.FILES)
        if offering_form.is_valid():
            offering_form.save()
        return redirect('/community/lend')

    else:
        categories = Offering.objects.values('category').distinct()
        offerings = {}
        # Iterate over distinct categories
        for category in categories:
            # Filter products by the current category
            category_wise_items = Offering.objects.filter(category=category['category']).exclude(lender=request.user)
            # Store the products in the dictionary with the category name as key
            offerings[category['category']] = category_wise_items
        return render(request, 'community/borrow.html', {"borrow_token": True, "offerings": offerings})

def lend(request):
    if request.method=='POST':
        demand_form = AskFor(data=request.POST, files=request.FILES)
        if demand_form.is_valid():
            demand_form.save()
        return redirect('/community/borrow')

    else:
        categories = Demand.objects.values('category').distinct()
        demands = {}
        # Iterate over distinct categories
        for category in categories:
            # Filter products by the current category
            category_wise_items = Demand.objects.filter(category=category['category']).exclude(borrower=request.user)
            # Store the products in the dictionary with the category name as key
            demands[category['category']] = category_wise_items
        return render(request, 'community/lend.html', {"lend_token": True, "demands": demands})


def dealing(request, id):
    id=id.split('by')
    lender = Offering.objects.filter(id=int(id[0]))[0].lender

    if request.user.id == lender.id:
        username = User.objects.filter(id=int(id[-1]))[0].username
    else:
        username = lender.username

    room_name = f'{id[-1]}-{lender.id}' # borrower-lender //always
    messages = ChatBox.objects.filter(room=room_name)
    return render(request,'community/dealing.html', {'room_name': room_name, 'messages': messages, 'username': username})

def deal(request, id):
    pass
