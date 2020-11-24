import subprocess
import json
import os
from constants import *
from dotenv import load_dotenv
load_dotenv()
from bit import wif_to_key
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3 import Web3 
from web3.auto.gethdev import w3
from web3.middleware import geth_poa_middleware
from eth_account import Account

mnemonic = os.getenv('MNEMONIC')

def derive_wallets(coins):
    command = f'php ./hd-wallet-derive/hd-wallet-derive.php -g --mnemonic="{mnemonic}" --coin="{coins}" --numderive=3 --cols=path,address,privkey,pubkey --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return keys

coins = { ETH: derive_wallets(ETH), BTCTEST: derive_wallets(BTCTEST) }

##print(coins)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin== BTCTEST:
        return PrivateKeyTestnet(priv_key)

def create_tx(coin, account, to, amount):
    if coin == ETH:
        value = w3.toWei(amount, "ether")
        gasEstimate = w3.eth.estimateGas(
        {"from" : account.address, "to" : to, "amount" : amount}
        )
        return {
            "from" : account.address,
            "to" : to,
            "value" : value,
            "gasPrice" : w3.eth.gasPrice,
            "gas" : gasEstimate,
            "nonce" : w3.eth.getTransactionCount(account.address),
            }
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

def send_tx(coin, account, to, amount):
    tx = create_tx(coin, account, to, amount)
    signed_tx = account.sign_transaction(tx)
    if coin == ETH:
        return w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    elif coin == BTCTEST:
        return  NetworkAPI.broadcast_tx_testnet(signed_tx)

# Define accounts

account_one= priv_key_to_account(BTCTEST,coins[BTCTEST][0]['privkey'])
account_one_eth= priv_key_to_account(ETH,coins[ETH][0]['privkey'])

##print(coins[ETH][0]['privkey'])
##print(f"BTCTEST:{coins[BTCTEST][0]['address']}")

account_two= coins[BTCTEST][1]['address']
account_two_eth= coins[ETH][1]['address']
print(account_two_eth)
# Define messages
from bit import wif_to_key
key1 = wif_to_key(coins[BTCTEST][0]['privkey'])
key2 = wif_to_key(coins[BTCTEST][1]['privkey'])
##print(key1.get_balance("btc"))
send_tx(ETH, account_one_eth,account_two_eth, 0.01)
##send_tx(BTCTEST,account_one,account_two, 0.000001)

##print(key1.get_balance("btc"))
##print(key2.get_balance("btc"))