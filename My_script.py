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
import pandas as pd
import ContractFunction
from web3.contract import Contract
from web3.types import ABI
import requests

""" 
    2. Упаковать нормально код и улучшить логгирование, как в скрипте со смарт контрактом
    3. Сделать свапалку на юнисвап
 """

logger.add(
    "log/runScript.log",
    format="{time} | {level} | {message}",
    level="DEBUG",
)

wallet_key = pd.read_excel(
    './wallets/wallets.xlsx', sheet_name='wallet', header=None)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# WATH https://habr.com/ru/post/674204/ fot web3 on python
# https://translated.turbopages.org/proxy_u/en-ru.ru.1526aeb4-63f6e7ac-aeec75a2-74722d776562/https/docs.soliditylang.org/en/develop/abi-spec.html - расшифровка
# https://github.com/h1rdr3v2/faucetbch/blob/master/main.py - скрипт на кошелек
# https://github.com/IgorGemsCodeAutomation/Arbitrum-warming_up_wallets/blob/main/main.py - проект парня из нашего чата
# https://louisabraham.github.io/articles/no-abi.html - статья как отсылать без ABi на контракт
# https://eth-converter.com/ - конвентер эфиры в гвеи и т.д.

# ? компиляция контракта прямо web3 https://web3py.readthedocs.io/en/stable/web3.contract.html
# ! упаковать все красиво, как у https://github.com/SomeWeb3/arbitrum_contract_deployer/tree/main/app


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
        'gas': 2_000_000,
    }
    count_nonce = dict_transaction['nonce']
    return dict_transaction


def createTransactionWithoutGasPrice(chainId, account_from, value, data, contract, network, gasPrice):
    global count_nonce
    web3 = Web3(network)
    while count_nonce == web3.eth.getTransactionCount(account_from):
        time.sleep(5)
    dict_transaction = {
        'chainId': chainId,
        'from': account_from,
        'to': contract,
        'gasPrice': gasPrice,
        'nonce': web3.eth.getTransactionCount(account_from),
        'value': int(Web3.toWei(value, 'ether')),
        'data': data,
        'gas': 2_000_000 * 2,
    }
    count_nonce = dict_transaction['nonce']
    return dict_transaction


def createCallContract(chainId, account_from, value, network):
    global count_nonce
    web3 = Web3(network)
    # while count_nonce == web3.eth.getTransactionCount(account_from):
    #     time.sleep(5)
    dict_transaction = {
        'chainId': chainId,
        'from': account_from,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.getTransactionCount(account_from),
        'value': int(Web3.toWei(value, 'ether')),
        'gas': 2_000_000 * 2,
    }
    count_nonce = dict_transaction['nonce']
    return dict_transaction


def sign_transaction(dict_transaction, network, private_key):
    web3 = Web3(network)
    if network == scroll_alpha:
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    signed_txn = web3.eth.account.sign_transaction(
        dict_transaction, private_key)
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    with open(f'./hashWallets/{dict_transaction["from"]}.txt', 'w') as f:
        f.write(str(txn_hash.hex()))
    while True:
        try:
            txn = web3.eth.get_transaction_receipt(txn_hash.hex())
            if txn['status'] == 1:
                logger.success(
                    f"Transaction {dict_transaction['from']} to {dict_transaction['to']} send - {txn_hash.hex()}")
            else:
                logger.error(
                    f"Transaction {dict_transaction['from']} to {dict_transaction['to']} not send - {txn_hash.hex()}")
            break
        except TransactionNotFound:
            pass


def createHEX(value):
    valueWei = int(Web3.toWei(value, 'ether'))
    amount = valueWei
    hex = Web3.toHex(amount)
    line = hex[2:]
    newline = line.rstrip('0')
    if (len(newline) < 60):
        c = "0"
        n = 60 - len(newline)
        new_str = c * n
        value = new_str + newline
    return value


