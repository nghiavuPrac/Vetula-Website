from django.shortcuts import get_object_or_404, redirect
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.views.decorators.csrf import csrf_exempt
from django.dispatch import receiver
from .models import Profile


# @csrf_exempt
# @receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn = sender

    if ipn.payment_status == ST_PP_COMPLETED:
        # payment was successful
        invoice = ipn.invoice
        user_profile = get_object_or_404(Profile, id=invoice.split("-")[0])
        user_profile.purchase = True
        user_profile.save()
        return redirect("user")



valid_ipn_received.connect(payment_notification)