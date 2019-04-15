import os
import json

DATABASE_PATH = "/Users/charlesge/charles/university/Master_project/smart-ponzi-detection/dataset/sm_database_old/"


def get_np_creation():
    creation_timestamps = {}
    with open(DATABASE_PATH + "normal_np.json") as f:
        while True:
            contract_hash = f.readline()
            if not contract_hash:
                break
            creation_timestamps[contract_hash] = get_creation_timestamp(f.readline())
    print(len(creation_timestamps))
    print(min(creation_timestamps.values()))
    print(max(creation_timestamps.values()))


def get_creation_timestamp(content):
    timestamps = []
    # print(len(content.split('"timeStamp":"')[1:]))
    for each in content.split('"timeStamp":"')[1:]:
        t = each.split('"')[0]
        timestamps.append(int(t))
    return min(timestamps)


if __name__ == '__main__':
    get_np_creation()
