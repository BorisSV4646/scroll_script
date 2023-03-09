from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.exceptions import TransactionNotFound
from loguru import logger
import time
from uniswap import Uniswap
import copy
import os
from dotenv import load_dotenv
from hexbytes import HexBytes

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# WATH https://habr.com/ru/post/674204/ fot web3 on python
# https://translated.turbopages.org/proxy_u/en-ru.ru.1526aeb4-63f6e7ac-aeec75a2-74722d776562/https/docs.soliditylang.org/en/develop/abi-spec.html - расшифровка
# https://github.com/h1rdr3v2/faucetbch/blob/master/main.py - скрипт на кошелек
# https://github.com/IgorGemsCodeAutomation/Arbitrum-warming_up_wallets/blob/main/main.py - проект парня из нашего чата
# https://louisabraham.github.io/articles/no-abi.html - статья как отсылать без ABi на контракт
# https://eth-converter.com/ - конвентер эфиры в гвеи и т.д.


scroll_alpha = Web3.HTTPProvider('https://alpha-rpc.scroll.io/l2')
goerly = Web3.HTTPProvider(
    'https://endpoints.omniatech.io/v1/eth/goerli/public')
count_nonce = 0


def get_wallet_edge():
    with open('wallets/wallet_edge.txt', 'r') as file:
        _main_wallet = [row.strip() for row in file]
        return _main_wallet


def check_balance(_main_wallet, network):
    web3 = Web3(network)
    return (web3.fromWei(web3.eth.get_balance(_main_wallet), 'ether'))


def create_transaction(chainId, account_from, value, data, contract, network):
    global count_nonce
    web3 = Web3(network)
    while count_nonce == web3.eth.getTransactionCount(account_from):
        time.sleep(5)
    dict_transaction = {
        'chainId': chainId,
        'from': account_from,
        'to': contract,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.getTransactionCount(account_from),
        'value': int(Web3.toWei(value, 'ether')),
        'data': data,
        'gas': 2_000_000 * 2,
    }
    count_nonce = dict_transaction['nonce']
    return dict_transaction


def sign_transaction(dict_transaction, network):
    web3 = Web3(network)
    signed_txn = web3.eth.account.sign_transaction(
        dict_transaction, os.environ.get('private_key_main'))  # тут надо будет ввести перемнную для закрытого ключа
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    while True:
        try:
            txn = web3.eth.get_transaction_receipt(txn_hash.hex())
            if txn['status'] == 1:
                logger.success(
                    f"Wallet {dict_transaction['to']} succes recieve {dict_transaction['value']} ETH - {txn_hash.hex()}")
            else:
                logger.error(f"{txn_hash.hex()} not send")
            break
        except TransactionNotFound:
            pass


def send_txn():
    wallets = get_wallet_edge()
    for i in range(len(wallets)):
        network = goerly
        account_from = os.environ.get('main_account')
        chainId = 5
        value = 0.01
        data = ""
        if (check_balance(wallets[i], network) >= 0.04):
            logger.info(f"{wallets[i]} have more than 0.04 eth")
            continue
        else:
            contract = wallets[i]
            sign_transaction(create_transaction(
                chainId, account_from, value, data, contract, network), network)

# *Сделать цикл для разных кошелей. Разобраться как брат только мультипликатор функции
# *и подставлять к нему закодированные данные


# def depositETH():
#     contract = "0xe5E30E7c24e4dFcb281A682562E53154C15D3332"
#     amount = 10000040
#     gas = 2_000_000
#     dict_transaction = {
#         'chainId': 5,
#         'from': account_from,
#         'to': contract,
#         'gasPrice': web3.eth.gas_price,
#         'nonce': web3.eth.getTransactionCount(account_from),
#         'value': int(Web3.toWei(amount, 'gwei')),
#         'data': "0x9f8420b3000000000000000000000000000000000000000000000000002386f26fc100000000000000000000000000000000000000000000000000000000000000009c40",
#         'gas': gas,
#     }
#     signed_txn = web3.eth.account.sign_transaction(
#         dict_transaction, private_key)
#     txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
#     logger.success(txn_hash.hex())


# смотреть: https://uniswap-python.com/getting-started.html
# https://stackoverflow.com/questions/64526925/how-to-swap-tokens-on-uniswap-using-web3-js
# https://www.youtube.com/watch?v=oYMCQg4Oqlc
def wrapETH():
    web3 = Web3(scroll_alpha)
    logger.info(f"Is connected to SCroll Alpha: {web3.isConnected()}")
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    # uniswap = Uniswap(address=account_from, private_key=private_key,
    #                   version=version, provider="https://alpha-rpc.scroll.io/l2")
    # eth = "0x0000000000000000000000000000000000000000"
    # usdc = "0xA0D71B9877f44C744546D649147E3F1e70a93760"
    # print(uniswap.get_eth_balance())
    # print(uniswap.get_token(eth))
    # uniswap.make_trade(eth, usdc, 4627292594762859)

    contract = "0x5300000000000000000000000000000000000004"
    amount = 10000000
    gas = 2_000_000
    dict_transaction = {
        'chainId': 534353,
        'from': account_from,
        'to': contract,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.getTransactionCount(account_from),
        'value': int(Web3.toWei(amount, 'gwei')),
        'data': "0xd0e30db0",
        'gas': gas * 2,
    }
    signed_txn = web3.eth.account.sign_transaction(
        dict_transaction, private_key)
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    logger.success(txn_hash.hex())


