import os

PONZI_PATH = "/Users/charlesge/charles/university/Master_project/smart-ponzi-detection/dataset/ponzi/opcode/"
NON_PONZI_PATH = "/Users/charlesge/charles/university/Master_project/smart-ponzi-detection/dataset/non_ponzi/opcode/"


def start():
    i = 0
    for filename in os.listdir(NON_PONZI_PATH):
        if not filename.endswith(".json"):
            continue
        with open(NON_PONZI_PATH + filename) as f:
            if "REVERT" in f.read():
                print(filename)
                i += 1
                print(i)


if __name__ == '__main__':
    start()
