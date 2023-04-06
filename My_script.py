from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.exceptions import TransactionNotFound
from loguru import logger
import time
import os
from dotenv import load_dotenv
import pandas as pd
import ContractFunction


""" ! анврапнуть эфир обратно, вывести в гоэрли, запустить по новой 
    ! понять в чем рпоблема с газом? Что такое газ и какую сумму надо туда указывать? Посмотреть примеры как это делают ребята
    2. Упаковать нормально код и улучшить логгирование, как в скрипте со смарт контрактом
    3. Сделать свапалку на юнисвап - смотреть про мультикалл
        https://www.npmjs.com/package/ethereum-multicall
        https://www.solveforum.com/forums/threads/solved-uniswap-v3-multicall-to-swap-tokens-error.1060683/
        https://www.youtube.com/watch?v=vXu5GeLP6A8
        https://www.youtube.com/watch?v=Ve8Kp7hFES8
    
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


# def create_transaction(chainId, account_from, value, data, contract, network):
#     global count_nonce
#     web3 = Web3(network)
#     while count_nonce == web3.eth.getTransactionCount(account_from):
#         time.sleep(5)
#     dict_transaction = {
#         'chainId': chainId,
#         'from': account_from,
#         'to': contract,
#         'gasPrice': web3.eth.gas_price,
#         'nonce': web3.eth.getTransactionCount(account_from),
#         'value': int(Web3.toWei(value, 'ether')),
#         'data': data,
#         'gas': 2_000_000,
#     }
#     count_nonce = dict_transaction['nonce']
#     return dict_transaction


def create_transaction(chainId, account_from, value, data, contract, network):
    global count_nonce
    web3 = Web3(network)
    dict_transaction = {
        'chainId': chainId,
        'from': account_from,
        'to': contract,
        'gasPrice': web3.eth.gas_price,
        'value': int(Web3.toWei(value, 'ether')),
        'data': data,
        'gas': 2_000_000,
    }
    if count_nonce == web3.eth.getTransactionCount(account_from):
        newNonce = web3.eth.getTransactionCount(account_from) + 1
        dict_transaction["nonce"] = newNonce
    else:
        dict_transaction["nonce"] = web3.eth.getTransactionCount(account_from)
    print(dict_transaction["nonce"])
    count_nonce = dict_transaction['nonce']
    return dict_transaction


def createCallContract(chainId, account_from, value, network):
    web3 = Web3(network)
    dict_transaction = {
        'chainId': chainId,
        'from': account_from,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.getTransactionCount(account_from),
        'value': int(Web3.toWei(value, 'ether')),
        'gas': 2000000,
    }
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


def send_txn():
    wallets = get_wallet_edge()
    for i in range(len(wallets)):
        network = goerly
        account_from = os.environ.get('main_account')
        chainId = 5
        value = 0.1
        data = ""
        if (check_balance(wallet_key.at[i, 0], network) >= 0.1):
            logger.info(
                f"{wallet_key.at[i, 0]} have more than 0.1 eth")
            continue
        else:
            contract = wallet_key.at[i, 0]
            private_key = os.environ.get('private_key_main')
            sign_transaction(create_transaction(
                chainId, account_from, value, data, contract, network), network, private_key)


def depositETH():
    wallets = get_wallet_edge()
    for i in range(len(wallets)):
        network = goerly
        web3 = Web3(network)
        account_from = wallet_key.at[i, 0]
        chainId = 5
        gasPrice = web3.eth.gas_price
        value = 0.022
        contract_abi = [
            {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "_amount",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "_gasLimit",
                        "type": "uint256"
                    }
                ],
                "name": "depositETH",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        contract = "0xe5E30E7c24e4dFcb281A682562E53154C15D3332"
        deposit_contract = web3.eth.contract(contract, abi=contract_abi)
        private_key = wallet_key.at[i, 1]
        transaction = deposit_contract.functions.depositETH(20000000000000000, 40000).buildTransaction(createCallContract(
            chainId, account_from, value, network))
        sign_transaction(transaction, network, private_key)


def wrapETHandUnwrap():
    wallets = get_wallet_edge()
    for i in range(len(wallets)):
        contract = "0xa1EA0B2354F5A344110af2b6AD68e75545009a03"
        contract_abi = [
            {
                "name": "withdraw",
                "type": "function",
                "inputs": [
                    {
                        "name": "wad",
                        "type": "uint256"
                    }
                ],
                "outputs": []
            },
            {
                "name": "deposit",
                "type": "function",
                "inputs": [
                    {
                        "name": "amount",
                        "type": "uint256"
                    }
                ],
                "outputs": []
            }
        ]
        network = scroll_alpha
        web3 = Web3(network)
        wrap_contract = web3.eth.contract(contract, abi=contract_abi)
        account_from = wallet_key.at[i, 0]
        chainId = 534353
        value = 0.01
        private_key = wallet_key.at[i, 1]
        while (check_balance(wallet_key.at[i, 0], network) < 0.05):
            time.sleep(3)
        transactionWrap = wrap_contract.functions.deposit().buildTransaction(createCallContract(
            chainId, account_from, value, network))
        sign_transaction(transactionWrap, network, private_key)

        time.sleep(5)

        new_value = 0
        transactionUnwrap = wrap_contract.functions.withdraw(10000000000000000).buildTransaction(createCallContract(
            chainId, account_from, new_value, network))
        sign_transaction(transactionUnwrap, network, private_key)


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


def withdrawDeposit():
    wallets = get_wallet_edge()
    for i in range(len(wallets)):
        network = scroll_alpha
        web3 = Web3(network)
        account_from = wallet_key.at[i, 0]
        chainId = 534353
        value = 0.07
        contract_abi = [
            {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "_amount",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "_gasLimit",
                        "type": "uint256"
                    }
                ],
                "name": "withdrawETH",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        contract = "0x6d79Aa2e4Fbf80CF8543Ad97e294861853fb0649"
        deposit_contract = web3.eth.contract(contract, abi=contract_abi)
        private_key = wallet_key.at[i, 1]
        transaction = deposit_contract.functions.withdrawETH(60000000000000000, 160000).buildTransaction(createCallContract(
            chainId, account_from, value, network))
        sign_transaction(transaction, network, private_key)


# def withdrawDeposit():
#     wallets = get_wallet_edge()
#     for i in range(len(wallets)):
#         network = scroll_alpha
#         web3 = Web3(network)
#         account_from = wallet_key.at[i, 0]
#         chainId = 534353
#         contract_abi = [
#             {
#                 "inputs": [
#                     {
#                         "internalType": "uint256",
#                         "name": "_amount",
#                         "type": "uint256"
#                     },
#                     {
#                         "internalType": "uint256",
#                         "name": "_gasLimit",
#                         "type": "uint256"
#                     }
#                 ],
#                 "name": "withdrawETH",
#                 "outputs": [],
#                 "stateMutability": "nonpayable",
#                 "type": "function"
#             }
#         ]
#         contract = "0x6d79Aa2e4Fbf80CF8543Ad97e294861853fb0649"
#         deposit_contract = web3.eth.contract(contract, abi=contract_abi)
#         private_key = wallet_key.at[i, 1]

#         gas_price = web3.eth.gasPrice
#         balance = web3.eth.getBalance(account_from)
#         print(balance)
#         gas_limit = 160000
#         fee = gas_limit * gas_price
#         value_to_withdraw = balance - fee
#         print(value_to_withdraw)
#         dict_transaction = {
#             'chainId': chainId,
#             'from': account_from,
#             'gasPrice': gas_price,
#             'nonce': web3.eth.getTransactionCount(account_from),
#             'value': value_to_withdraw,
#             'gas': gas_limit,
#         }
#         transaction = deposit_contract.functions.withdrawETH(
#             value_to_withdraw - 50000000000000000, gas_limit).buildTransaction(dict_transaction)
#         sign_transaction(transaction, network, private_key)


def backSendETH():
    wallets = get_wallet_edge()
    for i in range(len(wallets)):
        network = goerly
        web3 = Web3(network)
        account_from = wallet_key.at[i, 0]
        chainId = 5
        value = web3.eth.get_balance(wallet_key.at[i, 0]) - 0.001
        data = ""
        if (check_balance(wallet_key.at[i, 0], network) == 0):
            logger.info(
                f"{wallet_key.at[i, 0]} don`t hane ETH")
            continue
        else:
            contract = os.environ.get('main_account')
            private_key = wallet_key.at[i, 1]
            sign_transaction(create_transaction(
                chainId, account_from, value, data, contract, network), network, private_key)


def main():
    send_txn()
    depositETH()
    wrapETHandUnwrap()
    BufficornBatle()


def comeBAck():
    withdrawDeposit()
    backSendETH()


withdrawDeposit()
