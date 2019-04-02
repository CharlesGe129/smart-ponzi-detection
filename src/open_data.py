import ast
import time
import json
import os
import src.tools as tl


OPCODES = ['SWAP8', 'DUP11', 'DUP14', 'SWAP10', 'DUP15', 'LOG2', 'INVALID', 'SWAP9', 'SWAP5', 'SWAP12', 'SWAP16',
           'DUP9', 'LOG1', 'DUP12', 'SWAP11', 'SWAP2', 'MSTORE8', 'SWAP14', 'DUP13', 'POP', 'DUP8','DUP7',
           'DUP3', 'DUP4', 'MSTORE', 'SWAP3', 'CODECOPY', 'JUMP', 'DUP5', 'SWAP13', 'STOP', 'CALLDATACOPY', 'SWAP7',
           'SWAP1', 'SWAP6', 'RETURN', 'DUP6', 'SWAP4', 'REVERT', 'SELFDESTRUCT', 'DUP10', 'DUP16', 'JUMPI',
           'SSTORE', 'PUSH', 'LOG3', 'LOG4', 'Missing', 'SWAP15', 'DUP1&2']


class EtherDataToFreqAndTrDisc:
    def __init__(self):
        self.cur_time = time.clock()
        self.paths = dict()
        self.op = list()
        self.opcodes = list()
        self.revert = dict()

    def start(self):
        self.define_path()
        self.load_if_revert()
        # self.gen_op_counts()
        self.load_op()
        self.gen_op_freq()
        # self.gen_op_freq_origin()
        # self.gen_tr_dico()

    def define_path(self):
        self.cur_time = time.clock()
        print("EtherDataToFreqAndTrDisc: define variables...")
        self.paths['db'] = '../dataset/'

        self.paths['database_nml'] = self.paths['db'] + 'sm_database/normal.json'
        self.paths['database_int'] = self.paths['db'] + 'sm_database/internal.json'
        self.paths['database_op'] = self.paths['db'] + 'ponzi/op_count/'

        self.paths['database_nml_np'] = self.paths['db'] + 'sm_database/normal_np.json'
        self.paths['database_int_np'] = self.paths['db'] + 'sm_database/internal_np.json'
        self.paths['database_op_np'] = self.paths['db'] + 'non_ponzi/op_count/'

        self.paths['opcode'] = self.paths['db'] + 'ponzi/opcode/'
        self.paths['opcode_np'] = self.paths['db'] + 'non_ponzi/opcode/'

        # # For original data Marion_files
        # self.paths['db'] = '../dataset/sm_database/'
        # self.paths['database_op'] = self.paths['db'] + 'opcode/opcodes_count/'
        # self.paths['database_op_np'] = self.paths['db'] + 'opcode_np/opcode_count/bytecode_np/'

        self.cur_time = tl.compute_time(self.cur_time)
        pass

    def load_if_revert(self):
        revert = {}
        for directory in ['opcode', 'opcode_np']:
            for filename in os.listdir(self.paths[directory]):
                if not filename.endswith(".json"):
                    continue
                with open(self.paths[directory] + filename) as f:
                    revert[filename.split(".json")[0]] = 'REVERT' in f.read()
        self.revert = revert

    def load_op(self):
        self.op = [
            sorted([fname.split('.csv')[0] for fname in os.listdir(self.paths['database_op']) if fname.endswith('.csv') and not self.revert[fname.split('.csv')[0]]]),
            sorted([fname.split('.csv')[0] for fname in os.listdir(self.paths['database_op_np']) if fname.endswith('.csv') and not self.revert[fname.split('.csv')[0]]])
        ]
        print("op length: " + str(len(self.op[0])) + ", " + str(len(self.op[1])))
        self.opcodes = OPCODES

    def gen_op_counts(self):
        opcode_paths = [self.paths['database_op'].replace('op_count', 'opcode'),
                        self.paths['database_op_np'].replace('op_count', 'opcode')]
        output_path = [self.paths['database_op'], self.paths['database_op_np']]
        i = 0
        for op_index in range(2):
            for filename in os.listdir(opcode_paths[op_index]):
                i += 1
                print(f"{i}, {filename}")
                if not filename.endswith('.json'):
                    continue
                self.gen_one_op_count(opcode_paths[op_index] + filename,
                                      output_path[op_index] + filename.replace('.json', '.csv'))

    @staticmethod
    def gen_one_op_count(data_path, output_path):
        codes = [0 for each in OPCODES]
        with open(data_path) as f_opcode:
            while True:
                line = f_opcode.readline()
                if not line:
                    break
                if line[0] in ['#', ':', '\n']:
                    continue
                if '\t' in line:
                    code = line.split('\t')[1].split('(')[0].strip('\n')
                elif line.startswith('0x') and ' ' in line:
                    code = line.split(' ')[1].split('(')[0].strip('\n')
                if code in ['DUP1', 'DUP2']:
                    code = 'DUP1&2'
                elif code.startswith('Missing'):
                    code = 'Missing'
                if code not in OPCODES:
                    print(code)
                else:
                    codes[OPCODES.index(code)] += 1
        with open(output_path, 'w') as f_count:
            f_count.write('\n'.join(
                [OPCODES[i] + ',' + str(codes[i]) for i in range(len(OPCODES)) if codes[i] != 0]))

    def gen_op_freq(self):
        print("EtherDataToFreqAndTrDisc: generating op_freq.json")
        op_freq = [{}, {}]
        # op_freq = [[], []]
        for i in range(2):
            db_path = self.paths['database_op'] if i == 0 else self.paths['database_op_np']
            for addr in self.op[i]:
                with open(db_path + addr + '.csv', 'r') as f:
                    raw = f.readlines()
                    res = [0 for i in range(len(self.opcodes))]
                    if len(raw) > 1:
                        tot = 0
                        for opcode in raw:
                            opcode = opcode.strip('\n')
                            code = opcode.split(',')[0]
                            count = int(opcode.split(',')[1])
                            tot += count
                            res[self.opcodes.index(code)] += count
                    tot = tot if len(raw) > 1 else 1
                    res = [x / tot for x in res]
                    op_freq[i][addr] = res
                    # op_freq[i].append(res)

        print(f"{len(op_freq[0])}, {len(op_freq[1])}")
        self.cur_time = tl.compute_time(self.cur_time)
        with open(self.paths['db'] + 'op_freq_list.json', 'w') as outfile:
            outfile.write(json.dumps(op_freq))
            print('op_freq serialized')

    def gen_tr_dico(self):
        # tr_dico is ordered by op[]
        # tr_dico[p=0, np=1][# of Contracts][nml=0, int=1][list of TXs in nml.json] = {'blockNumber': xxx} = dict()
        tr_dico = [[[0, 0] for i in range(len(self.op[0]))], [[0, 0] for i in range(len(self.op[1]))]]
        file_paths = ['database_nml', 'database_int', 'database_nml_np', 'database_int_np']
        op_indices = [0, 0, 1, 1]
        nml_int_indices = [0, 1, 0, 1]
        for i in range(4):
            tr_index = op_indices[i]
            cur_op = self.op[tr_index]
            nml_int_index = nml_int_indices[i]
            print("loading " + file_paths[i])
            count = 0
            with open(self.paths[file_paths[i]]) as f:
                while True:
                    count += 1
                    if count % 100 == 0:
                        print(count)
                    contract_hash = f.readline().strip('\n')
                    list_line = f.readline()
                    if not contract_hash:
                        break
                    if contract_hash not in cur_op:
                        continue
                    tr_dico[tr_index][cur_op.index(contract_hash)][nml_int_index] = ast.literal_eval(list_line.strip('\n'))
        self.cur_time = tl.compute_time(self.cur_time)
        self.save_tr_dico(tr_dico)

    def save_tr_dico(self, tr_dico):
        for i in range(len(self.op[1])//500 + 1):
            with open(self.paths['db'] + 'tr_dico_nonponzi' + str(i) + '.json', 'w') as f:
                f.write(json.dumps(tr_dico[1][i*500:(i+1)*500]))
                print('serialized #' + str(i) + ' tr_dico from ' + str(i*500) + ' to ' + str((i+1)*500))
        with open(self.paths['db'] + 'tr_dico_ponzi.json', 'w') as f:
            f.write(json.dumps(tr_dico[0]))

    def gen_op_freq_origin(self):
        op_freq = [[], []]
        for add in self.op[0]:
            with open(self.paths['database_op'] + add + '.json', 'r') as f:
                # print(self.paths['database_op'] + add + '.json')
                raw = f.readlines()
                res = [0 for i in range(len(self.opcodes))]
                if len(raw) > 1:
                    tot = 0
                    for opcode in raw:
                        # count = number % 10 instead of number?
                        count = float(opcode[3])
                        tot += count
                        res[self.opcodes.index(opcode[5:-1])] = count
                else:
                    tot = 1
                res = [x / tot for x in res]
                op_freq[0].append(res)
                print(res)

        # non ponzi instances

        for add in self.op[1]:
            with open(self.paths['database_op_np'] + add + '.json', 'r') as f:
                raw = f.readlines()
                res = [0 for i in range(len(self.opcodes))]
                if len(raw) > 1:
                    tot = 0
                    for opcode in raw:
                        # count = number % 10 instead of number?
                        count = float(opcode[3])
                        tot += count
                        res[self.opcodes.index(opcode[5:-1])] = count
                else:
                    tot = 1

                res = [x / tot for x in res]
                op_freq[1].append(res)
                print(res)

        t2 = tl.compute_time(self.cur_time)

        with open(self.paths['db'] + 'op_freq.json', 'w') as outfile:
            outfile.write(json.dumps(op_freq))
            print('op_freq serialized')


if __name__ == '__main__':
    a = EtherDataToFreqAndTrDisc()
    a.start()
