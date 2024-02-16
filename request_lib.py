from plaid.model.transactions_sync_request import TransactionsSyncRequest
def get_transaction_data(access_token, client):
    transaction_request = TransactionsSyncRequest(
        access_token = access_token
    )
    response = client.transactions_sync(transaction_request)

    print("transaction_requested")
    return(response)

from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
def get_balance_data(access_token, client):
    balance_request = AccountsBalanceGetRequest(
        access_token = access_token
    )
    balance_response = client.accounts_balance_get(balance_request)

    print("balance_requested")
    return(balance_response)