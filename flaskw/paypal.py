from paypalrestsdk import Payment
from paypalrestsdk import Authorization
from flask import redirect, flash


def create_payment(amount, denomination="USD", description="Contract Payment"):
    payment = Payment({
        "intent": "authorize",

        # Set payment method
        "payer": {
            "payment_method": "paypal"
        },

        # Set redirect urls
        "redirect_urls": {
            "return_url": "http://127.0.0.1:5000/table",
            "cancel_url": "http://127.0.0.1:5000/table"
        },

        # Set transaction object
        "transactions": [{
            "amount": {
            "total": str(amount),
            "currency": denomination
            },
            "description": description
        }]
    })

    # Create payment
    if payment.create():
        # Extract redirect url
        for link in payment.links:
            if link.method == "REDIRECT":
                # Capture redirect url
                redirect_url = str(link.href)

                # REDIRECT USER to redirect_url
                redirect(redirect_url)
    else:
        flash("Error while creating payment:")
        flash(payment.error)

    flash(str(payment.links))