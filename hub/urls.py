# hub/urls.py
from django.urls import path
from . import views

app_name = 'hub'

urlpatterns = [
    path('', views.demo, name='demo'),
    path('home/', views.index, name='home'),
    
    # Authentication
    path('register/', views.register_user, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # Cars
    path('cars/', views.car_list, name='car_list'),
    path('new-cars/', views.new_car_list, name='new_car_list'),
    path('used-cars/', views.used_car_list, name='used_car_list'), # New URL for used cars
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('add-used-car/', views.add_used_car, name='add_used_car'),
    
    # Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:pk>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_history, name='order_history'),
    path('payment/',views.payment,name='payment'),
    path('payment_success/', views.payment_success, name='payment_success'),

    # Services
    # path('services/book/', views.book_service, name='book_service'),
    path('services/', views.my_bookings, name='my_bookings'),
    path('book-service/', views.book_service, name='book_service'),
    path('my-services/', views.my_service_bookings, name='my_service_bookings'),
    
    # Jobs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/apply/<int:pk>/', views.apply_job, name='apply_job'),
    path('jobs/my-applications/', views.my_applications, name='my_applications'),
    path('jobs/create/', views.create_job_vacancy, name='create_job_vacancy'),

    path('buy_now/<int:pk>/', views.buy_now, name='buy_now'),
    path('book-service-api/', views.book_service_api, name='book_service_api'),
    path('service-chatbot/', views.service_chatbot, name='service_chatbot'),


    #chat
    # path('my-chats/', views.my_chats, name='my_chats'),

    # pre-booking
    path('pre-book/<int:car_id>/', views.pre_book_car, name='pre_book_car'),
    path('my-prebookings/', views.my_prebookings, name='my_prebookings'),
    
    # Other pages
    path('news/', views.news, name='news'),
    path('products/', views.products, name='products'), # This should ideally be 'new_releases' or something similar

    #ml prediction page
    path('predict/', views.predict_price, name='predict_price'),
]