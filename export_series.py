import csv
import numpy as np
import os

class Exporter:
    def __init__(self, unit_ts_length=300, stride=10, padding=10, size_train=0.4, dir_path="./exported-datasets/"):
        self.unit_ts_length = unit_ts_length
        self.stride = stride
        self.padding = padding
        self.size_train = size_train
        self.dir_path = dir_path

    def check_columns_number(self, iterable_ts_dataframe_list):
        for ts_dataframe_list in iterable_ts_dataframe_list:
            assert len(ts_dataframe_list[0].columns) == 1, "export functions work only for one column !"

    def check_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def export_ts(self, healthy_ts, unhealthy_ts, fname=None):
        self.check_columns_number([healthy_ts, unhealthy_ts])
        if fname is None:
            fname = healthy_ts[0].columns[0]
        self.check_directory(self.dir_path + fname)
        with open(r'' + self.dir_path + fname + '/' + fname + '_TRAIN', "w") as train_f, \
                open(r'' + self.dir_path + fname + '/' + fname + '_TEST', "w") as test_f:
            train_writer = csv.writer(train_f)
            test_writer = csv.writer(test_f)
            for ts in healthy_ts:
                for i in range(self.padding, len(ts) - self.unit_ts_length - self.padding, self.stride):
                    series = ts.ix[i:i + self.unit_ts_length].values.ravel()
                    if (len(series) == self.unit_ts_length):
                        if (np.random.binomial(1, self.size_train)):
                            train_writer.writerow([0] + list(series))
                        else:
                            test_writer.writerow([0] + list(series))
            for ts in unhealthy_ts:
                for i in range(self.padding, len(ts) - self.unit_ts_length - self.padding, self.stride):
                    series = ts.ix[i:i + self.unit_ts_length].values.ravel()
                    if (len(series) == self.unit_ts_length):
                        if (np.random.binomial(1, self.size_train)):
                            train_writer.writerow([1] + list(series))
                        else:
                            test_writer.writerow([1] + list(series))

    def simple_export_ts(self, healthy_ts, unhealthy_ts, fname=None, normalized=False):
        self.check_columns_number([healthy_ts, unhealthy_ts])
        healthy = np.concatenate(
            [np.round(ts.ix[:self.unit_ts_length].values, 2) for ts in healthy_ts if len(ts) > self.unit_ts_length],
            axis=1).T
        if(normalized):
            healthy = (healthy - np.mean(healthy, axis=1).reshape(-1, 1)) / (np.std(healthy, axis=1).reshape(-1, 1))
        healthy = np.insert(healthy, 0, np.ones(len(healthy)), axis=1)

        unhealthy = np.concatenate(
            [np.round(ts.ix[:self.unit_ts_length].values, 2) for ts in unhealthy_ts if len(ts) > self.unit_ts_length],
            axis=1).T
        if (normalized):
            unhealthy = (unhealthy - np.mean(unhealthy, axis=1).reshape(-1, 1)) / (np.std(unhealthy, axis=1).reshape(-1, 1))
        unhealthy = np.insert(unhealthy, 0, np.zeros(len(unhealthy)), axis=1)

        test_train = np.concatenate((healthy, unhealthy), axis=0)
        np.random.shuffle(test_train)
        cut = int(self.size_train * len(test_train))

        if fname is None:
            fname = healthy_ts[0].columns[0]
        self.check_directory(self.dir_path + fname)
        np.savetxt(self.dir_path + fname + '/' + fname + '_TRAIN', test_train[:cut], delimiter=",", fmt='%3.2f')
        np.savetxt(self.dir_path + fname + '/' + fname + '_TEST', test_train[cut:], delimiter=",", fmt='%3.2f')
