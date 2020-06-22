
from django.urls import path

from unionpays.views import UnionpaysView, UniBackView, UniNotifyView

urlpatterns = [
    path('unionpay/', UnionpaysView.as_view(), name='unionpay'),
    path('uniback/', UniBackView.as_view(), name='uniback'),
    path('uninotify/', UniNotifyView.as_view(), name='uninotify'),
]