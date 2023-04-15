from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from foodapp_main import settings

from order.utils import create_order_and_orderedItems

stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.
@csrf_exempt
def webhook(request):
    endpoint_secret = 'whsec_e745e0d59b412f2456462571d24d800bfd114734e658a9ec4b00a2b65e5dc2f0'
    event = None
    payload = request.body
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event['type'] == 'payment_intent.created':
        payment_intent = event['data']['object']
        # print(payment_intent)
        
    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
    elif event['type'] == 'payment_intent.amount_capturable_updated':
        payment_intent = event['data']['object'] 
        if payment_intent.status == 'requires_capture':
            create_order_and_orderedItems( transaction_id=payment_intent.id, 
                                            payment_method='Stripe',  
                                            status='Payment Authorised',
                                            metadata=payment_intent.metadata
                                          )

        
    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event['type']))
    
    
    return JsonResponse({"success" : True})