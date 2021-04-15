# Eoa historical bal
The purpose of this repo is to query inventory-service.json file historically from the Ethereum blockchain and return each ethereum addresses balance accross multiple token types

## Setup
```
git clone git@github.com:LiquidityProviders/eoa-historic-bal.git
cd eoa-historic-bal
git submodule update --init --recursive
./install.sh
```
go to https://observablehq.com/@levity/search-for-a-block-by-timestamp and enter in the timestamp you would like Dydx balance data for

Enter in the block number returned by the link above into the start script below as the `--block-number-to-query` argument.

Ensure you have created the startfile, added it to the homedirectory of the repo (see example startfile below), and make sure it is executable.

create the `addresses_config.json` file in the repository's root directory, it should look something like this:
```

{
   "tokens": {
      "ETH": {
        "tokenAddress": "0x0000000000000000000000000000000000000000"
      },
      "DAI": {
        "tokenAddress": "0x6B175474E89094C44Da98b954EedeAC495271d0F"
      },
      "WETH": {
        "tokenAddress": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
      },
      "USDC": {
        "tokenAddress": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "tokenDecimals": 6
      },
      "MKR": {
        "tokenAddress": "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2"
      },
      "TBTC": {
        "tokenAddress": "0x8dAEBADE922dF735c38C80C7eBD708Af50815fAa"
      },
      "LEV": {
        "tokenAddress": "0x0f4ca92660efad97a9a70cb0fe969c755439772c",
        "tokenDecimals": 9
      },
      "L2": {
        "tokenAddress": "0xBbff34E47E559ef680067a6B1c980639EEb64D24"
      },
      "WBTC": {
        "tokenAddress": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
        "tokenDecimals": 8
      }
    },
   "reserve": {
     "id": "reserve",
     "name": "Reserve account",
     "type": "reserve-account",
     "config": {
       "address": "0x00000000000000000000000000000",
       "minEthBalance": 5.0
     }
   },
      "members": [
     {
       "id": "oasis_server1",
       "name": "Oasis Server1",
       "type": "oasis-market-maker-keeper",
       "deposit": "True",
       "config": {
         "oasisAddress": "0x00000000000000000000000000000",
         "oasissupportaddress": "0x00000000000000000000000000000",
         "marketmakeraddress": "0x00000000000000000000000000000"
       },
       "tokens": {
         "ETH": {
           "minAmount": 1.0,
           "avgAmount": 5.0
         },
         "WETH": {
           "minAmount": 0.0,
           "avgAmount": 0.0,
           "maxAmount": 0.0
         },
         "SAI": {
           "minAmount": 0.0,
           "avgAmount": 0.0,
           "maxAmount": 0.0
         }
       }
     }...
  ]
}
```

Run the startfile:

./start.sh


## Example start script
```
#!/bin/bash

 source ./env
 source ./_virtualenv/bin/activate || exit
 dir="$(dirname "$0")"
 export PYTHONPATH=$PYTHONPATH:$dir:$dir/lib/pymaker

 exec python3 -m eoa_historic_bal.main \
     --rpc-host <NODE> \
     --rpc-timeout 30 \
     --block-number-to-query <BLOCKNUM>\
     --addresses-config 'inventory_service_config.json' \
     $@ 2> >(tee -a ${LOGS_DIR:?}/eoa_historical_bal.log >&2)

```

