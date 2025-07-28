from django.urls import path
from . import views 

app_name = "coins"

urlpatterns = [
    path("convert/", views.convert_coins, name="convert_coins"),
    path("clear/", views.clear_history, name="clear_history"),
    path("reset-balance/", views.reset_cash_balance, name="reset_balance"),
]