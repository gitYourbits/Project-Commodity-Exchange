from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def index(request):
    return redirect('/community/borrow')


def lend(request):
    return render(request, 'community/lend.html', {"lend_token": True})

def borrow(request):
    return render(request, 'community/borrow.html', {"borrow_token": True})