def send_txn():
    wallets = get_wallet_edge()
    for i in range(len(wallets)):
        network = goerly
        account_from = os.environ.get('main_account')
        chainId = 5
        value = 0.15
        data = ""
        if (check_balance(wallet_key.at[i, 0], network) >= 0.15):
            logger.info(
                f"{wallet_key.at[i, 0]} have more than 0.15 eth")
            continue
        else:
            contract = wallet_key.at[i, 0]
            private_key = os.environ.get('private_key_main')
            sign_transaction(create_transaction(
                chainId, account_from, value, data, contract, network), network, private_key)

# ?как пеервести hex в число: x = int("16345785d8a0000", 16)


def depositETH():
    wallets = get_wallet_edge()
    for i in range(len(wallets)):
        network = goerly
        web3 = Web3(network)
        account_from = wallet_key.at[i, 0]
        chainId = 5
        gasPrice = web3.eth.gas_price
        value = 0.100003
        data = f"0x9f8420b3{createHEX(0.1)}00000000000000000000000000000000000000000000000000000000000000009c40"
        contract = "0xe5E30E7c24e4dFcb281A682562E53154C15D3332"
        private_key = wallet_key.at[i, 1]
        sign_transaction(createTransactionWithoutGasPrice(
            chainId, account_from, value, data, contract, network, gasPrice), network, private_key)


def wrapETH():
    wallets = get_wallet_edge()
    contract = "0xa1EA0B2354F5A344110af2b6AD68e75545009a03"
    ContractFunction.gethaches(contract)
    newcontract = ContractFunction.getContract()
    for i in range(len(wallets)):
        network = scroll_alpha
        account_from = wallet_key.at[i, 0]
        chainId = 534353
        value = 0.01
        private_key = wallet_key.at[i, 1]
        while (check_balance(wallet_key.at[i, 0], network) < 0.01):
            time.sleep(3)
        transaction = newcontract.functions.deposit().buildTransaction(createCallContract(
            chainId, account_from, value, network))
        sign_transaction(transaction, network, private_key)


def unwrapETH():
    wallets = get_wallet_edge()
    contract = "0xa1EA0B2354F5A344110af2b6AD68e75545009a03"
    ContractFunction.gethaches(contract)
    newcontract = ContractFunction.getContract()
    for i in range(len(wallets)):
        network = scroll_alpha
        account_from = wallet_key.at[i, 0]
        chainId = 534353
        value = 0
        private_key = wallet_key.at[i, 1]
        while (check_balance(wallet_key.at[i, 0], network) < 0.01):
            time.sleep(3)
        transaction = newcontract.functions.withdraw(10000000000000000).buildTransaction(createCallContract(
            chainId, account_from, value, network))
        sign_transaction(transaction, network, private_key)


# def swapUni():
#     version = 3
#     uniswap = Uniswap(address=os.environ.get('main_account'), private_key=os.environ.get('private_key_main'),
#                       version=version, provider="https://alpha-rpc.scroll.io/l2", factory_contract_addr="0x29f8ecF9d27551905116F35B1bF38C1B3B211729", router_contract_addr="0xD9880690bd717189cC3Fbe7B9020F27fae7Ac76F")
#     eth = "0x0000000000000000000000000000000000000000"
#     usdc = "0xA0D71B9877f44C744546D649147E3F1e70a93760"
#     print(uniswap.get_eth_balance())
#     print(uniswap.get_token(eth))
#     print(uniswap.get_token('0xA0D71B9877f44C744546D649147E3F1e70a93760'))
#     uniswap.get_price_input(eth, usdc, 1*10**16)
    # uniswap.make_trade(eth, usdc, 1*10**16, fee=500)


