const Web3 = require("web3");
const { geth_poa_middleware } = require("web3-middleware");
const { TransactionNotFound } = require("web3-core-helpers");
const { createLogger } = require("loguru");
const time = require("time");
const Uniswap = require("uniswap");
const copy = require("copy");
const os = require("os");
const dotenv = require("dotenv");
const HexBytes = require("hexbytes");
const pd = require("pandas");

const wallet_key = pd.read_excel("./wallets/wallets.xlsx", {
  sheet_name: "wallet",
  header: null,
});

const dotenv_path = path.join(__dirname, ".env");
if (fs.existsSync(dotenv_path)) {
  dotenv.config({ path: dotenv_path });
}

const scroll_alpha = new Web3.providers.HttpProvider(
  "https://alpha-rpc.scroll.io/l2"
);
const goerly = new Web3.providers.HttpProvider(
  "https://endpoints.omniatech.io/v1/eth/goerli/public"
);
let count_nonce = 0;

function get_wallet_edge() {
  const file = fs.readFileSync("wallets/wallet_edge.txt", "utf8");
  const _main_wallet = file.trim().split("\n");
  return _main_wallet;
}

function check_balance(_main_wallet, network) {
  const web3 = new Web3(network);
  return web3.utils.fromWei(web3.eth.getBalance(_main_wallet), "ether");
}

function create_transaction(
  chainId,
  account_from,
  value,
  data,
  contract,
  network
) {
  global.count_nonce;
  const web3 = new Web3(network);
  while (count_nonce == web3.eth.getTransactionCount(account_from)) {
    time.sleep(5);
  }
  const dict_transaction = {
    chainId: chainId,
    from: account_from,
    to: contract,
    gasPrice: web3.eth.getGasPrice(),
    nonce: web3.eth.getTransactionCount(account_from),
    value: web3.utils.toWei(value.toString(), "ether"),
    data: data,
    gas: 2000000 * 2,
  };
  count_nonce = dict_transaction["nonce"];
  return dict_transaction;
}

function sign_transaction(dict_transaction, network, private_key) {
  const web3 = new Web3(network);
  if (network == scroll_alpha) {
    web3.middleware_onion.inject(geth_poa_middleware, (layer = 0));
  }
  const signed_txn = web3.eth.accounts.signTransaction(
    dict_transaction,
    private_key
  ); // тут надо будет ввести перемнную для закрытого ключа
  const txn_hash = web3.eth.sendSignedTransaction(signed_txn.rawTransaction);
  while (true) {
    try {
      const txn = web3.eth.getTransactionReceipt(txn_hash.hex());
      if (txn["status"] == 1) {
        logger.success(
          `Transaction ${dict_transaction["from"]} to ${
            dict_transaction["to"]
          } send - ${txn_hash.hex()}`
        );
      } else {
        logger.error(
          `Transaction ${dict_transaction["from"]} to ${
            dict_transaction["to"]
          } not send - ${txn_hash.hex()}`
        );
      }
      break;
    } catch (e) {
      if (e instanceof TransactionNotFound) {
        continue;
      }
      throw e;
    }
  }
}

function createHEX(value, gasPrice) {
  const valueWei = web3.utils.toWei(value.toString(), "ether");
  console.log(valueWei);
  const amount = parseInt(valueWei) + parseInt(gasPrice);
  console.log(amount);
  const hex = web3.utils.toHex(amount);
  console.log(hex);
}

function send_txn() {
  const wallets = get_wallet_edge();
  for (let i = 0; i < wallets.length; i++) {
    const network = "goerly";
    const account_from = process.env.main_account;
    const chainId = 5;
    const value = 0.01;
    const data = "";
    if (check_balance(wallet_key[i][0], network) >= 0.01) {
      console.log(`${wallet_key[i][0]} have more than 0.01 eth`);
      continue;
    } else {
      const contract = wallet_key[i][0];
      const private_key = process.env.private_key_main;
      sign_transaction(
        create_transaction(
          chainId,
          account_from,
          value,
          data,
          contract,
          network
        ),
        network,
        private_key
      );
    }
  }
}

// *Сделать цикл для разных кошелей. Разобраться как брат только мультипликатор функции
// *и подставлять к нему закодированные данные

function depositETH() {
  const wallets = get_wallet_edge();
  for (let i = 0; i < wallets.length; i++) {
    const network = "goerly";
    const account_from = wallet_key[i][0];
    const chainId = 5;
    const value = 0.01;
    // "0x9f8420b3000000000000000000000000000000000000000000000000002386f26fc100000000000000000000000000000000000000000000000000000000000000009c40"
    const data = `0x9f8420b3${value.toString()}0000000000000000000000000000000000000000000000000000000000009c40`;
    const contract = "0xe5E30E7c24e4dFcb281A682562E53154C15D3332";
    const private_key = wallet_key[i][1];
    sign_transaction(
      create_transaction(chainId, account_from, value, data, contract, network),
      network,
      private_key
    );
  }
}
