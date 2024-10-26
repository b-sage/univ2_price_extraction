import argparse
from utils import get_pools
from config import TOKENS_JSON

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tokenA', required=True, type=str)
    parser.add_argument('--tokenB', required=True, type=str)
    args = parser.parse_args()

    assert args.tokenA != args.tokenB, "Cannot use same token"

    pools = get_pools()
    tokens = get_pools(path=TOKENS_JSON)

    for pool, pool_data in pools.items():
        token0 = pool_data['token0']
        token1 = pool_data['token1']
        if (args.tokenA == token0 or args.tokenA == token1) and (args.tokenB == token0 or args.tokenB == token1):
            token0_data = tokens.get(token0)
            token1_data = tokens.get(token1)
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
             
