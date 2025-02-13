import stripe
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from common.views import CommonMixin
from orders.forms import OrderForm
from orders.models import Order
from products.models import Baskets
from store.settings import DOMAIN_NAME, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_KEY

stripe.api_key = STRIPE_SECRET_KEY
endpoint_secret = STRIPE_WEBHOOK_KEY


class OrdersListView(CommonMixin, ListView):
    template_name = 'orders/orders.html'
    title = 'Orders'
    queryset = Order.objects.all()
    ordering = '-created'

    def get_queryset(self):
        queryset = super(OrdersListView, self).get_queryset()
        return queryset.filter(initiator=self.request.user)


class OrderDetailView(CommonMixin, DetailView):
    model = Order
    template_name = 'orders/order.html'

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['title'] = f'Store - order #{self.object.id}'
        return context


class OrderSuccessView(CommonMixin, TemplateView):
    template_name = 'orders/success.html'
    title = 'Success order'


class CancelOrderView(CommonMixin, TemplateView):
    template_name = 'orders/cancel.html'
    title = 'Cancel order'


class OrderCreateView(CommonMixin, CreateView):
    template_name = 'orders/order-create.html'
    form_class = OrderForm
    success_url = reverse_lazy('orders:order-create')
    title = 'Order Create'

    def form_valid(self, form):
        form.instance.initiator = self.request.user
        return super(OrderCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(OrderCreateView, self).get_context_data(**kwargs)
        context['baskets'] = Baskets.objects.filter(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        super(OrderCreateView, self).post(request, *args, **kwargs)
        baskets = Baskets.objects.filter(user=self.request.user)
        checkout_session = stripe.checkout.Session.create(
            line_items=baskets.baskets_line_items_create(),
            metadata={'order_id': self.object.id},
            mode='payment',
            success_url='{}{}'.format(DOMAIN_NAME, reverse('orders:order-success')),
            cancel_url='{}{}'.format(DOMAIN_NAME, reverse('orders:order-cancel')),
        )
        return HttpResponseRedirect(checkout_session.url, status=303)


def fulfill_checkout(session_id):
    print("Fulfilling Checkout Session", session_id)

    # Retrieve the Checkout Session from the API with line_items expanded
    checkout_session = stripe.checkout.Session.retrieve(
        session_id,
        expand=['line_items'],
    )
    print(session_id)
    order_id = int(checkout_session.metadata.order_id)
    order = Order.objects.get(id=order_id)
    order.after_payment()


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body

    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    if (
            event['type'] == 'checkout.session.completed'
            or event['type'] == 'checkout.session.async_payment_succeeded'
    ):
        fulfill_checkout(event['data']['object']['id'])

    return HttpResponse(status=200)
