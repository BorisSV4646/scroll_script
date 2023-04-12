const Web3 = require("web3");
require("dotenv").config();

export async function sendETHtoWallets(to) {
  const web3 = new Web3(
    new Web3.providers.HttpProvider("https://rpc.ankr.com/eth_goerli")
  );

  const myAddress = web3.eth.accounts.privateKeyToAccount(private_key_main);

  const nonce = await web3.eth.getTransactionCount(
    myAddress["address"],
    "latest"
  );

  console.log(nonce);

  const transaction = {
    to: to,
    value: Web3.utils.toHex(Web3.utils.toWei("0.1", "ether")),
    gas: Web3.utils.toHex(21000),
    nonce: nonce,
  };

  const signedTx = await web3.eth.accounts.signTransaction(
    transaction,
    private_key_main
  );

  web3.eth.sendSignedTransaction(
    signedTx.rawTransaction,
    function (error, hash) {
      if (!error) {
        console.log(
          "🎉 The hash of your transaction is: ",
          hash,
          "\n Check Alchemy's Mempool to view the status of your transaction!"
        );
      } else {
        console.log(
          "❗Something went wrong while submitting your transaction:",
          error
        );
      }
    }
  );
}
