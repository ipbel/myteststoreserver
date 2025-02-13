from django.db import models

from products.models import Baskets
from user.models import User


class Order(models.Model):
    CREATED = 0
    PAID = 1
    ON_WAY = 2
    DELIVERED = 3
    STATUSES = (
        (CREATED, 'Created'),
        (PAID, 'Paid'),
        (ON_WAY, 'On Way'),
        (DELIVERED, 'Delived'),
    )

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=256)
    address = models.CharField(max_length=256)
    basket_history = models.JSONField(default=dict)
    initiator = models.ForeignKey(to=User, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=STATUSES, default=CREATED)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id} {self.first_name} {self.last_name} {self.STATUSES[self.status][1]}'

    def after_payment(self):
        baskets = Baskets.objects.filter(user=self.initiator)
        self.status = self.PAID
        self.basket_history = {
            'total_sum': float(baskets.total_sum()),
            'purchased_items': [basket.de_json() for basket in baskets]
        }
        baskets.delete()
        self.save()
