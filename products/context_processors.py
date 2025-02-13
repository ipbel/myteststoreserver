from products.models import Baskets


def baskets(request):
    user = request.user
    return {'basket': Baskets.objects.filter(user=request.user) if user.is_authenticated else []}
