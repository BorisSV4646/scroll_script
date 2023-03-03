from web3 import Web3
from web3.middleware import geth_poa_middleware
from loguru import logger
import time
from uniswap import Uniswap
import copy

# WATH https://habr.com/ru/post/674204/ fot web3 on python
# https://translated.turbopages.org/proxy_u/en-ru.ru.1526aeb4-63f6e7ac-aeec75a2-74722d776562/https/docs.soliditylang.org/en/develop/abi-spec.html - расшифровка
# https://github.com/h1rdr3v2/faucetbch/blob/master/main.py - скрипт на кошелек
# https://github.com/IgorGemsCodeAutomation/Arbitrum-warming_up_wallets/blob/main/main.py - проект парня из нашего чата
# https://louisabraham.github.io/articles/no-abi.html - статья как отсылать без ABi на контракт
# https://eth-converter.com/ - конвентер эфиры в гвеи и т.д.

private_key = "3b58db09af4c2d51507cbb11cf902f50ae2902b9447478fdaff9226f1a646d5f"
account_from = "0x7A8463B955c403ebd4611b18743a40aeBa0d7d4F"
version = 3

scroll_alpha = Web3.HTTPProvider('https://alpha-rpc.scroll.io/l2')
goerly = Web3.HTTPProvider(
    'https://endpoints.omniatech.io/v1/eth/goerli/public')


web3 = Web3(goerly)
if web3.isConnected() != True:
    logger.error(f"Is connected: {web3.isConnected()}")
# web3.middleware_onion.inject(geth_poa_middleware, layer=0)


# TODO: сделать нормальный словарь на все случаи транз
transaction_main = {
    'chainId': 534353,
    'from': account_from,
    'to': "",
    'gasPrice': web3.eth.gas_price,
    'nonce': web3.eth.getTransactionCount(account_from),
    'value': int(Web3.toWei(0, 'ether')),
    'data': "0x5ae401dc0000000000000000000000000000000000000000000000000000000064016524000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000000e404e45aaf000000000000000000000000a0d71b9877f44c744546d649147e3f1e70a9376000000000000000000000000053000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000bb8000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000003635c9adc5dea00000000000000000000000000000000000000000000000000000001ca1046f3f2c4a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004449404b7c000000000000000000000000000000000000000000000000001ca1046f3f2c4a0000000000000000000000007a8463b955c403ebd4611b18743a40aeba0d7d4f00000000000000000000000000000000000000000000000000000000",
    'gas': 2_000_000 * 2,
}


def get_wallet_edge():
    with open('wallets/wallet_edge.txt', 'r') as file:
        _main_wallet = [row.strip() for row in file]
        return _main_wallet


def check_balance(_main_wallet):
    return (web3.fromWei(web3.eth.get_balance(_main_wallet), 'ether'))

# *Разобраться с nonce - как его увеличить на 1 без while


def send_txn(account_from):
    wallets = get_wallet_edge()
    for i in range(len(wallets)):
        if (check_balance(wallets[i]) >= 0.02):
            logger.info(f"{wallets[i]} have more than 0.02 eth")
            continue
        else:
            amount = 0.01
            gas = 2_000_000
            nonce = web3.eth.getTransactionCount(account_from)
            print(nonce)
            txn = {
                'chainId': 5,
                'from': account_from,
                'to': wallets[i],
                'value': int(Web3.toWei(amount, 'ether')),
                'nonce': nonce,
                'gasPrice': web3.eth.gas_price,
                'gas': gas,
            }
            signed_txn = web3.eth.account.sign_transaction(
                txn, private_key)
            txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
            hash = txn_hash.hex()
            logger.success(
                f"{wallets[i]} succes recieve {amount} ETH - {hash}")
            while (nonce == (web3.eth.getTransactionCount(account_from))):
                time.sleep(3)
            # txn = web3.eth.get_transaction_receipt(hash)
            # logger.info(txn[0]['status'])

# *Сделать цикл для разных кошелей. Разобраться как брат только мультипликатор функции
# *и подставлять к нему закодированные данные


def depositETH():
    contract = "0xe5E30E7c24e4dFcb281A682562E53154C15D3332"
    amount = 10000040
    gas = 2_000_000
    dict_transaction = {
        'chainId': 5,
        'from': account_from,
        'to': contract,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.getTransactionCount(account_from),
        'value': int(Web3.toWei(amount, 'gwei')),
        'data': "0x9f8420b3000000000000000000000000000000000000000000000000002386f26fc100000000000000000000000000000000000000000000000000000000000000009c40",
        'gas': gas,
    }
    signed_txn = web3.eth.account.sign_transaction(
        dict_transaction, private_key)
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    logger.success(txn_hash.hex())


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


def create_transaction(value, data, contract):
    dict_transaction = copy.deepcopy(transaction_main)
    dict_transaction["value"] = value
    dict_transaction["data"] = data
    dict_transaction["to"] = contract
    return dict_transaction


def sign_transaction(dict_transaction):
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


    # send_txn(account_from)
    # depositETH()
    # wrapETH()
    # unwrapETH()
create_pool()
