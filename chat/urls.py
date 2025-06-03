from django.urls import path
from . import views
app_name = 'chat'

urlpatterns = [
    # path('contact_seller/<int:car_id>', views.contact_seller, name='contact_seller'),
    # path('my_received_messages/', views.my_received_messages, name='my_received_messages'),
    # path('my_sent_messages/', views.my_sent_messages, name='my_sent_messages'),
    path('chat/<int:car_id>/<int:user_id>/', views.chat_view, name='chat_view'),

]


