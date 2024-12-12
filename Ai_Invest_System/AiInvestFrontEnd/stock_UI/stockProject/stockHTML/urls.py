from django.urls import path
from . import views

urlpatterns = [
    path('login/today_stock/<str:stock_code>/', views.stock_detail, name='stock_detail'),
    path('login/', views.login, name='login'),
    path('login/today_stock/', views.today_stock, name='today_stock'),
    path('login/today_stock/get_today_stock_data/<int:page>/', views.get_today_stock_data, name='get_today_stock_data'),
    path('login/today_stock/get_today_stock_data/search_stocks/', views.search_stocks, name='search_stocks'),
    ]
