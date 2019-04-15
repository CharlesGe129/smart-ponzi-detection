import os
import statistics
from src.open_data import OPCODES


PATH_P = '../dataset/ponzi/op_count/'
PATH_NP = '../dataset/non_ponzi/op_count/'


def start():
    for path in [PATH_P, PATH_NP]:
        op_data = {'avg': [0 for each in OPCODES], 'stdev': [list() for each in OPCODES]}
        count = 0
        print(f"============================\n{path}")
        for filename in os.listdir(path):
            if not filename.endswith(".csv"):
                continue
            count += load_op(path + filename, op_data)
        cal_avg_and_stdev(op_data, count)


def load_op(path, op_data):
    with open(path) as f:
        if "REVERT" in f.read():
            return 0
    with open(path) as f:
        cur_opcodes = {}
        for line in f.readlines():
            code = line.split(",")[0]
            num = int(line.split(",")[1])
            index = OPCODES.index(code)
            op_data['avg'][index] += num
            cur_opcodes[index] = num
        for i in range(len(OPCODES)):
            if i in cur_opcodes:
                op_data['stdev'][i].append(cur_opcodes[i])
            else:
                op_data['stdev'][i].append(0)
    return 1


def cal_avg_and_stdev(op_data, count):
    for i in range(len(OPCODES)):
        opcode = OPCODES[i]
        avg = op_data['avg'][i] / count
        # print(op_data['stdev'][i])
        print(f"{opcode}, avg={avg}, stdev={round(statistics.stdev(op_data['stdev'][i]), 6)}")


def top_30_draft_to_result():
    with open('../report_per_day/top_30_avg_stdev_draft.txt') as f:
        content = f.readlines()
    data = {'p': {}, 'np': {}}
    for line in content[2:51]:
        line = line.strip('\n')
        code = line.split(', ')[0]
        avg = line.split(', ')[1]
        stdev = line.split(', ')[2]
        data['p'][code] = {'avg': avg, 'stdev': stdev}
    for line in content[53:]:
        line = line.strip('\n')
        code = line.split(', ')[0]
        avg = line.split(', ')[1]
        stdev = line.split(', ')[2]
        data['np'][code] = {'avg': avg, 'stdev': stdev}
    opcodes = ['SSTORE', 'POP', 'MSTORE', 'SWAP1', 'STOP', 'DUP9', 'RETURN', 'SWAP2', 'DUP1&2', 'JUMP', 'DUP3', 'SMAP3', 'PUSH', 'DUP4', 'SWAP4', 'JUMPI', 'DUP6', 'DUP5', 'CODECOPY', 'size_info', 'nbr_tx_in', 'lifetime', 'SWAP7', 'num_paid_in_addr', 'gini_in', 'SWAP5', 'overlap_in_out_addr', 'SWAP6', 'gini_time_out', 'avg_time_btw_tx']
    for i in range(len(opcodes)):
        print(f"{i+1}, {opcodes[i]}")
        if opcodes[i] not in data['p']:
            print(f"\tPonzi: avg=xxxxxx, stdev=xxxxxx; Non-Ponzi: avg=xxxxxx, stdev=xxxxxx")
        else:
            print(f"\tPonzi: avg={data['p'][opcodes[i]]['avg']}, stdev={data['p'][opcodes[i]]['stdev']}; Non-Ponzi: avg={data['np'][opcodes[i]]['avg']}, stdev={data['np'][opcodes[i]]['stdev']}")


if __name__ == '__main__':
    start()

