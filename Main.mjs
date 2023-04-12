import { sendETHtoWallets } from "./SendTransaction.mjs";
const { fs } = require("fs");

fs.readFile("./wallets/Private_key.txt", "utf8", (err, data) => {
  if (err) throw err;
  console.log(data);
});

// научить читать JS из файла
// for (i = 0; i <= 5; i++) {
//   let wallet = sendETHtoWallets();
// }
