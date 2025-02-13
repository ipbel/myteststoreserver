import stripe
from django.conf import settings
from django.db import models

from user.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductCategory(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Product(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    stripe_product_price_id = models.CharField(max_length=128, null=True, blank=True)
    image = models.ImageField(upload_to='products_images')
    category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f"Product: {self.name} | Category: {self.category}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.stripe_product_price_id:
            stripe_product_price = self.create_stripe_product_price()
            self.stripe_product_price_id = stripe_product_price.id
        super(Product, self).save(force_insert=False, force_update=False, using=None, update_fields=None)

    def create_stripe_product_price(self):
        stripe_product = stripe.Product.create(name=self.name)
        stripe_product_price = stripe.Price.create(
            product=stripe_product['id'],
            unit_amount=round(self.price * 100),
            currency='RUB',
        )
        return stripe_product_price


class BasketQuerySet(models.QuerySet):
    def total_sum(self):
        return sum(basket.sum() for basket in self)

    def total_products(self):
        return len(self)

    def baskets_line_items_create(self):
        line_items = []
        for basket in self:
            item = {
                'price': basket.product.stripe_product_price_id,
                'quantity': basket.quantity,
            }
            line_items.append(item)
        return line_items


class Baskets(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    objects = BasketQuerySet.as_manager()

    class Meta:
        verbose_name = 'Basket'

    def __str__(self):
        return f"User: {self.user} | Product: {self.product} | Quantity: {self.quantity}"

    def sum(self):
        return self.product.price * self.quantity

    def baskets_length(self):
        return len(self.product)

    def de_json(self):
        basket_item = {
            'product_name': self.product.name,
            'quantity': self.quantity,
            'price': float(self.product.price),
            'sum': float(self.sum()),
        }
        return basket_item
