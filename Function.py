from evmdasm import EvmBytecode
from tqdm import tqdm
from time import sleep
from json import JSONDecodeError
from web3 import Web3
import requests


goerly = Web3.HTTPProvider(
    'https://endpoints.omniatech.io/v1/eth/goerli/public')
scroll_alpha = Web3.HTTPProvider('https://alpha-rpc.scroll.io/l2')
web3 = Web3(scroll_alpha)
address = "0x5300000000000000000000000000000000000004"


def setContractAdress(newadress):
    global address
    address = newadress


bytecode = web3.eth.get_code(address)

opcodes = EvmBytecode(bytecode).disassemble()

hashes = set()
for i in range(len(opcodes) - 3):
    if (
        opcodes[i].name == "PUSH4"
        and opcodes[i + 1].name == "EQ"
        and opcodes[i + 2].name == "PUSH2"
        and opcodes[i + 3].name == "JUMPI"
    ):
        hashes.add(opcodes[i].operand)
hashes = list(hashes)

signatures = {}


def getSignature(hash):
    global signatures
    r = requests.get(
        "https://www.4byte.directory/api/v1/signatures/?hex_signature=" + hash
    )
    try:
        res = r.json()["results"]
        res.sort(key=lambda r: r["created_at"])
        signatures[hash] = [m["text_signature"] for m in res]
        return True
    except JSONDecodeError:
        return False


for hash in tqdm(hashes):
    while not getSignature(hash):
        sleep(1)

abi = []
functions = []
for h, sign in signatures.items():
    if not sign:
        print("No match found for", h)
        continue
    if len(sign) > 2:
        print(f"Multiple matches found for {h}:", ", ".join(sign))
    functions.append(sign[0])
    name, sign = sign[0].split("(")
    args = sign[:-1].split(",")
    if args == ['']:  # ''.split() returns ['']
        args = []
    abi.append(
        {
            "type": "function",
            "name": name,
            "inputs": [{"type": t} for t in args],
            "outputs": [{"type": "unknown"}],
        },
    )

web3.codec._registry.register_decoder(
    "unknown", lambda b: bytes(b.getbuffer()))
contract = web3.eth.contract(
    address=address,
    abi=abi,
)

print(signatures)

print("Initialized interface with functions:")
for f in sorted(functions):
    print("   ", f)
