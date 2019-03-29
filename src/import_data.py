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


"""

Run with file '../dataset/ponzi_collection.csv' and '../dataset/non_ponzi_collection.csv' containing the blockchain addresses of each smart contracts

Returns: json files containing all the transactions info of each smart contract

"""

import requests
import csv
import ast
import json
import os



PATH = '../dataset/'
DB = PATH + 'sm_database/{}/'
OPCODE_PATH = '/Users/charlesge/charles/university/Master_project/smart-ponzi-detection/dataset/non_ponzi/opcode/'


class EthCrawlerNormalTx:
    def __init__(self, addresses, saved_file, revert_dict):
        self.name = "crawler_nml"
        self.addresses = sorted(addresses)
        self.addr_len = len(addresses)
        self.saved_file = saved_file
        self.url_nml_pattern = 'http://api.etherscan.io/api?module=account&action=txlist&address={0}&startblock=0&endblock=99999999&sort=asc&apikey=APIbirthday&page={1}&offset=10000'
        self.count = 0
        self.revert_dict = revert_dict

    def start(self):
        # with open(self.saved_file, 'w') as nml:
        #     nml.close()
        addresses = self.addresses
        i = 0
        while addresses[i] != '0x2a0c0dbecc7e4d658f48e01e3fa353f44050c208':
            i += 1
        self.addresses = addresses[i:]
        [self.crawl(addr) for addr in self.addresses]

    def crawl(self, addr):
        self.count += 1
        page = 1
        txs = []
        if addr not in self.revert_dict:
            print(f"Error: addr={addr}")
        elif self.revert_dict[addr]:
            return
        while True:
            url = self.url_nml_pattern.format(addr, page)
            print(f"{addr}, page={page}, progress:{round(self.count / self.addr_len * 100, 2)}%, num_txs={len(txs)}")
            data_one_page = self.crawl_one_page(url)
            if not data_one_page:
                break
            else:
                txs += data_one_page
                page += 1
        print(f"len of txs: {len(txs)}")
        save_file(self.saved_file + addr, txs)

    @staticmethod
    def crawl_one_page(url):
        for i in range(3):
            try:
                response = requests.get(url, timeout=20)
                data = json.loads(response.text)
                if 'result' not in data:
                    print(f"error, no result {url}")
                    return []
                # {"status":"0","message":"No transactions found","result":[]}
                if len(data['result']) == 0:
                    return []
                else:
                    return data['result']
            except Exception as e:
                print("Error: ")
                print(e)


class EthCrawlerInternalTx:
    def __init__(self, addresses, saved_file, revert_dict):
        self.name = "crawler_nml"
        self.addresses = sorted(addresses)
        self.addr_len = len(addresses)
        self.saved_file = saved_file
        self.url_nml_pattern = 'http://api.etherscan.io/api?module=account&action=txlistinternal&address={0}&startblock=0&endblock=9999999&sort=asc&apikey=APIbirthday&page={1}&offset=10000'
        self.count = 0
        self.revert_dict = revert_dict

    def start(self):
        # with open(self.saved_file, 'w') as int:
        #     int.close()
        [self.crawl(addr) for addr in self.addresses]

    def crawl(self, addr):
        self.count += 1
        page = 1
        txs = []
        if addr not in self.revert_dict:
            print(f"Error: addr={addr}")
        elif self.revert_dict[addr]:
            return
        while True:
            url = self.url_nml_pattern.format(addr, page)
            print(f"{addr}, page={page}, progress:{round(self.count / self.addr_len * 100, 2)}%, num_txs={len(txs)}")
            data_one_page = self.crawl_one_page(url)
            if not data_one_page:
                break
            else:
                txs += data_one_page
                page += 1
        print(f"len of txs: {len(txs)}")
        save_file(self.saved_file + addr, txs)

    @staticmethod
    def crawl_one_page(url):
        for i in range(3):
            try:
                response = requests.get(url, timeout=20)
                a = requests.get(url, )
                data = json.loads(response.text)
                if 'result' not in data:
                    print(f"error, no result {url}")
                    return []
                # {"status":"0","message":"No transactions found","result":[]}
                if len(data['result']) == 0:
                    print("End")
                    return []
                else:
                    return data['result']
            except Exception as e:
                print("Error: ")
                print(e)


def save_file(path, data):
    # path = '/xxx/xxx/xxx/addr' without '.json'
    lens = int(len(data) / 1000000)
    for index in range(lens):
        file = f"{path}_{index}.json"
        with open(file, 'w') as f:
            start = index * 1000000
            end = start + 1000000
            f.write(json.dumps(data[start:end]))
    file = f"{path}_{lens}.json"
    with open(file, 'w') as f:
        f.write(json.dumps(data[lens*1000000:]))


if __name__ == '__main__':
    # Check if NP contracts have "REVERT" in OPCODE. Ignore contracts contain "REVERT" during downloads.
    revert = {}
    for filename in os.listdir(OPCODE_PATH):
        if not filename.endswith(".json"):
            continue
        with open(OPCODE_PATH + filename) as f:
            revert[filename.split(".json")[0]] = 'REVERT' in f.read()

    # crawling
    # files = ['ponzi_collection.csv', 'non_ponzi_collection.csv']
    # files = ['ponzi_collection.csv']
    files = ['non_ponzi_collection.csv']
    for pz_file in files:
        with open(PATH + pz_file, 'rt') as f:
            csv_data = list(csv.reader(f))
        addr_index = 2 if pz_file.startswith('ponzi') else 0
        addresses = [line[addr_index].split(',')[0].split(' ')[0] for line in csv_data[1:]]
        saved_file = DB.format('normal' if pz_file.startswith('ponzi') else 'normal_np')
        EthCrawlerNormalTx(addresses, saved_file, revert).start()
        saved_file = DB.format('internal' if pz_file.startswith('ponzi') else 'internal_np')
        EthCrawlerInternalTx(addresses, saved_file, revert).start()
