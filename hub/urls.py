from django.urls import path
from . import views


urlpatterns = [
    # path('home', views.home, name='home'),
    path('home', views.index, name='home'),
    path('', views.demo, name='demo'),

    path('register/', views.register_user, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),

    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('add-to-cart/<int:car_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('buy_now/<int:car_id>/', views.buy_now, name='buy_now'),
    path('process-order/', views.process_order, name='process_order'),
    path('payment/', views.payment, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('checkout/', views.checkout, name='checkout'),
    # path('remove-from-cart/<int:car_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('book-service/', views.book_service, name='book_service'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),

    path('jobs/', views.job_list, name='job_list'),
    path('jobs/apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('jobs/create/', views.create_job_vacancy, name='create_job_vacancy'),
    path('news/', views.news, name='news'),
    path('products/', views.products, name='products'),






]
