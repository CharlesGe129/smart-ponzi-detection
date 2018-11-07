import ast
import time
import json
import os
import src.tools as tl


class EtherDataToFreqAndTrDisc:
    def __init__(self):
        self.cur_time = 0
        self.paths = dict()
        self.op = list()

    def define_path(self):
        self.cur_time = time.clock()
        print("EtherDataToFreqAndTrDisc: define variables...")
        self.paths['db'] = '../Marion_files/sm_database/'

        self.paths['database_nml'] = self.paths['db'] + 'normal.json'
        self.paths['database_int'] = self.paths['db'] + 'internal.json'
        self.paths['database_op'] = self.paths['db'] + 'opcode/raw_opcodes/'

        self.paths['database_nml_np'] = self.paths['db'] + 'normal_np.json'
        self.paths['database_int_np'] = self.paths['db'] + 'internal_np.json'
        self.paths['database_op_np'] = self.paths['db'] + 'opcode_np/opcode_count/bytecode_np/'

        self.cur_time = tl.compute_time(self.cur_time)

    def load_op(self):
        self.op = [
            [fname.split('.json')[0] for fname in os.listdir(self.paths['database_op']) if fname.endswith('.json')],
            [fname.split('.json')[0] for fname in os.listdir(self.paths['database_op_np']) if fname.endswith('.json')]
        ]

    def gen_op_freq(self):
        print("EtherDataToFreqAndTrDisc: generating op_freq.json")
        opcodes = ['SWAP8', 'DUP11', 'DUP14', 'SWAP10', 'DUP15', 'LOG2', 'INVALID', 'SWAP9', 'SWAP5', 'SWAP12',
                   'SWAP16',
                   'DUP9', 'LOG1', 'DUP12', 'SWAP11', 'SWAP2', 'MSTORE8', 'SWAP14', 'DUP13', 'POP', 'DUP1', 'DUP8',
                   'DUP7',
                   'DUP3', 'DUP4', 'MSTORE', 'SWAP3', 'CODECOPY', 'JUMP', 'DUP5', 'SWAP13', 'STOP', 'CALLDATACOPY',
                   'SWAP7',
                   'SWAP1', 'SWAP6', 'RETURN', 'DUP6', 'SWAP4', 'REVERT', 'DUP2', 'SELFDESTRUCT', 'DUP10', 'DUP16',
                   'JUMPI',
                   'SSTORE', 'PUSH', 'LOG3', 'LOG4', 'Missing', 'SWAP15']
        op_freq = [[], []]
        aaa = 0
        for i in range(2):
            db_path = self.paths['database_op'] if i == 0 else self.paths['database_op_np']
            for add in self.op[i]:
                aaa += 1
                print(f'{aaa}, {add}')
                with open(db_path + add + '.json', 'r') as f:
                    raw = f.readlines()
                    res = [0 for i in range(len(opcodes))]
                    if len(raw) > 1:
                        tot = 0
                        for opcode in raw:
                            opcode = opcode.strip(' \n')
                            if opcode.startswith('#') or opcode.startswith(':label') or not opcode or 'Missing opcode' in opcode:
                                continue
                            tot += 1
                            code = opcode.split('\t')[1].split('(')[0] if '\t' in opcode else opcode.split(' ')[1].split('(')[0]
                            res[opcodes.index(code)] += 1
                    tot = max(1, tot)
                    res = [x / tot for x in res]
                    op_freq[i].append(res)

        print(f"{len(op_freq[0])}, {len(op_freq[1])}")
        self.cur_time = tl.compute_time(self.cur_time)

    def gen_tr_dico(self):
        # tr_dico is ordered by op[]
        # tr_dico[p=0, np=1][# of TXs][nml=0, int=1][list of TXs in nml.json] = {'blockNumber': xxx} = dict()
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
                print('serialized #' + str(i) + ' tr_dico from ')
        with open(self.paths['db'] + 'tr_dico_ponzi.json', 'w') as f:
            f.write(json.dumps(tr_dico[0]))

    def start(self):
        self.define_path()
        self.load_op()
        self.gen_op_freq()
        self.gen_tr_dico()


if __name__ == '__main__':
    a = EtherDataToFreqAndTrDisc()
    a.start()
