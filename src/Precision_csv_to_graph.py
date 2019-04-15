import matplotlib.pyplot as plt

PATH = '../dataset/models/daily_precision.csv'
SAVE_PATH = '../report_per_day/'


def start():
    data = read_csv()
    graph([float(each.split(',')[1].strip('%')) for each in data],
          "Number of days after a contract is created", "J48 precisions of 10-fold cross-validation")
    graph([float(each.split(',')[2].strip('%')) for each in data],
          "Number of days after a contract is created", "J48 recall numbers of 10-fold cross-validation")
    graph([float(each.split(',')[3].strip('%')) for each in data],
          "Number of days after a contract is created", "RandomForest precisions of 10-fold cross-validation")
    graph([float(each.split(',')[4].strip('%')) for each in data],
          "Number of days after a contract is created", "RandomForest recall numbers of 10-fold cross-validation")
    # j48_precisions = [each.split(",")[1] for each in data][1:]
    # print(j48_precisions)


def read_csv():
    data = []
    with open(PATH) as f:
        while True:
            line = f.readline()
            if not line:
                break
            data.append(line.strip('\n'))
    return data[1:]


def graph(data, xlabel, ylabel):
    plt.figure()
    plt.plot([i for i in range(1, len(data) + 1)], data)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


if __name__ == '__main__':
    start()
