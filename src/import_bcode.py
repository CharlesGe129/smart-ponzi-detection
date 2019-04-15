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

from web3 import Web3
import csv
import os

#sm_file = 'Smart_Contract_Addresses.list'
sm_file = 'sm_add_nponzi.csv'
path = '../'
database_bcode = path + 'dataset/'

web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/TO1X2JTG8k9PiaYd0iQr'))


# with open(path + sm_file, 'rt') as f:
#     truc = csv.reader(f)
#     add = list(truc)
#
#
# addresses = [pk[:42] for pklist in add for pk in pklist]

for filename in ['ponzi_collection.csv']:
    with open(database_bcode + filename) as f:
        addresses = [line.split(',')[2] for line in f.readlines()][1:]

addresses = [each.split('.json')[0] for each in os.listdir(f"{database_bcode}/ponzi/bcode/") if each.endswith('.json')]
print(addresses)
print(len(addresses))
addresses = sorted(addresses)

except_addr = [each.split('.json')[0] for each in os.listdir(f"{database_bcode}/ponzi/opcode/") if each.endswith('.json')]
print(len(except_addr))

evmdis_path = '/Users/charlesge/go/bin/'
for ad in addresses:
    if ad in except_addr:
        continue
    # print(ad)
    try:
        print(f'cat {database_bcode}/ponzi/bcode/{ad}.json | {evmdis_path}/evmdis > {database_bcode}/ponzi/opcode/{ad}.json')
        # os.system(f'cat {database_bcode}/ponzi/bcode/{ad}.json | {evmdis_path}/evmdis > {database_bcode}/ponzi/opcode/{ad}.json')
    except:
        pass

print("done")
input()

i = 0
for ad in addresses:
    try:
        code = repr(web3.eth.getCode(web3.toChecksumAddress(ad)))[12:-2]
        if code:
            i += 1
            # print(str(i) + ": " + ad)
            with open(database_bcode + 'ponzi/bcode/' + ad + '.json', 'w') as f:
                f.write(code)
        else:
            print(ad)
        #Disasemble
        print(ad)
        #os.system('cat /Users/e31989/Documents/sm_database/bytecode/' + ad +'.json | evmdis > /Users/e31989/Documents/features/' + ad + '.json' )
    except Exception as e:
        print(e)
    
#for /r %i in (*.json); do cat "%i" | evmdis > "/Users/e31989/Documents/features/$~ni.json"; done
#for %i in (*.json); do cat "%i" | evmdis > "/Users/e31989/Documents/features/$~ni.json"; done