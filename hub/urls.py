#hub/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.demo, name='demo'),
    path('home/', views.index, name='home'),
    
    # Authentication
    path('register/', views.register_user, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # Cars
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    
    # Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:pk>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_history, name='order_history'),
    
    # Services
    path('services/book/', views.book_service, name='book_service'),
    path('services/', views.my_bookings, name='my_bookings'),
    
    # Jobs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/apply/<int:pk>/', views.apply_job, name='apply_job'),
    path('jobs/my-applications/', views.my_applications, name='my_applications'),
    path('jobs/create/', views.create_job_vacancy, name='create_job_vacancy'),

    path('buy_now/<int:pk>/', views.buy_now, name='buy_now'),
    
    # Other pages
    path('news/', views.news, name='news'),
    path('products/', views.products, name='products'),

    #ml prediction page
    path('predict/', views.predict_price, name='predict_price'),
] 