def unwrapETH():
    web3 = Web3(scroll_alpha)
    logger.info(f"Is connected to SCroll Alpha: {web3.isConnected()}")
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    contract = "0x5300000000000000000000000000000000000004"
    amount = 0
    gas = 2_000_000
    dict_transaction = {
        'chainId': 534353,
        'from': account_from,
        'to': contract,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.getTransactionCount(account_from),
        'value': int(Web3.toWei(amount, 'gwei')),
        'data': "0x2e1a7d4d000000000000000000000000000000000000000000000000002386f26fc10000",
        'gas': gas * 2,
    }
    signed_txn = web3.eth.account.sign_transaction(
        dict_transaction, private_key)
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    logger.success(txn_hash.hex())

# !Проблема с nonce - не дает сделать больше одной транзакции, так как нонс затревает
# !Проблема с Юнисвапом, надо понять как подставлять значения свои, так как цены меняются постоянно


def swapUSDC():
    web3 = Web3(scroll_alpha)
    logger.info(f"Is connected to SCroll Alpha: {web3.isConnected()}")
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    # version = 3
    # uniswap = Uniswap(address=account_from, private_key=private_key,
    #                   version=version, provider="https://alpha-rpc.scroll.io/l2")
    # eth = "0x0000000000000000000000000000000000000000"
    # usdc = "0xA0D71B9877f44C744546D649147E3F1e70a93760"
    # print(uniswap.get_eth_balance())
    # print(uniswap.get_token(eth))
    # uniswap.make_trade(eth, usdc, 4627292594762859)

    contract = "0x111690A4468ba9b57d08280b2166AFf2bAC65248"
    amount = 0.01
    gas = 2_000_000
    dict_transaction = {
        'chainId': 534353,
        'from': account_from,
        'to': contract,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.getTransactionCount(account_from),
        'value': int(Web3.toWei(amount, 'ether')),
        'data': "0x5ae401dc000000000000000000000000000000000000000000000000000000006401629600000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000e404e45aaf0000000000000000000000005300000000000000000000000000000000000004000000000000000000000000a0d71b9877f44c744546d649147e3f1e70a937600000000000000000000000000000000000000000000000000000000000000bb80000000000000000000000007a8463b955c403ebd4611b18743a40aeba0d7d4f000000000000000000000000000000000000000000000000002386f26fc10000000000000000000000000000000000000000000000000042b212447e0082c970000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        'gas': gas * 2,
    }
    signed_txn = web3.eth.account.sign_transaction(
        dict_transaction, private_key)
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    logger.success(txn_hash.hex())

    contract = "0xA0D71B9877f44C744546D649147E3F1e70a93760"
    amount = 0
    gas = 2_000_000
    dict_transaction = {
        'chainId': 534353,
        'from': account_from,
        'to': contract,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.getTransactionCount(account_from),
        'value': int(Web3.toWei(amount, 'ether')),
        'data': "0x095ea7b3000000000000000000000000111690a4468ba9b57d08280b2166aff2bac65248ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        'gas': gas * 2,
    }
    signed_txn = web3.eth.account.sign_transaction(
        dict_transaction, private_key)
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    logger.success(txn_hash.hex())

    contract = "0x111690A4468ba9b57d08280b2166AFf2bAC65248"
    amount = 0
    gas = 2_000_000
    dict_transaction = {
        'chainId': 534353,
        'from': account_from,
        'to': contract,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.getTransactionCount(account_from),
        'value': int(Web3.toWei(amount, 'ether')),
        'data': "0x5ae401dc0000000000000000000000000000000000000000000000000000000064016524000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000000e404e45aaf000000000000000000000000a0d71b9877f44c744546d649147e3f1e70a9376000000000000000000000000053000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000bb8000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000003635c9adc5dea00000000000000000000000000000000000000000000000000000001ca1046f3f2c4a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004449404b7c000000000000000000000000000000000000000000000000001ca1046f3f2c4a0000000000000000000000007a8463b955c403ebd4611b18743a40aeba0d7d4f00000000000000000000000000000000000000000000000000000000",
        'gas': gas * 2,
    }
    signed_txn = web3.eth.account.sign_transaction(
        dict_transaction, private_key)
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    logger.success(txn_hash.hex())

# TODO:Протестировать код с разделением транзы на две функции


def create_pool():
    web3 = Web3(scroll_alpha)
    logger.info(f"Is connected to SCroll Alpha: {web3.isConnected()}")
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    value = 0
    data = "1111111111"
    contract = "sassss"
    sign_transaction(create_transaction(value, data, contract))


send_txn()
# depositETH()
# wrapETH()
# unwrapETH()
# create_pool()

# if __name__ == '__main__':
#     pass
