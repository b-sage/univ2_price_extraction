import os

ETH_RPC_URL = os.getenv('ETH_RPC_URL') if os.getenv('ETH_RPC_URL') else 'https://eth.llamarpc.com'

DATA_DIR = os.getenv('UNI_DATA_DIR')

PAIRS_PATH = f"{DATA_DIR}/pairs"
PAIRS_JSON = f'{PAIRS_PATH}/pairs.json'
PAIRS_CSV = f'{PAIRS_PATH}/pairs.csv'

TOKENS_PATH = f"{DATA_DIR}/tokens"
TOKENS_JSON = f"{TOKENS_PATH}/tokens.json"
TOKENS_CSV = f"{TOKENS_PATH}/tokens.csv"

BAD_TOKENS_CSV = f"{TOKENS_PATH}/bad_tokens.csv"

PRICES_PATH = f"{DATA_DIR}/prices"
