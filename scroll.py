from web3 import Web3
from get_wallet import get_main_wallet, get_all_wallets
from loguru import logger
import json
from requests import Session
# from pyuseragents import random as random_useragent
import random
import time

providers = {
    'arbitrum': {'chainId': 42161,
                 "rpc": 'https://arb1.arbitrum.io/rpc',
                 "name": 'arbitrum'},
}

gasPrice = '0.1'
slippage = '0.01'


def swap(wallet):
    session = Session()
    session.headers.update({
        'user-agent': random_useragent(),
        'connection': 'keep-alive',
        'referer': 'https://app.openocean.finance/',
        'origin': 'https://app.openocean.finance',
        'content-type': 'application/json',
    })
    tokenlist_galaxy = ['GMX', 'GNS', 'BIFI', 'STG', 'WOO', 'SUSHI',
                        'DPX', 'JOE', 'BFR', 'GRAIL', 'RDNT', 'VSTA', 'JONES']
    random.shuffle(tokenlist_galaxy, random.random)
    token_in = 'ETH'
    get_tokenlist = session.get(
        'https://open-api.openocean.finance/v3/arbitrum/tokenList')
    for token_out in tokenlist_galaxy:
        if get_tokenlist.status_code != 200:
            logger.error('status code not 200, token list not loaded')
        else:
            tokenlist = json.loads(get_tokenlist.content)['data']
            for token in tokenlist:
                if token['symbol'] == token_in:
                    token_in_address = token['address']
                if token['symbol'] == token_out:
                    token_out_address = token['address']
            amount = random.randint(1, 3) / 10000
            account = wallet['wallet'].address
            swap_quote = f'https://open-api.openocean.finance/v3/arbitrum/swap_quote?inTokenAddress={token_in_address}&outTokenAddress={token_out_address}&amount={amount}&gasPrice={gasPrice}&slippage={slippage}&account={account}'

        trx_param = session.get(swap_quote)
        if trx_param:
            openocean_tx_build = json.loads(trx_param.content)['data']
            nonce = web3.eth.get_transaction_count(wallet['wallet'].address)
            oo_gasPrice = int(openocean_tx_build['gasPrice'])
            transaction = {
                "chainId": 42161,
                'from': openocean_tx_build['from'],
                'to': openocean_tx_build['to'],
                'gas': int(openocean_tx_build['estimatedGas']) * 4,
                # 'gasPrice': oo_gasPrice,
                'maxFeePerGas': oo_gasPrice,
                'maxPriorityFeePerGas': oo_gasPrice,
                'nonce': nonce,
                'data': openocean_tx_build['data'],
                'value': int(openocean_tx_build['value'])
            }

            s_tx = web3.eth.account.signTransaction(
                transaction, wallet['wallet'].privateKey)
            tx_hash = web3.eth.sendRawTransaction(s_tx.rawTransaction)
            logger.info(f'https://arbiscan.io/tx/{web3.toHex(tx_hash)}')
            try:
                tx_log = web3.eth.wait_for_transaction_receipt(
                    tx_hash, timeout=10)
                if len(tx_log.logs) < 5:
                    global stop_txn
                    stop_txn = True
            except Exception as e:
                logger.info('timeout txn')
            t_sleep = random.randint(10, 20)
            logger.info(f'next tx after {t_sleep}s; token - {token_out}')
            time.sleep(t_sleep)


if __name__ == '__main__':
    web3 = Web3(Web3.HTTPProvider(providers['arbitrum']['rpc']))
    wallets = get_main_wallet()
    wallets = get_all_wallets(wallets)
    for wallet in wallets:
        swap(wallet)
