import argparse
import json
import csv
import re
import pandas as pd
from evm_client.errors import NodeError
from evm_client.batch_client.utils import flatten, chunks
from evm_client.types.transaction import Transaction
from evm_client.batch_client import BatchEthClient
from evm_client.core.eth_core import EthCore
from evm_client.crypto_utils import hex_to_int, unpack_address, decode_string, decode_bytes32
from utils import get_pools, get_bad_tokens
from config import (
    TOKENS_CSV,
    TOKENS_JSON,
    ETH_RPC_URL,
    BAD_TOKENS_CSV
)

def get_token_addresses_from_pools(pools):
    return flatten([[v['token0'], v['token1']] for v in pools.values()])

def build_calls(tokens):
    calls = []
    idx_map = {}
    idx = 1
    for t in tokens:
        #                   name        decimals        symbol
        for selector in ['0x06fdde03', '0x313ce567', '0x95d89b41']:
            call = Transaction(selector, to=t)
            idx_map[idx] = f"{t}_{selector}"
            idx += 1
            calls.append(call)
    return calls, idx_map

def save_tokens(tokens, path=TOKENS_JSON):
    with open(path, 'w+') as f:
        json.dump(tokens, f)

def save_tokens_as_csv(tokens, path=TOKENS_CSV):
    df = pd.DataFrame(list(tokens.values()))
    df = df.set_index('address')
    df.to_csv(path)

def save_bad_tokens(tokens, path=BAD_TOKENS_CSV):
    with open(path, 'w+') as f:
        writer = csv.writer(f)
        writer.writerows([[t] for t in tokens])

def sanitize(string):
    return re.sub('[^\x20-\x7E]','', string)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rpc_url', required=False, type=str, default=ETH_RPC_URL)
    args = parser.parse_args()

    batch_client = BatchEthClient(args.rpc_url)

    pools = get_pools()
    existing_tokens = get_pools(path=TOKENS_JSON)
    bad_tokens = get_bad_tokens()
    
    pool_addresses = list(pools.keys())
    for token in pool_addresses:
        if not existing_tokens.get(token):
            existing_tokens[token] = {"address": token, "name": "Uniswap V2", "decimals": 18, "symbol": "UNI-V2"}

    token_addrs = list(set([t for t in get_token_addresses_from_pools(pools) if t not in bad_tokens]))
    new_tokens = [t for t in token_addrs if not existing_tokens.get(t)] 
    calls, idx_map = build_calls(new_tokens)
    result = batch_client.calls(calls, drop_reverts=True)
    #this result indexes solution is ugly, but resolves the issue atleast
    result_indexes = []
    for idx, r in result:
        result_indexes.append(idx)
        token, selector = idx_map[idx].split('_')
        if not existing_tokens.get(token):
            existing_tokens[token] = {"address": token, "name": "", "decimals": 0, "symbol": ""}
        if r != '0x':
            if selector == '0x06fdde03':
                try:
                    existing_tokens[token]['name'] = sanitize(decode_string(r))
                except:
                    existing_tokens[token]['name'] = sanitize(decode_bytes32(r).decode().replace('\x00', ''))
            elif selector == '0x313ce567':
                existing_tokens[token]['decimals'] = hex_to_int(r)
            elif selector == '0x95d89b41':
                try:
                    existing_tokens[token]['symbol'] = sanitize(decode_string(r))
                except:
                    existing_tokens[token]['symbol'] = sanitize(decode_bytes32(r).decode().replace('\x00', ''))
    for idx, key in idx_map.items():
        if idx not in result_indexes:
            token, _ = key.split('_')
            if token not in bad_tokens:
                bad_tokens.append(token)
    save_tokens(existing_tokens)
    save_tokens_as_csv(existing_tokens)
    save_bad_tokens(bad_tokens)
