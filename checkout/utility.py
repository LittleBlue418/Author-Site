from .forms import OrderForm
from .models import OrderLineItem
from products.models import Product


def order_form_from_request(post_data):
    """
    A function to create an order form instance from request data,
    expects a dictionary from the request data.
    """

    # Check use card address as shipping address
    if post_data.get('use-card-address-as-shipping-address') == 'on':

        # Populate shipping address fields with payment address details
        shipping_mapping = {
            'shipping_full_name': 'full_name',
            'shipping_street_address1': 'payment_street_address1',
            'shipping_street_address2': 'payment_street_address2',
            'shipping_town_or_city': 'payment_town_or_city',
            'shipping_country': 'payment_country',
            'shipping_postcode': 'payment_postcode',
            'shipping_county': 'payment_county',
        }

        for shipping_field, payment_field in shipping_mapping.items():
            post_data[shipping_field] = post_data[payment_field]

    # Creating the order form for validation
    order_form = OrderForm(post_data)

    return order_form


def extract_payment_intent_id(client_secret):
    """ Extracts the payment id from the client secret """
    return client_secret.split('_secret')[0]


def create_order_from_shopping_basket(
    shopping_basket,
    order_form,
    payment_intent_id,
    user
):
    """ Creates an order with line items from the shopping basket """

    order_lines = []

    for product_id, amount in shopping_basket.items():

        product = Product.objects.get(id=product_id)
        order_lines.append(OrderLineItem(
            product=product,
            quantity=amount,
            price=product.price,
            shipping=product.shipping,
        ))

    order = order_form.save(commit=False)
    order.stripe_payment_id = payment_intent_id

    if user.is_authenticated:
        order.user_profile = user.profile

    order.status = 'submitted'
    order.save()

    for order_line in order_lines:
        order_line.order = order
        order_line.save()

    return order


def update_user_profile_from_order(order):
    """
    Saves the order card address to the users default address
    on their profile.
    """
    profile = order.user_profile

    if not profile:
        return

    profile.default_street_address1 = order.payment_street_address1
    profile.default_street_address2 = order.payment_street_address2
    profile.default_town_or_city = order.payment_town_or_city
    profile.default_county = order.payment_county
    profile.default_postcode = order.payment_postcode
    profile.default_country = order.payment_country

    profile.save()
