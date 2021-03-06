from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import OrderForm
from .models import Order
from .utility import create_order_from_shopping_basket, update_user_profile_from_order
from django.contrib.auth.models import User

import json
import stripe
import time



class Stripe_WebHook_Handler:
    """
    Handles and processes the stripe webhook request.
    """

    def __init__(self, request, endpoint_secret):
        self.request = request
        self.endpoint_secret = endpoint_secret
        # Dictionary of the events we handle
        self.event_handlers = {
            'payment_intent.succeeded': self.handle_payment_intent_succeeded,
            'payment_intent.payment_failed': self.handle_payment_intent_payment_failed,
        }


    def process_request(self):
        """ Processes each request, and calls the appropriate handler """
        event = None

        try:
            event = stripe.Webhook.construct_event(
                self.request.body,
                self.request.META['HTTP_STRIPE_SIGNATURE'],
                self.endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        event_handler = self.event_handlers.get(event.type, self.unhandled_event)

        return event_handler(event)


    def handle_payment_intent_succeeded(self, event):
        """ Handles a successfll payment """
        payment_intent = event.data.object

        for attempt in range(5):
            try:
                order = Order.objects.get(stripe_payment_id=payment_intent.id)
            except Order.DoesNotExist:
                # We did not find the order in this attempt
                time.sleep(1)
                continue

            # We found the order
            order.status = 'paid'
            order.save()

            self._send_confirmation_email(order)

            return HttpResponse(status=200)

        # We did not find the order at all - We must create it

        # Create the order form from the payment intent data
        billing_details = payment_intent.charges.data[0].billing_details
        shipping_details = payment_intent.shipping

        order_form = OrderForm(
            {
                'full_name': billing_details.name,
                'email': billing_details.email,
                'phone_number': billing_details.phone,
                'gift_message': payment_intent.metadata.gift_message,
                'payment_street_address1': billing_details.address.line1,
                'payment_street_address2': billing_details.address.line2,
                'payment_town_or_city': billing_details.address.city,
                'payment_county': billing_details.address.state,
                'payment_postcode': billing_details.address.postal_code,
                'payment_country': billing_details.address.country,
                'shipping_full_name': shipping_details.name,
                'shipping_street_address1': shipping_details.address.line1,
                'shipping_street_address2': shipping_details.address.line2,
                'shipping_town_or_city': shipping_details.address.city,
                'shipping_county': shipping_details.address.state,
                'shipping_postcode': shipping_details.address.postal_code,
                'shipping_country': shipping_details.address.country,
            }
        )

        # Find the user
        user = None
        if payment_intent.metadata.user_id:
            try:
                user = User.objects.get(id=payment_intent.metadata.user_id)
            except User.DoesNotExist:
                pass

        # Creating the order from the order form and the shopping basket
        try:
            order = create_order_from_shopping_basket(
                json.loads(payment_intent.metadata.shopping_basket),
                order_form,
                payment_intent.id,
                user,
            )

            if payment_intent.metadata.save_user_info:
                update_user_profile_from_order(order)

            # Log the order as having been paid
            order.status = 'paid'
            order.save()

            self._send_confirmation_email(order)

        except Product.DoesNotExist as error:
            # This situation should never happen
            # Sending the details to ourselves so we can follow up
            send_mail(
                f'Error while processing payment intent: {payment_intent_id}',
                error,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL]
            )

            return HttpResponse(status=500)

        return HttpResponse(status=200)


    def handle_payment_intent_payment_failed(self, event):
        """ Handles a failed payment """
        payment_intent = event.data.object

        for attempt in range(5):
            try:
                order = Order.objects.get(stripe_payment_id=payment_intent.id)
            except Order.DoesNotExist:
                # We did not find the order in this attempt
                time.sleep(1)
                continue

            # We found the order
            order.status = 'payment_failed'
            order.save()

            return HttpResponse(status=200)

        # We did not find the order at all
        # Intentionally sent status code 500 to get Stripe to retry later
        return HttpResponse(status=500)


    def unhandled_event(self, event):
        """ Any unhandled event """
        # print(event.type, event)
        return HttpResponse(status=200)

    def _send_confirmation_email(self, order):
        """ Send the user a confirmation email """

        # Establish whether the user has pourchased an audio or e book
        bought_audiobook = False
        bought_ebook = False

        for lineitem in order.lineitems.all():
            if lineitem.product.product_type == 'e_book':
                bought_ebook = True
            elif lineitem.product.product_type == 'audio_book':
                bought_audiobook = True

        try:
            email_body = render_to_string(
                'checkout/text_templates/confirmation_email_body.txt',
                {
                    'order': order,
                    'contact_email': settings.DEFAULT_FROM_EMAIL,
                    'bought_audiobook': bought_audiobook,
                    'bought_ebook': bought_ebook,
                }
            )

            send_mail(
                f'[Order : {order.order_number}] Payment Recieved',
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [order.email]
            )
        except Exception as e:
            # Print here as we can't do anything with it in the webhook
            print('error: ', e)
