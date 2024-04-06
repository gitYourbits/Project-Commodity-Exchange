from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import ChatBox, Demand, Offering, Deal, Grievance, Notification, OtpVerification
from lendIt.form import Offer, AskFor
from django.views.decorators.csrf import csrf_exempt
import json


def index(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Register or login to enjoy services!')
        return render(request, 'verify.html', {'registeration_required': True})

    verifier = OtpVerification.objects.get(parent=request.user.id)
    if not verifier.status:
        messages.info(reqeust, 'Kindly verify your account with the OTP sent to your university email...')
        return render(request, 'verify.html')
    if verifier.grievance_count>0:
        messages.warning(request, 'You have complaints from users. Your account is blocked untill you resolve them.')    
        return redirect('/profile')
    return redirect('/community/borrow')


def chats(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Register or login to enjoy services!')
        return render(request, 'verify.html', {'registeration_required': True})

    verifier = OtpVerification.objects.get(parent=request.user.id)
    if not verifier.status:
        messages.info(reqeust, 'Kindly verify your account with the OTP sent to your university email...')
        return render(request, 'verify.html')

    checker = ChatBox.objects.filter(sender=request.user)
    checker = [i for i in checker]
    if len(ChatBox.objects.filter(receiver=request.user.id))!=0:
        checker.append(ChatBox.objects.filter(receiver=request.user.id)[0])
    if len(checker) == 0:
        messages.info(request, "you don't have any chats available yet!")
        return redirect('/')
    room = checker[0].room.split('-')
    return redirect(f'/community/deal/{room[0]}by{room[1]}/ongoing')


def borrow(request):
    if request.method=='POST':
        offering_form = Offer(data=request.POST, files=request.FILES)
        if offering_form.is_valid():
            offering_instance = offering_form.save(commit=False)
            offering_instance.lender = request.user
            offering_instance.save()

            messages.success(request, 'Your offer has been posted successfully! Here are more demands that you may fulfill.')
        return redirect('/community/lend')

    if not request.user.is_authenticated:
        messages.info(request, 'Register or login to enjoy services!')
        return render(request, 'verify.html', {'registeration_required': True})

    verifier = OtpVerification.objects.get(parent=request.user.id)
    if not verifier.status:
        messages.info(reqeust, 'Kindly verify your account with the OTP sent to your university email...')
        return render(request, 'verify.html')
    if verifier.grievance_count>0:
        messages.warning(request, 'You have complaints from users. Your account is blocked untill you resolve them.')    
        return redirect('/profile')

    categories = Offering.objects.values('category').distinct()
    offerings = {}
    # Iterate over distinct categories
    for category in categories:
        # Filter products by the current category
        category_wise_items = Offering.objects.filter(category=category['category']).exclude(lender=request.user.id)
        # Store the products in the dictionary with the category name as key
        offerings[category['category']] = category_wise_items
    return render(request, 'community/borrow.html', {"borrow_token": True, "offerings": offerings, "notifications": Notification.objects.filter(parent=request.user.id, seen=False)})


def lend(request):
    if request.method=='POST':
        demand_form = AskFor(data=request.POST, files=request.FILES)
        if demand_form.is_valid():
            demand_instance = demand_form.save(commit=False)
            demand_instance.borrower = request.user
            demand_instance.save()
            messages.success(request, 'Your demand has been posted! Here are some offers that you may like.')
        return redirect('/community/borrow')

    if not request.user.is_authenticated:
        messages.info(request, 'Register or login to enjoy services!')
        return render(request, 'verify.html', {'registeration_required': True})

    verifier = OtpVerification.objects.get(parent=request.user.id)
    if not verifier.status:
        messages.info(reqeust, 'Kindly verify your account with the OTP sent to your university email...')
        return render(request, 'verify.html')
    if verifier.grievance_count>0:
        messages.warning(request, 'You have complaints from users. Your account is blocked untill you resolve them.')    
        return redirect('/profile')

    categories = Demand.objects.values('category').distinct()
    demands = {}
    # Iterate over distinct categories
    for category in categories:
        # Filter products by the current category
        category_wise_items = Demand.objects.filter(category=category['category']).exclude(borrower=request.user.id)
        # Store the products in the dictionary with the category name as key
        demands[category['category']] = category_wise_items
    return render(request, 'community/lend.html', {"lend_token": True, "demands": demands, "notifications": Notification.objects.filter(parent=request.user.id, seen=False)})


@csrf_exempt
def dealing(request, id):
    if request.method == "POST":
        raw_data = request.body.decode('utf-8')
        data = json.loads(raw_data)
        notif_id = data['notif_id']

        this_notif = Notification.objects.get(id = int(notif_id))
        this_notif.clicked = True
        this_notif.save()

        return HttpResponse('Notification clicked...')

    if not request.user.is_authenticated:
        messages.info(request, 'Register or login to enjoy services!')
        return render(request, 'verify.html', {'registeration_required': True})

    verifier = OtpVerification.objects.get(parent=request.user.id)
    if not verifier.status:
        messages.info(reqeust, 'Kindly verify your account with the OTP sent to your university email...')
        return render(request, 'verify.html')

    id_stored = id
    id=id.split('by')
    offer = Offering.objects.filter(id=int(id[0]))[0]
    lender = offer.lender

    if request.user.id == lender.id:
        username = User.objects.filter(id=int(id[-1]))[0].username
        msg_notification_receiver = int(id[-1])
    else:
        username = lender.username
        msg_notification_receiver = lender.id

    room_name = f'{id[0]}-{id[-1]}-{lender.id}' # offering-borrower-lender //always
    messages = ChatBox.objects.filter(room=room_name)
    item = Offering.objects.filter(id=int(id[0]))[0]

    msgs1 = ChatBox.objects.filter(receiver = request.user.id)
    msgs2 = ChatBox.objects.filter(sender = request.user.id)
    msgsCombined = list(set(msgs1) | set(msgs2))

    chats = {}
    # Categorize chats based on the room attribute
    for msg in msgsCombined:
        room = msg.room
        if room not in chats:
            chats[room] = []
        chats[room].append(msg)

    chats_sorted = sorted(chats.items(), key=lambda x: max(x[1], key=lambda msg: msg.timeStamp).timeStamp, reverse=True)

    chats = dict(chats_sorted)

    for room, chat in chats.items():
        chat = sorted(chat, key=lambda msg: msg.timeStamp, reverse=True)
        getting_room_url = chat[0].room.split('-')
        
        chats[room] = [chat[0], chat[0].sender if request.user.id!=chat[0].sender.id else User.objects.filter(id=chat[0].receiver)[0], f"{getting_room_url[0]}by{getting_room_url[1]}", Offering.objects.filter(id=int(getting_room_url[0]))[0]]

    return render(request,'community/dealing.html', {'room_name': room_name, 'msgs': messages[::-1], 'username': username, 'id': id_stored, 'notification_receiver': msg_notification_receiver, 'chats': chats, 'item': item, 'chats_token': True, 'notifications': Notification.objects.filter(parent=request.user.id, seen=False), 'borrower_is_defaulter': len(Grievance.objects.filter(defaulter=int(id[-1]), resolved=False))>0 or len(Grievance.objects.filter(defaulter=lender.id, resolved=False))>0})


def deal(request, id):
    if not request.user.is_authenticated:
        messages.info(request, 'Register or login to enjoy services!')
        return render(request, 'verify.html', {'registeration_required': True})

    verifier = OtpVerification.objects.get(parent=request.user.id)
    if not verifier.status:
        messages.info(reqeust, 'Kindly verify your account with the OTP sent to your university email...')
        return render(request, 'verify.html')
    if verifier.grievance_count>0:
        messages.warning(request, 'You have complaints from users. Your account is blocked untill you resolve them.')    
        return redirect('/profile')

    deal = Deal.objects.filter(id=int(id))[0]
    return render(request, 'community/deal.html', {'deal': deal, 'notifications': Notification.objects.filter(parent=request.user.id, seen=False), 'borrower': User.objects.get(id=deal.borrower)})


def closing_deal(request, id):
    if not request.user.is_authenticated:
        messages.info(request, 'Register or login to enjoy services!')
        return render(request, 'verify.html', {'registeration_required': True})

    verifier = OtpVerification.objects.get(parent=request.user.id)
    if not verifier.status:
        messages.info(reqeust, 'Kindly verify your account with the OTP sent to your university email...')
        return render(request, 'verify.html')
    if verifier.grievance_count>0:
        messages.warning(request, 'You have complaints from users. Your account is blocked untill you resolve them.')    
        return redirect('/profile')

    id = id.split('by')
    item = Offering.objects.filter(id=int(id[0]))[0]
    deal = Deal(lender = item.lender, borrower=int(id[-1]), item=item, price=item.price)
    deal.save()
    return redirect('/community/deal/{}/closed'.format(deal.id))


def create_offering(request, id):
    if not request.user.is_authenticated:
        messages.info(request, 'Register or login to enjoy services!')
        return render(request, 'verify.html', {'registeration_required': True})

    verifier = OtpVerification.objects.get(parent=request.user.id)
    if not verifier.status:
        messages.info(reqeust, 'Kindly verify your account with the OTP sent to your university email...')
        return render(request, 'verify.html')
    if verifier.grievance_count>0:
        messages.warning(request, 'You have complaints from users. Your account is blocked untill you resolve them.')    
        return redirect('/profile')

    id=int(id)
    demand = Demand.objects.filter(id=id)[0]

    offering = Offering.objects.filter(lender=request.user, name=demand.name)

    if len(offering)==0:
        offering = Offering(lender = request.user, name = demand.name, category=demand.category, description=demand.description, price=demand.price, image=demand.image)
        offering.save()

        notification = Notification(parent=demand.borrower, associated_url=f'/community/deal/{offering.id}by{demand.borrower.id}/ongoing/', about=f'You have an offering from {offering.lender.username}')
        notification.save()

        return redirect(f'/community/deal/{offering.id}by{demand.borrower.id}/ongoing')
    return redirect(f'/community/deal/{offering[0].id}by{demand.borrower.id}/ongoing')

