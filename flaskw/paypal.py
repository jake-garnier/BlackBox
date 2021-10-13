from paypalrestsdk import Payment
from paypalrestsdk import Authorization
from flask import redirect, flash, jsonify, url_for
import paypalrestsdk
from flaskw import db
from paypalpayoutssdk.core import PayPalHttpClient, SandboxEnvironment
from paypalpayoutssdk.payouts import PayoutsPostRequest
from paypalhttp import HttpError
from flaskw import constants

def configure():
    # Creating an environment
    environment = SandboxEnvironment(client_id=constants.paypal_client_id, client_secret=constants.paypal_client_secret)
    payouts_client = PayPalHttpClient(environment)

    paypalrestsdk.configure({
        'mode': 'sandbox', #sandbox or live
        'client_id': constants.paypal_client_id,
        'client_secret': constants.paypal_client_secret }
    )

    return payouts_client

def create_payment(request):

    contract = db.get_contract(request.form['contractID'])

    payment = paypalrestsdk.Payment({
        "intent": "sale",

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
            "description": "This is the payment transaction description.",
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
        return jsonify({'redirect' : url_for('table'), 'success' : True})
    else:
        print(payment.error)
        jsonify({'success' : False})

def make_payout(payouts_client, attempt_id):

    attempt = db.get_attempt(attempt_id)
    contract = db.get_contract(attempt['contract_id'])

    body = {
        "sender_batch_header": {
            "recipient_type": "EMAIL",
            "email_message": "SDK payouts test txn",
            "note": "Enjoy your Payout!!",
            "sender_batch_id": attempt['id'],
            "email_subject": "This is a test transaction from SDK"
        },
        "items": [{
            "note": "Your 1$ Payout!",
            "amount": {
                "currency": "USD",
                "value": (contract['payout']-.05)
            },
            "receiver": attempt['payment_email']
        }]
    }

    request = PayoutsPostRequest()
    request.request_body(body)

    try:
        # Call API with your client and get a response for your call
        response = payouts_client.execute(request)
        # If call returns body in response, you can get the deserialized version from the result attribute of the response
        batch_id = response.result.batch_header.payout_batch_id
        print(batch_id)
        return 'Success!'
    except IOError as ioe:
        print(ioe)
        if isinstance(ioe, HttpError):
            # Something went wrong server-side
            print(ioe.status_code)
        return 'Failure you loser!'