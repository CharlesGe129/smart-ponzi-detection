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



PATH = '../dataset/'
DB = PATH + 'sm_database/{}.json'


class EthCrawlerNormalTx:
    def __init__(self, addresses, saved_file):
        self.name = "crawler_nml"
        self.addresses = addresses
        self.addr_len = len(addresses)
        self.saved_file = saved_file
        self.url_nml_pattern = 'http://api.etherscan.io/api?module=account&action=txlist&address={0}&startblock=0&endblock=99999999&sort=asc&apikey=APIbirthday'
        self.count = 0

    def start(self):
        with open(saved_file, 'w') as nml:
            nml.close()
        [self.crawl(addr) for addr in self.addresses]

    def crawl(self, addr):
        self.count += 1
        print(addr + ', progress: ' + str(round(self.count/self.addr_len*100, 2)) + '%')
        url = self.url_nml_pattern.format(addr)
        response = requests.get(url)
        with open(saved_file, 'a') as f:
            f.write(addr + '\n')
            f.write(response.text[38:-1] + '\n')


class EthCrawlerInternalTx:
    def __init__(self, addresses, saved_file):
        self.name = "crawler_nml"
        self.addresses = addresses
        self.addr_len = len(addresses)
        self.saved_file = saved_file
        self.url_nml_pattern = 'http://api.etherscan.io/api?module=account&action=txlistinternal&address={0}&startblock=0&endblock=9999999&sort=asc&apikey=APIbirthday'
        self.count = 0

    def start(self):
        with open(saved_file, 'w') as int:
            int.close()
        [self.crawl(addr) for addr in self.addresses]

    def crawl(self, addr):
        self.count += 1
        print(addr + ', progress: ' + str(round(self.count/self.addr_len*100, 2)) + '%')
        url = self.url_nml_pattern.format(addr)
        response = requests.get(url)
        with open(saved_file, 'a') as f:
            f.write(addr + "\n")
            f.write(response.text[38:-1] + '\n' if response.text[25:27] == 'OK' else '[]\n')


if __name__ == '__main__':
    files = ['ponzi_collection.csv', 'non_ponzi_collection.csv']
    for pz_file in files:
        with open(PATH + pz_file, 'rt') as f:
            csv_data = list(csv.reader(f))
        addr_index = 2 if pz_file.startswith('ponzi') else 0
        addresses = [line[addr_index].split(',')[0].split(' ')[0] for line in csv_data[1:]]
        saved_file = DB.format('normal' if pz_file.startswith('ponzi') else 'normal_np')
        EthCrawlerNormalTx(addresses, saved_file).start()
        saved_file = DB.format('internal' if pz_file.startswith('ponzi') else 'internal_np')
        EthCrawlerInternalTx(addresses, saved_file).start()
