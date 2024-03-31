from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from community.models import ChatBox
from django.core.mail import send_mail


def index(request):
    room_name = '1-2'
    messages = ChatBox.objects.filter(room=room_name)
    return render(request, 'index.html', {"room_name": room_name, "messages": messages, "index_token": True})


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
    return render(request, 'profile.html')


def signUpHandle(request):
    if request.method=='POST':
        username = request.POST.get('username', '')
        username = username.lower()
        fname = request.POST.get('fname', '')
        lname = request.POST.get('lname', '')
        email = request.POST.get('email', '')
        pass1 = request.POST.get('pass1', '')
        pass2 = request.POST.get('pass2', '')
        check = request.POST.get('check', '')

        # check errors here
        if pass1!=pass2:
            messages.warning(request, "Your entered passwords did not match each other. Please try again...")
            return redirect('/blog')

        if username[0].isdigit() or username[0] == ' ':
            messages.info(request, "Usernamae must not start with a digit or a space.")
            return redirect('/blog')


        not_allowed = '''+!@#$%&*^~][}{`',<>|\/:;=?"'''
        for i in not_allowed:
            if i in username:
                messages.info(request, '''Usernamae cannot contain +!@#$%&*^~][}{`',<>|\/:;=?" characters''')

                return redirect('/blog')

        # adding user
        try:
            user = User.objects.create_user(username, email, pass1)
            user.first_name = fname
            user.last_name = lname
            user.save()
            
            if check == 'remember-me':
                user = authenticate(username = username, password = pass1)
                if user is not None:
                    login(request, user)
                    messages.success(request, "Account successfully created!")
                    messages.success(request, f"successfully logged in as {username}!")

                    return redirect('/blog')

            else:
                messages.success(request, "Account successfully created!")
                return redirect('/community/market-place')

        except Exception as e:
            messages.error(request, "This username already exists. Please Try entering a unique username!")
            return redirect('/register')
    
    else:
        return render(request, 'notfound.html')


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


