import os
import json


def start(path_db='../dataset/sm_database/'):
    PATH_DB = path_db
    PATH_OPCODE = PATH_DB + '../ponzi/opcode/'
    PATH_OPCODE_NP = PATH_DB + '../non_ponzi/opcode/'

    revert_dict = load_if_revert([PATH_OPCODE, PATH_OPCODE_NP])
    contract_create_block = dict()
    for directory in [PATH_DB + 'normal/', PATH_DB + 'normal_np/']:
        print(f"Loading {directory}")
        for filename in os.listdir(directory):
            if not filename.endswith("_0.json"):
                continue
            addr = filename.split('_0')[0]
            if addr not in revert_dict or revert_dict[addr]:
                continue
            contract_create_block[addr] = get_contract_create_block(directory + filename)
    return contract_create_block


def load_if_revert(directories):
    revert = {}
    for path in directories:
        for filename in os.listdir(path):
            if not filename.endswith(".json"):
                continue
            with open(path + filename) as f:
                revert[filename.split(".json")[0]] = 'REVERT' in f.read()
    return revert


def get_contract_create_block(path):
    with open(path) as f:
        data = json.loads(f.read())
        return int(data[0]['blockNumber'])


if __name__ == '__main__':
    a = start()
    print(len(a))
    print(max(a.values()))
    print(min(a.values()))
