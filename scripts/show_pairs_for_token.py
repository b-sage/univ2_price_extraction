import argparse
from utils import get_pools
from config import TOKENS_JSON

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', required=True, type=str)
    args = parser.parse_args()

    pools = get_pools()
    tokens = get_pools(path=TOKENS_JSON)
    for pool, pool_data in pools.items():
        token0 = pool_data['token0']
        token1 = pool_data['token1']
        if token0 == args.token or token1 == args.token:
            token0_data = tokens.get(token0)
            token1_data = tokens.get(token1)
            if token0_data and token1_data:
                print(f'''
PAIR: {pool_data['pair']}
TOKEN0 NAME: {token0_data['name']}
TOKEN0 SYMBOL: {token0_data['symbol']}
TOKEN0 ADDRESS: {token0}
TOKEN1 NAME: {token1_data['name']}
TOKEN1 SYMBOL: {token1_data['symbol']}
TOKEN1 ADDRESS: {token1}
DEPLOYMENT_BLOCK: {pool_data['deployment_block']}
        ''')
