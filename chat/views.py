from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Car, Message
from django.contrib.auth.models import User


# Create your views here.
# @login_required
# def contact_seller(request, car_id):
#     car = get_object_or_404(Car, id=car_id)
#     seller = car.seller

#     if request.method == 'POST':
#         form = MessageForm(request.POST)
#         if form.is_valid():
#             message = form.save(commit=False)
#             message.sender = request.user
#             message.receiver = seller
#             message.car = car
#             message.save()
#             return redirect('my_sent_messages')
#     else:
#         form = MessageForm()

#     return render(request, 'chat/contact_seller.html', {
#         'form': form,
#         'car': car,
#         'seller': seller
#     })


# @login_required
# def my_received_messages(request):
#     messages = Message.objects.filter(receiver=request.user).order_by('-sent_at')
#     return render(request, 'chat/received.html', {'messages': messages})

# @login_required
# def my_sent_messages(request):
#     messages = Message.objects.filter(sender=request.user).order_by('-sent_at')
#     return render(request, 'chat/sent.html', {'messages': messages})


@login_required
def chat_view(request, car_id, user_id):
    car = get_object_or_404(Car, id=car_id)
    other_user = get_object_or_404(User, id=user_id)

    messages = Message.objects.filter(
        car=car,
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                car=car,
                content=content
            )
            return redirect('chat:chat_view', car_id=car.id, user_id=other_user.id)

    return render(request, 'chat/chat_room.html', {
        'car': car,
        'other_user': other_user,
        'messages': messages
    })