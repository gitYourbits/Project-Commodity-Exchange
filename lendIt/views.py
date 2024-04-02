from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from community.models import Demand, Offering, Deal, Grievance, Notification
from .form import Offer, AskFor, PutGrievance


def index(request):

    demand_form = AskFor()
    offering_form = Offer()

    latest_ongoing_deals = Deal.objects.all()[0:6]
    categories = Offering.objects.values_list('category', flat=True).distinct()
    notifications = Notification.objects.filter(parent=request.user.id, seen=False)

    return render(request, 'index.html', {"index_token": True, 'demand_form': demand_form, 'offering_form': offering_form, "deals": latest_ongoing_deals, 'categories': categories, 'notifications': notifications})


def register(request):
    if request.method == 'POST':
        fname = request.POST.get('fname', '')
        lname = request.POST.get('lname', '')

        email = request.POST.get('email', '')
        if '@lpu.in' not in email:
            messages.error(reqeust, 'You can only register through your university email id.')
            return redirect('/')

        pass1 = request.POST.get('pass1', '')
        pass2 = request.POST.get('pass2', '')

        username=''
        for i in email:
            if i=='@':
                break
            else:
                username+=i

        if pass1!=pass2:
            messages.warning(request, "Your entered passwords did not match each other. Please try again...")
            return redirect('/')

        try:
            user = User.objects.create_user(username, email, pass1)
            user.first_name = fname
            user.last_name = lname
            user.save()
            
            user = authenticate(username = username, password = pass1)
            if user is not None:
                send_otp(email)
                login(request, user)
                messages.success(request, f'Account created successfully! An OTP has sent to your registered email, you will need that otp to verify your account. Note your username: "{username}"')
                return redirect(f'/')

        except Exception as e:
            messages.error(request, f"Account already exists with {e}.")
            return redirect('/')

        return redirect('/')

def send_otp(mail):
    import pyotp

    totp = pyotp.TOTP(pyotp.random_base32(), interval=3600*12) #otp valid for 12 hours
    otp = totp.now()

    # Send OTP via email
    send_mail(
        'Your OTP',  # Subject
        f'Your OTP is: {otp}',  # Message
        'mr.raojiad19092003@gmail.com',  # Sender's email address
        [mail],  # Recipient's email address
        fail_silently=False,
    )



def profile(request):
    # offering_form = Offer(data=request.POST, files=request.FILES)
    return render(request, 'profile.html')


def loginHandle(request):
    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username = username, password = password)

        if user is not None:
            login(request, user)
            messages.success(request, f"successfully logged in as {username}")
            return redirect('/')

        else:
            messages.error(request, "Invalid username or password...")
            return redirect('/')
    else:
        return render(request, 'notfound.html')


def logoutHandle(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect('/')
    else:
        messages.info(request, "No user has logged in yet")
        return redirect('/')


