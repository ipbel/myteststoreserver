from django.urls import path

from orders.views import (CancelOrderView, OrderCreateView, OrderDetailView,
                          OrdersListView, OrderSuccessView)

app_name = 'orders'

urlpatterns = [
    path('', OrdersListView.as_view(), name='orders'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order'),
    path('order-create/', OrderCreateView.as_view(), name='order-create'),
    path('order-success/', OrderSuccessView.as_view(), name='order-success'),
    path('order-cancel/', CancelOrderView.as_view(), name='order-cancel'),
]
