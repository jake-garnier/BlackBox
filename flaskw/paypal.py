from paypalrestsdk import Payment
from paypalrestsdk import Authorization
from flask import redirect, flash, jsonify
import paypalrestsdk
from flaskw import db


# def create_payment(amount, denomination="USD", description="Contract Payment"):
#     payment = Payment({
#         "intent": "authorize",

#         # Set payment method
#         "payer": {
#             "payment_method": "paypal"
#         },

#         # Set redirect urls
#         "redirect_urls": {
#             "return_url": "http://127.0.0.1:5000/table",
#             "cancel_url": "http://127.0.0.1:5000/table"
#         },

#         # Set transaction object
#         "transactions": [{
#             "amount": {
#             "total": str(amount),
#             "currency": denomination
#             },
#             "description": description
#         }]
#     })

#     # Create payment
#     if payment.create():
#         # Extract redirect url
#         for link in payment.links:
#             if link.method == "REDIRECT":
#                 # Capture redirect url
#                 redirect_url = str(link.href)

#                 # REDIRECT USER to redirect_url
#                 redirect(redirect_url)
#     else:
#         flash("Error while creating payment:")
#         flash(payment.error)

#     flash(str(payment.links))

def configure():
    paypalrestsdk.configure({
        'mode': 'sandbox', #sandbox or live
        'client_id': 'Ae25aMoBv7uZfZP0b3OG4_-W3ffiBuVU774srA0yYqq_8_MvbI4cV_fNsoDraE-vzP-_DxPg8NPl7Zye',
        'client_secret': 'EE0KgZwfsx4VtLRj0DDhJzH8rw_uWw1Sb2F-VLUB3h0rGidtYF9suXh20NeelMnBG4iZFY7eEOcJsznn' }
    )

def create_payment(request):

    contract = db.get_contract(request.form['contractID'])

    payment = paypalrestsdk.Payment({
        "intent": "authorize",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",
            "cancel_url": "http://localhost:3000/"},
        "transactions": [{
            "amount": {
                "total": str(contract['payout']),
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        print('Payment success!')
    else:
        print(payment.error)

    return jsonify({'paymentID' : payment.id})

def execute_payment(request):
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id' : request.form['payerID']}):
        print('Execute success!')
        success = True
    else:
        print(payment.error)

    return jsonify({'success' : success})