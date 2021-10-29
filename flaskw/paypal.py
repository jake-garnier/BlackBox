"""
File Name: paypal.py
Description: Contains functions which manage the various paypal functions which receive and disburse payments 
and manage balances.
"""

from paypalrestsdk import Payment
from paypalrestsdk import Authorization
from flask import redirect, flash, jsonify, url_for
import paypalrestsdk
from flaskw import sql as sql
from paypalpayoutssdk.core import PayPalHttpClient, SandboxEnvironment
from paypalpayoutssdk.payouts import PayoutsPostRequest
from paypalhttp import HttpError
from flaskw import constants

"""
Description: Configures the paypal environment, initializing the sandbox environment and the payouts client.
@return (paypalrestsdk.PayoutsClient) The client used to send paypal payouts.
"""
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

"""
Description: Function for handling the creating of a paypal payment from the user to the application's merchant account.
@arg: request (POST request): The request containing the information about the submission.
"""
def create_payment(request, db):

    contract = sql.get_contract(request.form['contractID'], db)

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


"""
Description: Function for handling the execution of a paypal payment from the user to the application's 
merchant account.
@arg: request (POST request): The request containing the information about the submission.
"""
def execute_payment(request):

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id' : request.form['payerID']}):
        print('Execute success!')
        return jsonify({'redirect' : url_for('table'), 'success' : True})
    else:
        print(payment.error)
        jsonify({'success' : False})


"""
Description: Function for handling the sending of a paypal payment from the application"s merchant account to a user.
@arg payouts_client (paypalrestsdk.PayoutsClient): The client used to send the paypal payout.
@arg attempt_id (int): The id of the attempt that was successful.
@return (str): Message of success or failure.
"""
def make_payout(payouts_client, attempt_id, db):

    attempt = sql.get_attempt(attempt_id, db)
    contract = sql.get_contract(attempt['contract_id'], db)

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