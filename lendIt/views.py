from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from community.models import Demand, Offering, Deal, Grievance, Notification, OtpVerification, Payment
from .form import Offer, AskFor, PutGrievance
from django.views.decorators.csrf import csrf_exempt
import json
import razorpay


@csrf_exempt
def index(request):
    if request.user.is_authenticated:
        verifier = OtpVerification.objects.get(parent=request.user.id)

        if not verifier.status:
            messages.info(reqeust, 'Kindly verify your account with the OTP sent to your university email...')
            return render(request, 'verify.html')

        if verifier.grievance_count>0:
            messages.warning(request, 'You have complaints from users. Your account is blocked untill you resolve them.')
            
            return redirect('/profile')

    else:
        messages.info(request, 'Register or login to enjoy services!')
        return render(request, 'verify.html', {'registeration_required': True})

    if request.method == 'POST':
        raw_data = request.body.decode('utf-8')
        data = json.loads(raw_data)
        data = data['otp']

        if verifier.otp == data:
            verifier.status = True
            verifier.save()
            messages.success(request, 'Verification successful. Enjoy the services!')
        else:
            messages.error(request, 'OTP verification failed - Wrong OTP.')
        return HttpResponse('Verification failed...')

    demand_form = AskFor()
    offering_form = Offer()

    latest_ongoing_deals = Deal.objects.all()[0:6]
    categories = Offering.objects.values_list('category', flat=True).distinct()

    notifications = Notification.objects.filter(parent=request.user.id, seen=False)

    return render(request, 'index.html', {"index_token": True, 'demand_form': demand_form, 'offering_form': offering_form, "deals": latest_ongoing_deals, 'categories': categories[:11], 'notifications': notifications})


@csrf_exempt
def clear_notifs(request):
    if request.method == 'POST':
        # Get the raw data from POST request
        raw_data = request.body.decode('utf-8')
        # Parse the JSON data into a Python dictionary
        data = json.loads(raw_data)
        # Extract notification IDs from the dictionary keys
        notification_ids = list(data["this_user_notification_ids"].values())
        for id in notification_ids:
            n = Notification.objects.get(id=int(id))
            n.seen = True
            n.save()
        return HttpResponse("Cleared Notifications...")


def register(request):
    if request.method == 'POST':
        fname = request.POST.get('fname', '')
        lname = request.POST.get('lname', '')

        email = request.POST.get('email', '')
        if '@lpu.in' not in email:
            messages.error(request, 'You can only register through your university email id.')
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
                otp = send_otp(email)
                verifier = OtpVerification()
                verifier.parent = request.user.id
                verifier.otp=otp
                verifier.save()
                
                login(request, user)
 
                messages.success(request, f'Account created successfully! An OTP has sent to your registered email, you will need that otp to verify your account. Note your username: "{username}"\nNote: Verification is useful for User security.')
                return redirect(f'/')

        except Exception as e:
            messages.error(request, f"Account already exists: {e}.")
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
    return otp


