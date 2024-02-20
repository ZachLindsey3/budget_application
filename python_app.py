from flask import Flask, render_template, jsonify, request, session
from keys import clientId, secret

import request_lib as reqs

import plaid
from plaid.api import plaid_api

from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser

from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest

from plaid.model.country_code import CountryCode
from plaid.model.products import Products

import json

# Available environments are
# 'Production'
# 'Development'
# 'Sandbox'
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': clientId,
        'secret': secret,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

app = Flask(__name__)
app.secret_key = "MY_SECRET_KEY"

@app.route('/')
def index():
    plaid_client_id = clientId

    return render_template('index.html', plaid_client_id=plaid_client_id)

@app.route('/api/create_link_token', methods = ['GET'])
def link_token():
    request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(
            client_user_id='user-id-01',
            # phone_number='+1 415 5550123'
        ),
        products=[Products("auth"), Products("transactions")],
        client_name='ZSL Test Personal Finance App',
        country_codes=[CountryCode('US')],
        language='en',
    #   products=[Products('transactions')],
    #   required_if_supported_products=[Products('liabilities')],
    #   webhook='https://sample-web-hook.com',
    #   redirect_uri='https://domainname.com/oauth-page.html',
    #   account_filters=LinkTokenAccountFilters(
    #     depository=DepositoryFilter(
    #       account_subtypes=DepositoryAccountSubtypes([
    #          DepositoryAccountSubtype('checking'),
    #          DepositoryAccountSubtype('savings')
    #       ])
    #     ),
    #     credit=CreditFilter(
    #       account_subtypes=CreditAccountSubtypes([
    #          CreditAccountSubtype('credit card')
    #       ])
    #     )
    #   )
    )

    response = client.link_token_create(request)

    return(response.to_dict())

@app.route('/api/exchange_public_token', methods=['POST'])
def exchange_token():
    #TODO: Make this better maybe
    encoding = 'utf-8'
    request_body = json.loads(request.data.decode(encoding))

    exchange_request = ItemPublicTokenExchangeRequest(
        public_token = request_body['public_token']
    )
    exchange_response = client.item_public_token_exchange(exchange_request)
    
    session['access_token'] = exchange_response.to_dict()['access_token']

    return(exchange_response.to_dict())

@app.route('/api/balance_data', methods=['GET'])
def get_balance_data():
    response = reqs.get_balance_data(access_token=session["access_token"], client=client)
    return(response.to_dict())

@app.route('/api/transaction_data', methods=['GET'])
def get_transaction_data():
    response = reqs.get_transaction_data(access_token=session["access_token"], client=client)
    return(response.to_dict())

@app.route('/api/test_table', methods=['GET'])
def test_table_response():
    trans_response = reqs.get_transaction_data(access_token=session["access_token"], client=client).to_dict()
    added_list = trans_response['added']
    test_response = dict()
    result_list = []
    for transaction in added_list:
        result_list.append({"amount" : transaction["amount"], "iso_currency_code" : transaction["iso_currency_code"], "merchant_name" : transaction["merchant_name"]})

    test_response['result'] = result_list
    print(test_response)

    response = {
        "result": [
            {
            "name": "John",
            "marks": {
                "math": "78",
                "english": "90",
                "chemistry": "64",
                "physics": "89"
            }
            },
            {
            "name": "Mike",
            "marks": {
                "math": "67",
                "english": "86",
                "chemistry": "59",
                "physics": "70"
            }
            },
            {
            "name": "Julia",
            "marks": {
                "math": "82",
                "english": "75",
                "chemistry": "73",
                "physics": "84"
            }
            },
            {
            "name": "Tom",
            "marks": {
                "math": "76",
                "english": "64",
                "chemistry": "59",
                "physics": "72"
            }
            },
            {
            "name": "Barbara",
            "marks": {
                "math": "90",
                "english": "85",
                "chemistry": "88",
                "physics": "92"
            }
            }
        ]
    }
    return(test_response)


@app.route('/api/is_account_connected', methods=['GET'])
def account_connected():
    if session["access_token"]:
        return({'status' : True })
    else:
        return({'status' : False})
    
# Route for handling the login page logic
from flask import Flask, render_template, redirect, url_for, request
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('plaid_login'))
    return render_template('login.html', error=error)

@app.route('/plaid_login', methods=['GET', 'POST'])
def plaid_login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('index'))
    return render_template('plaid_login.html', error=error)

@app.route('/plaid_login/print_test', methods = ['GET'])
def print_test():
    print("test world")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)