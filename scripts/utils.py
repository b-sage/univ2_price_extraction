import os
import json
import csv
from config import PAIRS_JSON, TOKENS_JSON, BAD_TOKENS_CSV
from evm_client.batch_client.utils import flatten

#TODO: rename
def get_pools(path=PAIRS_JSON):
    if not os.path.isfile(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def get_bad_tokens(path=BAD_TOKENS_CSV):
    if not os.path.isfile(path):
        return []
    with open(path, 'r') as f:
        return flatten([line for line in csv.reader(f)])
