from django.urls import path
from . import views

urlpatterns = [
    path('login/today_stock/stock/<str:stock_code>/', views.stock_detail, name='stock_detail'),
    path('login/', views.login, name='login'),
    path('login/today_stock/', views.today_stock, name='today_stock'),
    ]
