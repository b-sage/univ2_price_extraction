import argparse
import json
import pandas as pd
from hexbytes import HexBytes
from eth_abi import decode
from eth_utils import to_checksum_address
from evm_client.batch_client import BatchEthClient
from evm_client.batch_client.utils import flatten
from evm_client.sync_client import SyncEthClient
from evm_client.crypto_utils import hex_to_int, unpack_address
from utils import get_pools
from constants import (
    UNIV2_FACTORY, 
    UNIV2_FACTORY_DEPLOYMENT_BLOCK,
    PAIR_CREATED_TOPIC
)
from config import (
    ETH_RPC_URL,
    PAIRS_JSON,
    PAIRS_CSV
)

def unpack_new_pair_log_data(data):
    pair_address, _ = decode(['address', 'uint256'], HexBytes(data))
    return to_checksum_address(pair_address), _

def get_last_block_searched(pools):
    if not pools:
        return 0
    return max([v['deployment_block'] for v in pools.values()])

def save_pools(pools, path=PAIRS_JSON):
    with open(path, 'w+') as f:
        json.dump(pools, f)

def save_pools_as_csv(pools, path=PAIRS_CSV):
    df = pd.DataFrame(list(pools.values()))
    df = df.set_index('pair')
    df.to_csv(path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rpc_url', required=False, type=str, default=ETH_RPC_URL)
    parser.add_argument('--univ2_factory', required=False, type=str, default=UNIV2_FACTORY)
    args = parser.parse_args()

    eth_client = SyncEthClient(args.rpc_url)
    batch_client = BatchEthClient(args.rpc_url) 
    pools = get_pools()
    
    start_block = get_last_block_searched(pools)
    if start_block == 0:
        start_block = UNIV2_FACTORY_DEPLOYMENT_BLOCK
    else:
        #TODO: see if this introduces off by 1 error
        start_block += 1 
    end_block = eth_client.block_number()
    
    logs_generator = batch_client.get_logs(UNIV2_FACTORY, [PAIR_CREATED_TOPIC], start_block, end_block, block_inc=2000, req_inc=100)
    for l in logs_generator:
        block_num = l['blockNumber']
        pair, _ = unpack_new_pair_log_data(l['data'])
        token0 = unpack_address(l['topics'][1])
        token1 = unpack_address(l['topics'][2])
        pools[pair] = {"pair": pair, "token0": token0, "token1": token1, "deployment_block": block_num}
    save_pools(pools)
    save_pools_as_csv(pools) 
