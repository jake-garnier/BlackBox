from paypalrestsdk import Payment
from paypalrestsdk import Authorization
from flask import redirect, flash, jsonify, url_for
import paypalrestsdk
from flaskw import db


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
            "payment_method": "paypal"
        },

        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",
            "cancel_url": "http://localhost:3000/"
        },

        "transactions": [{
            "amount": {
                "total": str(contract['payout']),
                "currency": "USD"},
            "description": "This is the payment transaction description."
        }]
    })

    if payment.create():
        print('Payment success!')
        return jsonify({'paymentID' : payment.id, 'success' : True})
    else:
        print(payment.error)
        return jsonify({'success' : False})

def execute_payment(request):

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id' : request.form['payerID']}):
        print('Execute success!')
        authorization_id = payment.transactions[0].related_resources[0].authorization.id
        db.add_authorization_id_to_contract(request.form['contractID'], authorization_id)
        return jsonify({'redirect' : url_for('table'), 'success' : True})
    else:
        print(payment.error)
        jsonify({'success' : False})

def capture_payment(contractID):
    contract = db.get_contract(contractID)

    authorization = Authorization.find(contract['authorization_id'])

    # Set capture details
    capture = authorization.capture({
        "amount": {
            "currency": "USD",
            "total": str(contract['payout'])
        },
        "payee": {
            "email_address": "sb-eyoij8038949@personal.example.com"
        },
        "is_final_capture": True
    })

    # Capture authorization
    if capture.success():
        print("Capture[%s] successfully" % (capture.id))
        return redirect(url_for('table'))
        # return jsonify({'redirect' : url_for('table'), 'success' : True})
    else:
        print(capture.error)
        return jsonify({'success' : False})