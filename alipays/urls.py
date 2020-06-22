from django.urls import path

from alipays.views import OrderALIPayView, OrderALIPayResultView

urlpatterns = [
    path('order_alipay/', OrderALIPayView.as_view(), name='order_alipay'),
    path('ali_pay_result/', OrderALIPayResultView.as_view(), name='ali_pay_result'),
]