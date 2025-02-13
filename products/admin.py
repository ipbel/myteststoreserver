from django.contrib import admin

from products.models import Baskets, Product, ProductCategory

admin.site.register(ProductCategory)


@admin.register(Baskets)
class BasketsAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'quantity')


@admin.action(description="Update obj")
def objects_updates(modeladmin, request, queryset):
    for obj in queryset:
        obj.save()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'stripe_product_price_id')
    search_fields = ('name',)
    fields = ('image', 'name', ('quantity', 'price'), 'description', 'stripe_product_price_id', 'category')
    actions = [objects_updates]


class BasketAdmin(admin.TabularInline):
    model = Baskets
    fields = ('product', 'quantity', 'created_timestamp')
    readonly_fields = ('created_timestamp',)
    extra = 0
