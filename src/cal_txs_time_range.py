import os
import json

PATH_DB = '../dataset/sm_database/'
PATH_OPCODE = PATH_DB + '../ponzi/opcode/'
PATH_OPCODE_NP = PATH_DB + '../non_ponzi/opcode/'


def start():
    revert_dict = load_if_revert()
    for directory in [PATH_DB + 'normal/', PATH_DB + 'normal_np/']:
        timestamps = list()
        for filename in os.listdir(directory):
            if not filename.endswith("_0.json"):
                continue
            addr = filename.split('_0')[0]
            if addr not in revert_dict or revert_dict[addr]:
                continue
            timestamps.append(get_contract_create_time(directory + filename))
        print(len(revert_dict))
        print(len(timestamps))
        print(f"folder={directory.split('normal')[0]}, first_tx={min(timestamps)}, last_tx={max(timestamps)}")


def load_if_revert():
    revert = {}
    for path in [PATH_OPCODE, PATH_OPCODE_NP]:
        for filename in os.listdir(path):
            if not filename.endswith(".json"):
                continue
            with open(path + filename) as f:
                revert[filename.split(".json")[0]] = 'REVERT' in f.read()
    return revert


def get_contract_create_time(path):
    with open(path) as f:
        data = json.loads(f.read())
        return data[0]['timeStamp']


if __name__ == '__main__':
    start()
