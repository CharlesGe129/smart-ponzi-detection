import os

DATASET_PATH = '/Users/charles/charles/university/Master Project/go-ethereum/analysis_tool_python/SmartPonziDetection/dataset/'
FOLDERS = ['ponzi_bcode/', 'non_ponzi_bcode/']


def start():
    [convert_all_file(folder) for folder in FOLDERS]


def convert_all_file(folder):
    i = 0
    for filename in os.listdir(DATASET_PATH + folder):
        if not filename.endswith('.json'):
            continue
        i += 1
        print(f"{i}: {filename}")
        bcode_to_opcode(DATASET_PATH + folder + filename)


def bcode_to_opcode(path):
    path = path.replace('Master Project', 'Master\ Project')
    print('cat ' + path + ' | /Users/charles/go/bin/evmdis > ' + path.replace('_bcode', '_opcode'))
    os.popen(
        'cat ' + path + ' | /Users/charles/go/bin/evmdis > ' + path.replace('_bcode', '_opcode'))


start()
