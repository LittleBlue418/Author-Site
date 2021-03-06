from django.db import models
from django_countries.fields import CountryField

from products.models import Product
from profiles.models import UserProfile

import uuid


class Order(models.Model):
    """ Class for a customer's order """

    _STATUS = [
        ('submitted', 'Submitted'),
        ('paid', 'Paid'),
        ('payment_failed', 'Payment Failed'),
        ('shipped', 'Shipped'),
    ]

    class Meta:
        ordering = ['-date']

    # Basic order info
    order_number = models.CharField(max_length=32, editable=False)
    date = models.DateTimeField(auto_now_add=True)
    stripe_payment_id = models.CharField(max_length=254, blank=False, unique=True)
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    status = models.CharField(choices=_STATUS, max_length=20)

    # Customer Info
    full_name = models.CharField(max_length=50, blank=False)
    email = models.CharField(max_length=254, blank=False)
    phone_number = models.CharField(max_length=20, blank=False)

    # If Gift
    gift_message = models.TextField(max_length=500, blank=True, default='')

    # Payment details
    payment_street_address1 = models.CharField(max_length=80, blank=False)
    payment_street_address2 = models.CharField(max_length=80, blank=True)
    payment_town_or_city = models.CharField(max_length=40, blank=False)
    payment_county = models.CharField(max_length=80, blank=True)
    payment_postcode = models.CharField(max_length=20, blank=True)
    payment_country = CountryField(blank_label='Country *', blank=False)

    # Shipping details
    shipping_full_name = models.CharField(max_length=50, blank=False)
    shipping_street_address1 = models.CharField(max_length=80, blank=False)
    shipping_street_address2 = models.CharField(max_length=80, blank=True)
    shipping_town_or_city = models.CharField(max_length=40, blank=False)
    shipping_county = models.CharField(max_length=80, blank=True)
    shipping_postcode = models.CharField(max_length=20, blank=True)
    shipping_country = CountryField(blank_label='Country *', blank=False)

    def price_total(self):
        """ Calculate Order item price total """
        total = 0
        for lineitem in self.lineitems.all():
            total += lineitem.price_total()

        return total

    def shipping_total(self):
        """ Calculate Order shipping total """
        total = 0
        for lineitem in self.lineitems.all():
            total += lineitem.shipping_total()

        return total

    def grand_total(self):
        """ Calculate Order grand total """
        total = 0
        for lineitem in self.lineitems.all():
            total += lineitem.grand_total()

        return total

    def _generate_order_number(self):
        """ Generate a random, unique order number using UUID """
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """
        On order save, if there isn't an order number we generate
        one and save it to the order.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    """ Class for each item in the order """
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)
    shipping = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def price_total(self):
        """ Calculate lineitem item price total """
        if self.price is None:
            return 0
        return self.price * self.quantity


    def shipping_total(self):
        """ Calculate lineitem shipping total """
        if self.shipping is None:
            return 0
        return self.shipping * self.quantity

    def grand_total(self):
        """ Calculate lineitem grand total """
        return self.price_total() + self.shipping_total()
