from bs4 import BeautifulSoup
import json
import time
import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware
from loguru import logger
import struct

# *https://ethereum.stackexchange.com/questions/62247/how-to-use-a-metamask-wallet-from-web3-py - как отправить транзу на контракт
# !Начать следующий раз с подключения кошелька к сату --> потом уже запрос пост на получение токенов --> потом отправка транз на контракт


# private_key = "1effc9349ce5481f0cdf0fb07e8845be6051ee58c57d6e95e6b90bfb8f55a964"
# account_from = "0x04Ee5860e4fce5560865197BCfb83b9192ce4dbD"
# account_contract = "0x47c02b023b6787ef4e503df42bbb1a94f451a1c0"


# scroll_l1 = Web3.HTTPProvider('https://prealpha-rpc.scroll.io/l1')
# scroll_l2 = Web3.HTTPProvider('https://prealpha-rpc.scroll.io/l2')

# web3 = Web3(scroll_l1)
# logger.info(f"Is connected: {web3.isConnected()}")
# web3.middleware_onion.inject(geth_poa_middleware, layer=0)


# def send_txn(account_from, account_contract):

#     gas = 2_000_000
#     nonce = web3.eth.getTransactionCount(account_from)
#     txn = {
#         'chainId': 534351,
#         'from': account_from,
#         'to': account_contract,
#         'value': 0.0001,
#         'nonce': nonce,
#         'data': '0x5358fbda0000000000000000000000000000000000000000000000000000000000000000',
#         'gasPrice': web3.eth.gas_price,
#         'gas': gas,
#     }
#     return txn


# transaction = send_txn(account_from, account_contract)


# # 2. Подписываем транзакцию с приватным ключом
# signed_txn = web3.eth.account.sign_transaction(transaction, private_key)


# # 3. Отправка транзакции
# txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

# # Получаем хэш транзакции
# # Можно посмотреть статус тут https://testnet.bscscan.com/
# hash = txn_hash.hex()
# txn = web3.eth.get_transaction_receipt(hash)
# logger.info(txn)


def get_response(url, method='POST'):
    keys = {"address": "0x7A8463B955c403ebd4611b18743a40aeBa0d7d4F",
            "h-captcha-response": "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.hKdwYXNza2V5xQQNHAnkIVwbnlu76Xyvp6Zrjp-TfJAHFKtQiO5CG3zydkHaEPjTkbDNkz3GgkqdEUqhalHsRnRQZuQ_-RoIOKBmtJNSgExqUzIj9jPlOUWT3xNQlk9LTO-fNRYa52Y0f6NqvpcBkEXkwMAhrkhBDfoiExLT7h3Qhx39s6kk5Gg8tB2IkVO08otdHdqJBWgIKeHWEaXrEL_uiUR41fqCtcc9tAYZ_ZHSDpQHZuJciejWPLSUVNPrDMMwmHXpj3MjqgXDv5vGVOyL3-iTf4RlOP6gwr6R3Y6vq0ccoF-XJwA6QIJhIE99RX35tosf9MyrL338EhyVQ_cTyCUp7BzITotTthJjkraz-hxQp6VUzJOrmsan9NqKRyNsyQvDq8i-HMvPx9n7zQpUcOfMcbp4Ka-HttYA_xp8lJTWUvCptexvIlu-QNT1f_rH5lTRn02BiEaKOr5rIe_nyVPdw67RhF78SQ8IO-cQQLN2-5bpf87o4UR-8U4IP_MlF14SdaWA-HQzTJvoPyKbSUKggbCODK_fnjRGuJSp7iT2dCx3eEzYGnjrUq4GNE8gNj1rq6OZmXuwvF8E54UOWhLuBVVu-ZCe38ffn6wPvIP-6FQBw2LdLOTsSbPpR1y3WmSOcnLyN-8_0gjINYVhc8OJhLq9plVtQcX5sJWtZRhBBvb0tTHeNdB_awOBJ9BzpnObEyXAMkJExoV1ujB0kf9lnagcWFBSAbwx2uYiAnvTDg-wPHY_1KH1qIJuKYVOIEHfjJYUGLpX7Xqs4pI3rbTiCtW9xvIlZRfayf-Gz1yyOJAICDXMCeHxMS3Q7L1VSEpnWJcW--MCrzKS5QfPjqxIC3uKTpM3BqSU0cpeUXRQ8uvc_paZBV2xnX5Vrhl0rWrFWpYwJSv3VwAgD_O_migePNvtnoO4UePS-5pJ5pqwcNPbCpBHwsPsG4-3nBsnFy8X93gaIPHSFTJrqBrZqv-9VZ0AIeuNTYf0qo36SehO-oBomyIDSlj7pbjigTGb5TJAgqkUVBCVfqDIonaGR7MJeFRJ6KPHc92YmDJYb_nhWkMG7A22Xmip4RM6abOezX0g7BgNxYQq4kiOFHiKsW7PeHDE3XXSSLlK5V1ARP8veN6eE3rpzWO4cxi3Eeuvz-wFL-1GBNsjyTqmHFCte3mJw_M-sJkfTgFt0CvfCyy7SGQZH8fX34WZpKbLg6UKA-BaWvTy4urxiEv70WfohdeIXEqFSTQssj_iaYpjF322sVpyzxMCLHRHrkg_dWee4Pa0p7HwRQ01qVc-WGNo4tm4lZGFAU_EzyjTd1Ph8KpfyxXA77FEugEZhQ-UURIm5gNCbJo4Zbgt_-F8idCDAUc996vuWSKFLXI8Xh_IokswVd-ihR-jZXhwzmP8I_uoc2hhcmRfaWTOFZnkVKJwZAA.vvF-uazno6wMya1iwcFp2vErsy7DHV5q4nkbC6UcIns"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win32; x86) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "cookie": "__cfduid=da350b8e01521848041e557b8840722281595350016; PHPSESSID=rgr9ath2l0aumnkbt9s4k41if4"
    }
    response = requests.post(url, headers=headers, params=keys)
#response = requests.request(method, url, headers=headers, timeout=15)
    text_response = response.text
    return text_response


while True:
    res = get_response("https://prealpha-api.scroll.io/faucet/api/claim")
    text_response = res
    parse_data = BeautifulSoup(res, features="lxml")
    out = parse_data.find('button', {'class': 'MuiButtonBase-root'})
    # if "Request tokens every 24h." in text_response:
    #     print('Max claims lets wait for a day')
    #     time.sleep(86400)
    #     continue
    # if out is not None:
    #     print('Logged out')
    #     res = get_response(
    #         "https://faucetbch.com/index.php?login=true&email=qqxfgklk4el69e5u45wphqm245k3t5rhpcwac7uhwe")
    #     res = get_response("https://faucetbch.com/index.php?a=faucet2")
    #     print(res)
    #     time.sleep(2)
    print(res)
    break
