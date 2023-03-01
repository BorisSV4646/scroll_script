from web3 import Web3
from web3.middleware import geth_poa_middleware
from loguru import logger
import time

# WATH https://habr.com/ru/post/674204/ fot web3 on python
# https://translated.turbopages.org/proxy_u/en-ru.ru.1526aeb4-63f6e7ac-aeec75a2-74722d776562/https/docs.soliditylang.org/en/develop/abi-spec.html - расшифровка
# https://github.com/h1rdr3v2/faucetbch/blob/master/main.py - скрипт на кошелек
# https://github.com/IgorGemsCodeAutomation/Arbitrum-warming_up_wallets/blob/main/main.py - проект парня из нашего чата
# https://louisabraham.github.io/articles/no-abi.html - статья как отсылать без ABi на контракт
# https://eth-converter.com/ - конвентер эфиры в гвеи и т.д.

private_key = "3b58db09af4c2d51507cbb11cf902f50ae2902b9447478fdaff9226f1a646d5f"
account_from = "0x7A8463B955c403ebd4611b18743a40aeBa0d7d4F"

scroll_alpha = Web3.HTTPProvider('https://alpha-rpc.scroll.io/l2')
goerly = Web3.HTTPProvider(
    'https://endpoints.omniatech.io/v1/eth/goerli/public')


web3 = Web3(goerly)
logger.info(f"Is connected: {web3.isConnected()}")
# web3.middleware_onion.inject(geth_poa_middleware, layer=0)


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
        if (check_balance(wallets[i]) >= 0.03):
            logger.info(f"{wallets[i]} have more than 0.01 eth")
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
            logger.info(hash)
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
        'gas': gas * 2,
    }
    signed_txn = web3.eth.account.sign_transaction(
        dict_transaction, private_key)
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(txn_hash.hex())


# send_txn(account_from)
depositETH()
