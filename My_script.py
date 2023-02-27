from web3 import Web3
from web3.middleware import geth_poa_middleware
from loguru import logger

# logger.add("log/file_{time}.log",
#            format="{time} {level} {message}", level="DEBUG")

private_key = "3b58db09af4c2d51507cbb11cf902f50ae2902b9447478fdaff9226f1a646d5f"
account_from = "0x7A8463B955c403ebd4611b18743a40aeBa0d7d4F"
account_to = "0x2e2C1C959E6Ff27DbA3b7901ef86bFEA0174F0C1"
# *WATH https://habr.com/ru/post/674204/ fot web3 on python
# *https://l1scan.scroll.io/tx/0xdaf9e1855af2132eb1defbe766ab9eb855abd79f21817baa6a404017c0d267c0 - explorer
# *https://translated.turbopages.org/proxy_u/en-ru.ru.1526aeb4-63f6e7ac-aeec75a2-74722d776562/https/docs.soliditylang.org/en/develop/abi-spec.html - расшифровка
# *https://github.com/h1rdr3v2/faucetbch/blob/master/main.py - скрипт на кошелек


def get_wallet():
    with open('wallets/wallet.txt', 'r') as file:
        _main_wallet = [row.strip() for row in file]
    return _main_wallet


scroll_l1 = Web3.HTTPProvider('https://prealpha-rpc.scroll.io/l1')
scroll_l2 = Web3.HTTPProvider('https://prealpha-rpc.scroll.io/l2')


# web3 = Web3(scroll_l2)
# logger.info(f"Is connected: {web3.isConnected()}")
# web3.middleware_onion.inject(geth_poa_middleware, layer=0)

web3 = Web3(scroll_l1)
logger.info(f"Is connected: {web3.isConnected()}")
web3.middleware_onion.inject(geth_poa_middleware, layer=0)


def check_balance(_main_wallet):
    for wallets in _main_wallet:
        if ((web3.fromWei(web3.eth.get_balance(wallets), 'ether')) == 0):
            logger.error(f'Balance {wallets} 0 ')


def send_txn(account_from, account_to):
    amount = 0.01
    gas = 2_000_000
    nonce = web3.eth.getTransactionCount(account_from)
    txn = {
        'chainId': 534351,
        'from': account_from,
        'to': account_to,
        'value': int(Web3.toWei(amount, 'ether')),
        'nonce': nonce,
        'gasPrice': web3.eth.gas_price,
        'gas': gas,
    }

    return txn


transaction = send_txn(account_from, account_to)


# 2. Подписываем транзакцию с приватным ключом
signed_txn = web3.eth.account.sign_transaction(transaction, private_key)


# 3. Отправка транзакции
txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

# Получаем хэш транзакции
# Можно посмотреть статус тут https://testnet.bscscan.com/
hash = txn_hash.hex()
txn = web3.eth.get_transaction_receipt(hash)
logger.info(txn)


# check_balance(get_wallet())
