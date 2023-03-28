from web3 import Web3
import pandas as pd
from web3.types import ABI
from loguru import logger


logger.add(
    "log/checkWallet.log",
    format="{time} | {level} | {message}",
    level="DEBUG",
)

wallet_key = pd.read_excel(
    './wallets/wallets.xlsx', sheet_name='wallet', header=None)

scroll_alpha = Web3.HTTPProvider('https://alpha-rpc.scroll.io/l2')
goerly = Web3.HTTPProvider(
    'https://endpoints.omniatech.io/v1/eth/goerli/public')

web3 = Web3(scroll_alpha)


def get_wallet_edge():
    with open('wallets/wallet_edge.txt', 'r') as file:
        _main_wallet = [row.strip() for row in file]
        return _main_wallet


def checkSuccesTransactions(wallets):
    counter = []
    for i in range(len(wallets)):
        countSecces = 0
        with open(f'./hashWallets/{wallets[i]}.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                txn = web3.eth.get_transaction_receipt(line.replace("\n", ""))
                if txn['status'] == 1:
                    countSecces += 1
                else:
                    continue
        counter.append(countSecces)
    print(counter)
    return counter


def getTransactionCount(wallets, successTrnsactions):
    for i in range(len(wallets)):
        transactions = web3.eth.get_transaction_count(wallet_key.at[i, 0])
        if transactions >= 5 and successTrnsactions[i] >= 5:
            logger.success(
                f"{wallet_key.at[i, 0]} have more than five success transactions")
        elif transactions >= 5 and successTrnsactions[i] <= 5:
            logger.error(
                f"{wallet_key.at[i, 0]} have five transactions, but not success")
        else:
            logger.error(
                f"{wallet_key.at[i, 0]} don`t have five transactions")


getTransactionCount(get_wallet_edge(),
                    checkSuccesTransactions(get_wallet_edge()))
