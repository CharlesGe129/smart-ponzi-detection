import os
from src.open_data import OPCODES


PATH_PRE = '../dataset/'
PATH_SUR = '/op_count/'


def load_if_revert():
    revert = {}
    for directory in [PATH_PRE + 'ponzi/opcode/', PATH_PRE + 'non_ponzi/opcode/']:
        for filename in os.listdir(directory):
            if not filename.endswith(".json"):
                continue
            with open(directory + filename) as f:
                revert[filename.split(".json")[0]] = 'REVERT' in f.read()
    return revert


def start():
    revert_dict = load_if_revert()
    i = 0
    # for folder in ['ponzi', 'non_ponzi']:
    for folder in ['ponzi']:
        op_times = [0 for i in range(len(OPCODES))]
        path = PATH_PRE + folder + PATH_SUR
        for filename in os.listdir(path):
            if not filename.endswith('.csv'):
                continue
            if revert_dict[filename.split('.')[0]]:
                continue
            i += 1
            print(i)
            with open(path + filename) as f:
                load_op_times_one_file(f, op_times)
        print(f"folder={folder}")
        for op_index in range(len(op_times)):
            print(f"OPCODE={OPCODES[op_index]}, avg_times={(op_times[op_index])/i}")


def load_op_times_one_file(f, op_times):
    for line in f.readlines():
        code = line.split(',')[0]
        if code == 'REVERT':
            continue
        times = int(line.split(',')[1])
        op_times[OPCODES.index(code)] += times
    # print(op_times)


if __name__ == '__main__':
    start()
