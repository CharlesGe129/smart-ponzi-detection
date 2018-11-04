import time
import json
import os
import src.tools as tl


def open_data(opcodes):
    t0 = time.clock()

    print("tools.opend_data: define variables...")

    path = '../dataset/'

    database_nml = path + 'normal.json'
    database_int = path + 'internal.json'
    database_op = path + 'ponzi_opcode/'

    database_nml_np = path + 'normal_np.json'
    database_int_np = path + 'internal_np.json'
    database_op_np = path + 'non_ponzi_opcode/'

    t1 = tl.compute_time(t0)

    # Open databases to access info

    print("tools.open_data: open databases...")
    # ponzi instances
    # with open(database_nml, 'r') as f:
    #     raw_nml = f.readlines()
    #
    # with open(database_int, 'r') as f:
    #     raw_int = f.readlines()

    op = [[f[:-5] for f in os.listdir(database_op) if f[-5:] == '.json'],
          [f[:-5] for f in os.listdir(database_op_np) if f[-5:] == '.json']]

    op_freq = [[], []]
    aaa = 0
    for i in range(2):
        db_path = database_op if i == 0 else database_op_np
        for add in op[i]:
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

    t2 = tl.compute_time(t1)

    with open(path + 'op_freq.json', 'w') as outfile:
        outfile.write(json.dumps(op_freq))
        print('op_freq serialized')

        # tr_dico is a list of which the size is the number of SM, each element is a list of which the size
        # is the number of transactions, each element is a dictionnary containing data about a specific transacton.
    # print("tools.open_data: create dictionnaries...")
    # # ponzi instances
    # addr = [raw_nml[2 * i][:-1] for i in range(len(raw_nml) // 2)]
    # addr_int = [raw_int[2 * i][:-1] for i in range(len(raw_int) // 2)]
    #
    # addr_np = [raw_nml_np[2 * i][:-1] for i in range(len(raw_nml_np) // 2)]
    # addr_int_np = [raw_int_np[2 * i][:-1] for i in range(len(raw_int_np) // 2)]
    #
    # N = len(op[0])
    # N_np = len(op[1])
    #
    # tr_dico = [
    #     # ponzi
    #     [[ast.literal_eval(raw_nml[2 * addr.index(op[0][i]) + 1][:-1]),
    #       ast.literal_eval(raw_int[2 * addr_int.index(op[0][i]) + 1][:-1])] for i in range(N)],
    #     # non ponzi
    #     [[ast.literal_eval(raw_nml_np[2 * addr_np.index(op[1][i]) + 1][:-1]),
    #       ast.literal_eval(raw_int_np[2 * addr_int_np.index(op[1][i]) + 1][:-1])] for i in range(N_np)]
    # ]
    #
    # tl.compute_time(t2)
    # temp = int(N_np / 3)
    #
    # # saved in three different files, because os.write and os.read doesn't support file with size superior to 2GB, ours is 4.2Gb.
    #
    # with open(path + 'tr_dico_nonponzi1.json', 'w') as f:
    #     f.write(json.dumps(tr_dico[1][:temp]))
    #
    # print('serialized half tr_dico')
    #
    # with open(path + 'tr_dico_nonponzi2.json', 'w') as f:
    #     f.write(json.dumps(tr_dico[1][temp:2 * temp]))
    #
    # with open(path + 'tr_dico_nonponzi3.json', 'w') as f:
    #     f.write(json.dumps(tr_dico[1][2 * temp:]))
    # print('everything has been serialized')
    #
    # return tr_dico


opcodes = ['SWAP8','DUP11','DUP14','SWAP10','DUP15','LOG2','INVALID','SWAP9','SWAP5','SWAP12','SWAP16',
           'DUP9','LOG1','DUP12','SWAP11','SWAP2','MSTORE8','SWAP14','DUP13','POP','DUP1','DUP8','DUP7',
           'DUP3','DUP4','MSTORE','SWAP3','CODECOPY','JUMP','DUP5','SWAP13','STOP','CALLDATACOPY','SWAP7',
           'SWAP1','SWAP6','RETURN','DUP6','SWAP4','REVERT','DUP2','SELFDESTRUCT','DUP10','DUP16','JUMPI',
           'SSTORE','PUSH','LOG3','LOG4','Missing','SWAP15']
open_data(opcodes)
