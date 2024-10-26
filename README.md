# Uniswap V2 Price Extraction

## Setup
Set Environment Variables:
```
export ETH_RPC_URL={YOUR RPC URL}
export UNI_DATA_DIR={YOUR DATA DIR}
```
The uni data dir is required, while the eth rpc url will default to llamarpc if not provided.

Install requirements:
```
pip install -r requirements.txt
```

## Usage
The get_tokens script is dependent upon completion of the extract_pools script. These can either be run in order, or use the run_token_pull shell script provided.

