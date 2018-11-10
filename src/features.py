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
from sklearn import preprocessing
import matplotlib.pyplot as plt
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
        self.df = None
        self.df_out = None

    def start(self):
        self.define_path()
        self.load_op()
        self.load_tr_dico()
        self.compute_feature()
        self.create_pandas_dataframe()
        self.dump_arff()

    def define_path(self):
        print("Feature: define variable and load data")
        self.paths['db'] = '../Marion_files/sm_database/'

        self.paths['database_nml'] = self.paths['db'] + 'normal.json'
        self.paths['database_int'] = self.paths['db'] + 'internal.json'
        # Same as opcode/raw_opcodes/ in origin feature.py
        self.paths['database_op'] = self.paths['db'] + 'opcode/opcodes_count/'

        self.paths['database_nml_np'] = self.paths['db'] + 'normal_np.json'
        self.paths['database_int_np'] = self.paths['db'] + 'internal_np.json'
        self.paths['database_op_np'] = self.paths['db'] + 'opcode_np/opcode_count/bytecode_np/'

        self.cur_time = tl.compute_time(self.cur_time)
        pass

    def load_op(self):
        # op[p=0, np=1][index] = contract_address
        print("Loading op, opcodes, op_freq, size_info...")
        self.op = [
            [fname.split('.json')[0] for fname in os.listdir(self.paths['database_op']) if fname.endswith('.json')],
            [fname.split('.json')[0] for fname in os.listdir(self.paths['database_op_np']) if fname.endswith('.json')]
        ]
        self.opcodes = OPCODES
        for i in self.op[0]:
            self.size_info.append(os.path.getsize(self.paths['db'] + 'bytecode/' + i + '.json'))
        for i in self.op[1]:
            self.size_info.append(os.path.getsize(self.paths['db'] + 'bytecode_np/' + i + '.json'))
        with open(self.paths['db'] + 'op_freq.json', 'rb', ) as f:
            self.op_freq = json.loads(f.read())
        self.cur_time = tl.compute_time(self.cur_time)

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

    def compute_feature(self):
        print("computing features for ponzi...")
        self.ft_names = [# 'addr',
                         'ponzi', 'nbr_tx_in', 'nbr_tx_out', 'Tot_in', 'Tot_out', 'mean_in', 'mean_out', 'sdev_in',
                         'sdev_out', 'gini_in', 'gini_out', 'avg_time_btw_tx', 'gini_time_out', 'lifetime']
        # ideas: lifetime,number of active days, max/min/avg delay between in and out, max/min balance
        self.cal_advanced_features()

    def cal_advanced_features(self):
        ft = []
        len_op = [len(self.op[0]), len(self.op[1])]
        for tr_index in range(2):
            print('computing features for ' + ('ponzi' if tr_index == 0 else 'non ponzi'))
            for i in range(len_op[tr_index]):
                val_in = []
                val_out = []
                time_in = []
                time_out = []
                birth = float(self.tr_dico[tr_index][i][0][0]['timeStamp'])
                for tx in self.tr_dico[tr_index][i][0] + self.tr_dico[tr_index][i][1]:
                    contract_hash = self.op[tr_index][i]
                    timestamp = float(tx['timeStamp'])
                    if (timestamp - birth) / (60 * 60 * 24) <= self.J:
                        self.cal_value_time_in_out({'tx': tx, 'contract_hash': contract_hash, 'val_in': val_in,
                                                    'val_out': val_out, 'time_in': time_in, 'time_out': time_out,
                                                    'timestamp': timestamp})
                res = tl.basic_features('ponzi' if tr_index == 0 else 'non_ponzi',
                                        np.asarray(val_in), np.asarray(val_out),
                                        np.asarray(time_in), np.asarray(time_out))
                ft.append(np.concatenate((res, np.asarray(self.op_freq[tr_index][i], dtype='float64'))))
            self.cur_time = tl.compute_time(self.cur_time)
        self.ft = ft

    @staticmethod
    def cal_value_time_in_out(args):
        if args['tx']['from'] in ['', args['contract_hash']]:
            args['val_out'].append(float(args['tx']['value']))
            args['time_out'].append(args['timestamp'])
        else:
            args['val_in'].append(float(args['tx']['value']))
            args['time_in'].append(args['timestamp'])

    def create_pandas_dataframe(self):
        print("Creating pandas dataframe...")
        columns = [s + '@NUMERIC' for s in self.ft_names + self.opcodes]
        columns[0] = "ponzi@{ponzi,non_ponzi}"
        df = pd.DataFrame(data=self.ft, columns=columns)
        df['size_info@NUMERIC'] = self.size_info
        # data.loc[:, data.columns != columns[0]] = data.loc[:, data.columns != columns[0]].astype(np.float64)
        self.cur_time = tl.compute_time(self.cur_time)
        self.df = df
        self.get_rid_of_outliers(columns)

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
        with open(self.paths['db'] + 'models/PONZI_out_' + str(self.J) + '.arff', 'w') as f:
            a2p.dump(self.df_out, f)
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
