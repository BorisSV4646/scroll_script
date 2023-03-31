# Что не доделал:
#   1. Свап на юнисвап
#   2. Создание пула на юнисвап

""" def swapUSDC():
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
        transaction = newcontract.functions.swapExactTokensForTokens(0, 0, ["0x5300000000000000000000000000000000000004", "0xA0D71B9877f44C744546D649147E3F1e70a93760"], "0x04Ee5860e4fce5560865197BCfb83b9192ce4dbD").buildTransaction(createCallContract(
            chainId, account_from, value, network))
        sign_transaction(transaction, network, private_key)

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
    logger.success(txn_hash.hex()) """


""" def create_pool():
    web3 = Web3(scroll_alpha)
    logger.info(f"Is connected to SCroll Alpha: {web3.isConnected()}")
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    value = 0
    data = "1111111111"
    contract = "sassss"
    sign_transaction(create_transaction(value, data, contract)) """


# ? это вырезал - как создать HEX из нужных данных (тоесть зашифровать их в 32 бита для отправки транзакции)
""" def createHEX(value):
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
    return value """
