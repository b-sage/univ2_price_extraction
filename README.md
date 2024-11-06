# Uniswap V2 Price Extraction

## Setup
Clone Repo:
```
git clone git@github.com:b-sage/univ2_price_extraction.git
```

Set Environment Variables:
```
export ETH_RPC_URL={YOUR RPC URL}
export UNI_DATA_DIR={YOUR DATA DIR}
```
UNI_DATA_DIR is required to be set, while ETH_RPC_URL will default to llamarpc if not set.

Install requirements:
```
pip install -r requirements.txt
```

## Usage
The get_tokens script is dependent upon completion of the extract_pools script. Ex.
```
python3 extract_pools.py

python3 get_tokens.py
```

Once pool and token data has been saved down to UNI_DATA_DIR via execution of these scripts, we now need to determine pairs of interest.
Once we have determined a token we want to extract prices for we can use:
```
python3 show_pairs_for_token.py --token {TOKEN ADDRESS}
```
to show all pairs where this token is one of the underlying. Once a relevnt pair is determined, we can pass the pair address to pull_balance_data.py
like so:
```
python3 pull_balance_data.py --pairs {comma seperated list of pairs}
```

pull_balance_data will historically pull the balances of the pool every n blocks since inception of the pool, we can set n using --blocks_per_price
arg to pull_balance_data script. This will output a csv file by the name of the pair address containing timestamp, block number, token0 balance and
token1 balance.
