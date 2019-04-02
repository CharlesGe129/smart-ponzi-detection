#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 --------------------------------------------------------------------------------
 SPADE - Support for Provenance Auditing in Distributed Environments.
 Copyright (C) 2015 SRI International
 This program is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
 --------------------------------------------------------------------------------

"""


import numpy as np
import pandas as pd
import src.tools as tl
import os
from arff2pandas import a2p
from scipy import stats
import json
import time
# from sklearn import preprocessing
# import matplotlib.pyplot as plt
from src.open_data import OPCODES


class Feature:
    def __init__(self):
        self.cur_time = time.clock()
        self.paths = dict()
        self.op = list()
        self.opcodes = list()
        self.J = 100000
        self.tr_dico = list()
        self.size_info = list()
        self.op_freq = dict()
        self.ft_names = list()
        self.ft = list()
        self.ft_opcodes = list()
        self.ft_basic = list()
        self.df = None
        self.df_opcodes = None
        self.df_basic = None
        self.revert = dict()

    def start(self):
        self.define_path()
        self.load_if_revert()
        self.load_op()
        # self.load_tr_dico()
        self.load_txs_data()
        self.compute_feature()
        # self.df = self.create_pandas_dataframe(self.ft, self.ft_names + self.opcodes)
        # self.df_opcodes = self.create_pandas_dataframe(self.ft_opcodes, ['ponzi'] + self.opcodes)
        # self.df_basic = self.create_pandas_dataframe(self.ft_basic, self.ft_names)
        # self.dump_arff()

    def define_path(self):
        print("Feature: define variable and load data")
        self.paths['db'] = '../dataset/'

        self.paths['database_nml'] = self.paths['db'] + 'sm_database/normal/'
        self.paths['database_int'] = self.paths['db'] + 'sm_database/internal/'
        self.paths['database_op'] = self.paths['db'] + 'ponzi/op_count/'

        self.paths['database_nml_np'] = self.paths['db'] + 'sm_database/normal_np/'
        self.paths['database_int_np'] = self.paths['db'] + 'sm_database/internal_np/'
        self.paths['database_op_np'] = self.paths['db'] + 'non_ponzi/op_count/'

        self.paths['opcode'] = self.paths['db'] + 'ponzi/opcode/'
        self.paths['opcode_np'] = self.paths['db'] + 'non_ponzi/opcode/'

        # # For original data Marion_files
        # self.paths['db'] = '../dataset/sm_database/'
        # self.paths['database_op'] = self.paths['db'] + 'opcode/opcodes_count/'
        # self.paths['database_op_np'] = self.paths['db'] + 'opcode_np/opcode_count/bytecode_np/'

        self.cur_time = tl.compute_time(self.cur_time)

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
        # op[p=0, np=1][index] = contract_address
        print("Loading op, opcodes, op_freq, size_info...")
        self.op = [
            sorted([fname.split('.csv')[0] for fname in os.listdir(self.paths['database_op']) if
                    fname.endswith('.csv') and not self.revert[fname.split('.csv')[0]]]),
            sorted([fname.split('.csv')[0] for fname in os.listdir(self.paths['database_op_np']) if
                    fname.endswith('.csv') and not self.revert[fname.split('.csv')[0]]])
        ]
        self.opcodes = OPCODES
        for i in self.op[0]:
            self.size_info.append(os.path.getsize(self.paths['db'] + 'ponzi/bcode/' + i + '.json'))
        for i in self.op[1]:
            self.size_info.append(os.path.getsize(self.paths['db'] + 'non_ponzi/bcode/' + i + '.json'))
        self.load_op_freq()
        # Do some statistics
        print(len(self.op_freq))
        print(len(self.op_freq[0]))
        print(len(self.op_freq[0][0]))
        print(len(OPCODES))
        for tr_index in range(2):
            print(f"avg of {'Ponzi' if tr_index == 0 else 'Non-Ponzi'}")
            nums = [[] for i in range(50)]
            for contract in self.op_freq[tr_index]:
                for i in range(50):
                    nums[i].append(float(contract[i]))
            for i in range(50):
                print(f"{OPCODES[i]}: {sum(nums[i]) / len(nums[i])}")
        # End doing some statistics
        self.cur_time = tl.compute_time(self.cur_time)

    def load_op_freq(self):
        # # old
        # with open(self.paths['db'] + 'op_freq_list.json', 'rb', ) as f:
        #     temp_op_freq = json.loads(f.read())
        with open(self.paths['db'] + 'op_freq.json', 'rb', ) as f:
            op_freq_dict = json.loads(f.read())
        self.op_freq = [[], []]
        for np_index in range(2):
            for addr in self.op[np_index]:
                self.op_freq[np_index].append(op_freq_dict[np_index][addr])

    def load_tr_dico(self):
        # tr_dico[p=0, np=1][# of Contracts][nml=0, int=1][list of TXs in nml.json] = {'blockNumber': xxx} = dict()
        tr_dico = [[], []]
        with open(self.paths['db'] + 'tr_dico_ponzi.json', 'rb') as f:
            tr_dico[0] = json.loads(f.read())

        with open(self.paths['db'] + 'tr_dico_nonponzi0.json', 'rb') as f:
            tr_dico[1] = json.loads(f.read())
            print("Reading tr_dico: " + str(len(tr_dico[1])))
        for i in range(1, len(self.op[1])//500 + 1):
            with open(self.paths['db'] + 'tr_dico_nonponzi' + str(i) + '.json', 'rb') as f:
                tr_dico[1] += json.loads(f.read())
                print("Reading tr_dico: " + str(len(tr_dico[1])))
        self.tr_dico = tr_dico
        self.cur_time = tl.compute_time(self.cur_time)

    def load_txs_data(self):
        self.tr_dico = [[[[], []] for i in range(len(self.op[0]))], [[[], []] for i in range(len(self.op[1]))]]
        # tr_dico[p=0, np=1][# of Contracts][nml=0, int=1][list of TXs in nml.json] = {'blockNumber': xxx} = dict()
        self.load_txs_data_one_directory(self.paths['database_nml'], 0, 0)
        self.load_txs_data_one_directory(self.paths['database_int'], 0, 1)
        self.load_txs_data_one_directory(self.paths['database_nml_np'], 1, 0)
        self.load_txs_data_one_directory(self.paths['database_int_np'], 1, 1)

    def load_txs_data_one_directory(self, path, np_index, nml_index):
        # self.op[p=0, np=1][index] = contract_address
        for i in range(len(self.op[np_index])):
            contract_addr = self.op[np_index][i]
            print(f"contract_addr={contract_addr}")
            data = []
            if not self.revert[contract_addr]:
                try:
                    file_index = 0
                    while True:
                        print(f"Try load {contract_addr}_{file_index}.json")
                        with open(f"{path}{contract_addr}_{file_index}.json") as f:
                            data += json.loads(f.read())
                        file_index += 1
                except FileNotFoundError as e:
                    pass
            self.tr_dico[np_index][i][nml_index] = data
            print(f"data_len={len(data)}, tr_dico[{np_index}][{i}][{nml_index}] = data")

    def compute_feature(self):
        print("computing features for ponzi...")
        self.ft_names = [# 'addr',
                         'ponzi', 'nbr_tx_in', 'nbr_tx_out', 'Tot_in', 'Tot_out',
                         'num_paid_in_addr', 'num_paid_out_addr', 'overlap_in_out_addr',
                         'mean_in', 'mean_out', 'sdev_in', 'sdev_out', 'gini_in', 'gini_out', 'avg_time_btw_tx',
                         'gini_time_out', 'lifetime']
        # ideas: lifetime,number of active days, max/min/avg delay between in and out, max/min balance
        self.cal_advanced_features()

    def cal_advanced_features(self):
        ft = []
        ft_opcodes = []
        ft_basic = []
        len_op = [len(self.op[0]), len(self.op[1])]
        nbrs = [[], []]
        lifes = [[], []]
        for tr_index in range(2):
            print('computing features for ' + ('ponzi' if tr_index == 0 else 'non ponzi'))
            for i in range(len_op[tr_index]):
                # for each contract
                val_in = []
                val_out = []
                time_in = []
                time_out = []
                pay_in = 0
                pay_out = 0
                addr_in = set()
                addr_out = set()
                birth = float(self.tr_dico[tr_index][i][0][0]['timeStamp'])
                for tx in self.tr_dico[tr_index][i][0] + self.tr_dico[tr_index][i][1]:
                    # for each tx of that contract
                    contract_hash = self.op[tr_index][i]
                    timestamp = float(tx['timeStamp'])
                    if (timestamp - birth) / (60 * 60 * 24) <= self.J:
                        self.cal_value_time_in_out({'tx': tx, 'contract_hash': contract_hash, 'val_in': val_in,
                                                    'val_out': val_out, 'time_in': time_in, 'time_out': time_out,
                                                    'timestamp': timestamp})
                    (pay_in, pay_out) = self.cal_addr_in_out({'tx': tx, 'contract_hash': contract_hash,
                                                              'pay_in': pay_in, 'pay_out': pay_out, 'addr_in': addr_in,
                                                              'addr_out': addr_out})
                num_overlap_addr = len(addr_in.intersection(addr_out))
                res = tl.basic_features({'ponzi': 'ponzi' if tr_index == 0 else 'non_ponzi',
                                         'val_in': np.asarray(val_in), 'val_out': np.asarray(val_out),
                                         'time_in': np.asarray(time_in), 'time_out': np.asarray(time_out),
                                         'pay_in': pay_in, 'pay_out': pay_out, 'num_overlap_addr': num_overlap_addr})
                # gini: 12 in 13 out 15 timeout
                # 1 nbr_tx_in, 16 lifetime
                # CALLDATACOPY, CODECOPY, SWAP3, SSTORE, DUP6, SWAP6, REVERT, SSTORE
                nbrs[tr_index].append(float(res[1]))
                lifes[tr_index].append(float(res[16]))
                # if lifetime in lifes[tr_index]:
                #     lifes[tr_index][lifetime] += 1
                # else:
                #     lifes[tr_index][lifetime] = 1

                ft.append(np.concatenate((res, np.asarray(self.op_freq[tr_index][i], dtype='float64'))))
                ft_opcodes.append(np.concatenate((np.asarray(['ponzi' if tr_index == 0 else 'non_ponzi']),
                                                  np.asarray(self.op_freq[tr_index][i], dtype='float64'))))
                ft_basic.append(res)
            self.cur_time = tl.compute_time(self.cur_time)
        self.ft = ft
        self.ft_opcodes = ft_opcodes
        self.ft_basic = ft_basic
        print("nbrs==========================")
        print(f"P={sum(nbrs[0]) / len(nbrs[0])}, NP={sum(nbrs[1]) / len(nbrs[1])}")
        print("lifes==========================")
        print(f"P={sum(lifes[0]) / len(lifes[0])}, NP={sum(lifes[1]) / len(lifes[1])}")

    @staticmethod
    def cal_value_time_in_out(args):
        if args['tx']['from'] in ['', args['contract_hash']]:
            args['val_out'].append(float(args['tx']['value']))
            args['time_out'].append(args['timestamp'])
        else:
            args['val_in'].append(float(args['tx']['value']))
            args['time_in'].append(args['timestamp'])

    @staticmethod
    def cal_addr_in_out(args):
        tx = args['tx']
        contract_hash = args['contract_hash']
        if tx['from'] in [contract_hash, '']:
            args['pay_out'] += 1
            args['addr_out'].add(tx['to'])
        if tx['to'] in [contract_hash, '']:
            args['pay_in'] += 1
            args['addr_in'].add(tx['from'])
        return args['pay_in'], args['pay_out']

    def create_pandas_dataframe(self, ft, ft_names):
        print("Creating pandas dataframe...")
        columns = [s + '@NUMERIC' for s in ft_names]
        columns[0] = "ponzi@{ponzi,non_ponzi}"
        df = pd.DataFrame(data=ft, columns=columns)
        df['size_info@NUMERIC'] = self.size_info
        # data.loc[:, data.columns != columns[0]] = data.loc[:, data.columns != columns[0]].astype(np.float64)
        self.cur_time = tl.compute_time(self.cur_time)
        return df

    # deprecated
    def get_rid_of_outliers(self, columns):
        print("Getting rid of outliers for the non ponzi instances")
        out_index = 3
        """
        min_max_scaler = preprocessing.StandardScaler()
        dum = df.drop(df[df[columns[0]] == 'ponzi'].index)
        df_out = dum[(np.abs(stats.zscore(min_max_scaler.transform(dum.drop(labels=[columns[0]]+columns[n:],axis=1)))) < out_index).all(axis=1)]
        df_out = df_out.append(df.drop(df[df[columns[0]] == 'non_ponzi'].index))

        """
        dum = self.df.drop(self.df[self.df[columns[0]] == 'ponzi'].index)
        df_out = dum[(
            np.abs(stats.zscore(
                np.asarray(dum.drop(labels=[columns[0]] + columns[len(self.ft_names):], axis=1), dtype='float64'))) < out_index).all(
            axis=1)]
        self.df_out = df_out.append(self.df.drop(self.df[self.df[columns[0]] == 'non_ponzi'].index))
        self.cur_time = tl.compute_time(self.cur_time)

    def dump_arff(self):
        print("Dumping into arff files ...")
        with open(self.paths['db'] + 'models/PONZI_' + str(self.J) + '.arff', 'w') as f:
            a2p.dump(self.df, f)
        with open(self.paths['db'] + 'models/PONZI_opcodes_' + str(self.J) + '.arff', 'w') as f:
            a2p.dump(self.df_opcodes, f)
        with open(self.paths['db'] + 'models/PONZI_basic_' + str(self.J) + '.arff', 'w') as f:
            a2p.dump(self.df_basic, f)
        self.cur_time = tl.compute_time(self.cur_time)

    def remaining_code(self):
        pass
        '''
        plt.hist(df['avg_time_btw_tx@NUMERIC'][145:].astype('float32')/(60*60), bins = 15)
        plt.hist(df['avg_time_btw_tx@NUMERIC'][:145].astype('float32')/(60*60), bins = 15)
    
        plt.xlabel('Delay between transactions (hours)')
        plt.ylabel('number of instances')
        plt.title('Delay between transacstions histogram for non ponzi')
        plt.savefig(path + 'delay_histo.png')
        '''

    def nml_int_file_format(self):
        """
        normal.json : {
        (0)'blockNumber': 'n',
        (1)'timeStamp': 'n'
        (2) 'hash': '0x..',
        (3) 'nonce': 'n',
        (4)'blockHash': '0x..e6',
        (5)'transactionIndex': '1',
        (6)'from': '0x..',
        (7)'to': '0x..',
        (8)'value': 'n',
        (9)'gas': 'n',
        (10)'gasPrice': 'n',
        (11)'isError': '0',
        (12)'txreceipt_status': '',
        (13)'input': '0x..',
        (14)'contractAddress': '0x..',
        (15)'cumulativeGasUsed': 'n',
        (16)'gasUsed': 'n,
        (17)'confirmations': 'n'}

        internal.json :{
        (0)'blockNumber',
        (1)'timeStamp',
        (2)'hash',
        (3)'from',
        (4)'to',
        (5)'value',
        (6)'contractAddress',
        (7)'input',
        (8)'type',
        (9)'gas',
        (10)'gasUsed',
        (11)'traceId',
        (12)'isError',
        (13)'errCode'}

        value = 10**18 ETH value
        """


if __name__ == '__main__':
    Feature().start()
