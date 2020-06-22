from django.urls import path

from wxpays.views import OrderWXPayView, WXPayResultView

urlpatterns = [
    path('order_wx_pay/', OrderWXPayView.as_view(), name='order_wx_pay'),
    path('wxpay_result/', WXPayResultView.as_view(), name='wxpay_result'),
]