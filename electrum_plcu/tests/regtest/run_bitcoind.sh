#!/usr/bin/env bash
export HOME=~
set -eux pipefail
mkdir -p ~/.plcultima
cat > ~/.plcultima/plcultima.conf <<EOF
regtest=1
txindex=1
printtoconsole=1
rpcuser=doggman
rpcpassword=donkey
rpcallowip=127.0.0.1
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333
fallbackfee=0.0002
[regtest]
rpcbind=0.0.0.0
rpcport=18554
EOF
rm -rf ~/.plcultima/regtest
plcultimad -regtest &
sleep 6
plcultima-cli createwallet test_wallet
addr=$(plcultima-cli getnewaddress)
plcultima-cli generatetoaddress 150 $addr
tail -f ~/.plcultima/regtest/debug.log