@csrf_exempt
def profile(request):
    if request.method == "POST":
        if request.content_type == 'application/json':
            raw_data = request.body.decode('utf-8')
            data = json.loads(raw_data)
            notif_id = data['notif_id']

            this_notif = Notification.objects.get(id = int(notif_id))
            this_notif.clicked = True
            this_notif.save()
            return HttpResponse('Notification clicked...')

        deal_id = request.POST.get('dealId')
        grievance_form = PutGrievance(data=request.POST, files=request.FILES)

        if grievance_form.is_valid():
            grievance_instance = grievance_form.save(commit=False)
            grievance_instance.deal = Deal.objects.get(id=int(deal_id))
            grievance_instance.save()
            grievance_instance.defaulter = User.objects.get(id = grievance_instance.deal.borrower)
            grievance_instance.save()

            griev_count = OtpVerification.objects.get(parent=User.objects.get(id = grievance_instance.deal.borrower))
            griev_count.grievance_count+=1
            griev_count.save()

            new_notification = Notification(parent=User.objects.get(id = grievance_instance.deal.borrower), associated_url=f'/profile/#my_character', about=f'You have a complaint from {grievance_instance.deal.lender.username}')
            new_notification.save()
            
            messages.success(request, "Complaint has been sent.")

        return redirect('/profile')

    if not request.user.is_authenticated:
        messages.info(request, 'Register or login to enjoy services!')
        return render(request, 'verify.html', {'registeration_required': True})

    verifier = OtpVerification.objects.get(parent=request.user.id)
    if not verifier.status:
        messages.info(reqeust, 'Kindly verify your account with the OTP sent to your university email...')
        return render(request, 'verify.html')

    notifications = Notification.objects.filter(parent=request.user.id, seen=False)
    borrowings = Deal.objects.filter(borrower=request.user.id)
    lending_deals = Deal.objects.filter(lender=request.user.id)
    lendings = [[i, User.objects.get(id=i.borrower)] for i in lending_deals]
    grievances = Grievance.objects.filter(defaulter=request.user.id, resolved=False)

    grievance_form = PutGrievance()

    parameters = {'notifications': notifications, 'borrowings': borrowings, 'lendings': lendings, 'grievance_form': grievance_form, 'grievances': grievances}
    return render(request, 'profile.html', parameters)


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


def logoutHandle(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect('/')
    else:
        messages.info(request, "No user has logged in yet")
        return redirect('/')


def handle_payment(request):
    if request.method=='POST':
        g_id = request.POST.get('grievance_id')
        g_id = int(g_id)
        related_grievance = Grievance.objects.get(id=g_id)

        # payment gateway code starts here-----
        client = razorpay.Client(auth=('rzp_test_RHVvhCMiKWJeS1', '8IjZtvP0v4SNjhfZzLgSNQFI'))

        response_payment = client.order.create(dict(amount=related_grievance.deal.item.price*100, currency='INR'))

        if response_payment['status'] == 'created':
            if len(Payment.objects.filter(for_grievance=related_grievance.id)) != 0:
                Payment.objects.filter(for_grievance=related_grievance).delete()

            Payment(for_grievance=related_grievance, razorpay_order_id=response_payment['id']).save()
        # payment gateway code ends here-----
            
            return render(request, 'handle_payment.html', {'payment': response_payment, 'g_id': g_id})
            
        messages.error(request, 'We are unable to process the payment right now. Please try again after sometime.')
        return redirect('/profile')
    return redirect('/')

@csrf_exempt
def verify_payment(request):
    if request.method=='POST':
        response = request.POST
        # print(response)

        client = razorpay.Client(auth=('rzp_test_RHVvhCMiKWJeS1', '8IjZtvP0v4SNjhfZzLgSNQFI'))

        try:
            client.utility.verify_payment_signature({
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature']
            })

            instance = Payment.objects.get(razorpay_order_id=response['razorpay_order_id'])
            instance.razorpay_payment_id = response['razorpay_payment_id']
            instance.razorpay_signature = response['razorpay_signature']
            instance.paid = True
            instance.save()

            g_id = request.POST.get("grievance_id")
            u_id = request.POST.get("user_id")
            
            related_grievance = Grievance.objects.get(id=int(g_id))
            
            related_grievance.resolved = True
            related_grievance.save()

            g_count = OtpVerification.objects.get(parent=int(u_id))
            g_count.grievance_count-=1
            g_count.save()

            messages.success(request, f'Your complaint of {related_grievance.deal.item.name} from {related_grievance.deal.lender.username} has been resolved. Net amount payed: {related_grievance.deal.item.price}')

            return redirect('/')
        except Exception as e:
            messages.error(request, f"Your payment failed unexpectedly. Don't worry! your money is safe - Error: {e}")
            return redirect('/profile')
    return redirect('/')

# razorpay test card number (master card): 5267 3181 8797 5449


