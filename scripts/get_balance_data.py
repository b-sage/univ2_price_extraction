import argparse
import csv
from evm_client.batch_client.eth_client import BatchEthClient
from evm_client.sync_client.eth_client import SyncEthClient
from evm_client.core.eth_core import EthCore
from evm_client.batch_client.utils import chunks
from evm_client.types.transaction import Transaction
from evm_client.crypto_utils import hex_to_int
from utils import get_pools, get_bad_tokens
from config import (
    ETH_RPC_URL,
    PAIRS_JSON,
    TOKENS_JSON,
    PRICES_PATH
)

def build_balance_of_call_data(target):
    return '0x70a08231000000000000000000000000' + target[2:]

def build_bodies(pool, bad_tokens, end_block, blocks_per_price=1000):
    token0 = pool['token0']
    token1 = pool['token1']
    if token0 in bad_tokens or token1 in bad_tokens:
        assert False, "Pool includes a bad token, please try another pool"
    pair = pool['pair']
    deployment_block = pool['deployment_block']
    calldata = build_balance_of_call_data(pair) 
    t0_tx = Transaction(calldata, to=token0)
    t1_tx = Transaction(calldata, to=token1)
    return _build_bodies(t0_tx, t1_tx, deployment_block, end_block, pair, blocks_per_price=blocks_per_price)

def _build_bodies(token0_tx, token1_tx, deployment_block, end_block, pool, blocks_per_price=1000):
    bodies = []
    idx_map = {}
    idx = 1
    for block_range in chunks(list(range(deployment_block, end_block)), blocks_per_price):
        block = block_range[-1]
        bodies.append(EthCore.get_eth_call_body(token0_tx, block_number=block, request_id=idx))
        idx_map[idx] = f"{token0_tx.to}_{pool}_{block}"
        idx += 1
        bodies.append(EthCore.get_eth_call_body(token1_tx, block_number=block, request_id=idx))
        idx_map[idx] = f"{token1_tx.to}_{pool}_{block}"
        idx += 1
    return bodies, idx_map

def get_block_timestamps(batch_client, block_nums, req_inc=1000):
    res = batch_client.get_blocks_by_numbers(block_nums, req_inc=req_inc)
    result = {}
    for res_ in res:
        result = {**result, **{hex_to_int(r['number']): hex_to_int(r['timestamp']) for r in res_.values()}}
    return result

def save_prices(prices, pair_addr, base_path=PRICES_PATH):
    path = PRICES_PATH + f'/{pair_addr}.csv'
    with open(path, 'w+') as f:
        writer = csv.writer(f)
        writer.writerows(prices)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rpc_url', type=str, required=False, default=ETH_RPC_URL)
    parser.add_argument('--blocks_per_price', type=int, required=False, default=1000)
    parser.add_argument('--pairs', required=True, type=str)
    args = parser.parse_args()

    pairs = args.pairs.split(',')
    
    client = SyncEthClient(args.rpc_url)
    batch_client = BatchEthClient(args.rpc_url)

    block_number = client.block_number()
    
    pools = get_pools()
    tokens = get_pools(path=TOKENS_JSON)
    bad_tokens = get_bad_tokens()
    
    for pair in pairs:
        pool = pools.get(pair)
        token0 = pool['token0']
        token1 = pool['token1']
        bodies, idx_map = build_bodies(pools.get(pair), bad_tokens, block_number, blocks_per_price=args.blocks_per_price)
        res = batch_client.make_batch_request(bodies, inc=200)
        result_map = {}
        for res_ in res:
            for idx, r in res_.items():
                t, pool_, block_num = idx_map[idx].split('_')
                if not result_map.get(block_num):
                    result_map[block_num] = {}
                token = tokens.get(t)
                result_map[block_num][t] = hex_to_int(r) / (10 ** token['decimals'])
        block_nums = [int(x) for x in list(result_map.keys())]
        blocks = batch_client.get_blocks_by_numbers(block_nums, req_inc=500) 
        ts_map = {block['number']: block['timestamp'] for block in blocks}
        results = [[ts_map[int(block_)], r[token0], r[token1], int(block_)] for block_, r in result_map.items()]
        results.insert(0, ['timestamp', 'token0_balance', 'token1_balance', 'block_number'])
        save_prices(results, pair)