# ! прочитать https://owodunni.medium.com/uniswapv2-routing-5d56aec96ac3 и про маршрутизатор юнисвап
def swapUSDC():
    wallets = get_wallet_edge()
    contract = "0x111690A4468ba9b57d08280b2166AFf2bAC65248"
    ContractFunction.gethaches(contract)
    newcontract = ContractFunction.getContract()
    for i in range(len(wallets)):
        network = scroll_alpha
        account_from = wallet_key.at[i, 0]
        chainId = 534353
        value = 0.01
        private_key = wallet_key.at[i, 1]
        while (check_balance(wallet_key.at[i, 0], network) < 0.01):
            time.sleep(3)
        # transaction = newcontract.functions.sweepToken("0x0000000000000000000000000000000000000000", 50000000000000000, "0xA0D71B9877f44C744546D649147E3F1e70a93760").buildTransaction(createCallContract(
        #     chainId, account_from, value, network))
        transaction = newcontract.functions.swapExactTokensForTokens(0, 0, ["0x0000000000000000000000000000000000000000", "0xA0D71B9877f44C744546D649147E3F1e70a93760"], "0x04Ee5860e4fce5560865197BCfb83b9192ce4dbD").buildTransaction(createCallContract(
            chainId, account_from, value, network))
        sign_transaction(transaction, network, private_key)

    # contract = "0xA0D71B9877f44C744546D649147E3F1e70a93760"
    # amount = 0
    # gas = 2_000_000
    # dict_transaction = {
    #     'chainId': 534353,
    #     'from': account_from,
    #     'to': contract,
    #     'gasPrice': web3.eth.gas_price,
    #     'nonce': web3.eth.getTransactionCount(account_from),
    #     'value': int(Web3.toWei(amount, 'ether')),
    #     'data': "0x095ea7b3000000000000000000000000111690a4468ba9b57d08280b2166aff2bac65248ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    #     'gas': gas * 2,
    # }
    # signed_txn = web3.eth.account.sign_transaction(
    #     dict_transaction, private_key)
    # txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    # logger.success(txn_hash.hex())

    # contract = "0x111690A4468ba9b57d08280b2166AFf2bAC65248"
    # amount = 0
    # gas = 2_000_000
    # dict_transaction = {
    #     'chainId': 534353,
    #     'from': account_from,
    #     'to': contract,
    #     'gasPrice': web3.eth.gas_price,
    #     'nonce': web3.eth.getTransactionCount(account_from),
    #     'value': int(Web3.toWei(amount, 'ether')),
    #     'data': "0x5ae401dc0000000000000000000000000000000000000000000000000000000064016524000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000000e404e45aaf000000000000000000000000a0d71b9877f44c744546d649147e3f1e70a9376000000000000000000000000053000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000bb8000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000003635c9adc5dea00000000000000000000000000000000000000000000000000000001ca1046f3f2c4a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004449404b7c000000000000000000000000000000000000000000000000001ca1046f3f2c4a0000000000000000000000007a8463b955c403ebd4611b18743a40aeba0d7d4f00000000000000000000000000000000000000000000000000000000",
    #     'gas': gas * 2,
    # }
    # signed_txn = web3.eth.account.sign_transaction(
    #     dict_transaction, private_key)
    # txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    # logger.success(txn_hash.hex())


def BufficornBatle():
    wallets = get_wallet_edge()
    contract = "0x59Ef5D23edea409FbD03761A57D7078e475f8419"
    ContractFunction.gethaches(contract)
    newcontract = ContractFunction.getContract()
    for i in range(len(wallets)):
        network = scroll_alpha
        account_from = wallet_key.at[i, 0]
        chainId = 534353
        value = 0
        private_key = wallet_key.at[i, 1]
        while (check_balance(wallet_key.at[i, 0], network) < 0.01):
            time.sleep(3)
        transaction = newcontract.functions.mintCharacterNFT(0).buildTransaction(createCallContract(
            chainId, account_from, value, network))
        sign_transaction(transaction, network, private_key)

    # TODO:вместо обращения к контракту отправит просто HTTP запрос к кнопке и подписать кошельком
    # TODO:понять только должен ли быть подключен уже метамаск
    # https://onchain-tictactoe.vercel.app/


def newGame():
    pass


# def create_pool():
#     web3 = Web3(scroll_alpha)
#     logger.info(f"Is connected to SCroll Alpha: {web3.isConnected()}")
#     web3.middleware_onion.inject(geth_poa_middleware, layer=0)
#     value = 0
#     data = "1111111111"
#     contract = "sassss"
#     sign_transaction(create_transaction(value, data, contract))


# def main():
#     send_txn()
#     depositETH()
#     wrapETH()
#     unwrapETH()

swapUSDC()
