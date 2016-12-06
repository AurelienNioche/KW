import numpy as np
from sqlite3 import connect
from os import path, mkdir
from time import time
from datetime import timedelta
from multiprocessing import Pool, Value, cpu_count
from analysis import represent_results
from main2 import ModelA, ModelB


class DataGetter(object):

    def __init__(self, db_path):

        self.db_path = db_path
        self.connection = connect(self.db_path)
        self.cursor = self.connection.cursor()

    def get_parameters_and_backup(self, idx):

        # ----- PARAMETERS ----- #

        q = "SELECT t_max, alpha, temp, x1, x2, x3, c11, c12, c13, c21, c22, c23, c31, c32, c33, model " \
            "FROM parameters_{} WHERE ID=1".format(idx)
        self.cursor.execute(q)

        t_max, alpha, temp, x1, x2, x3, c11, c12, c13, c21, c22, c23, c31, c32, c33, model = \
            self.cursor.fetchone()

        model_dic = {"Model A": ModelA, "Model B": ModelB}

        parameters = {
            "t_max": t_max,
            "alpha": alpha,
            "temp": temp,
            "role_repartition": np.array([x1, x2, x3], dtype=int),
            "storing_costs": np.array(
                [
                    [c11, c12, c13],
                    [c21, c22, c23],
                    [c31, c32, c33]
                ]
            ),
            "model": model_dic[model]
        }

        # ----- BACKUP ----- #

        q = "SELECT exchange12, exchange13, exchange23, acceptance1, acceptance2, acceptance3, utility, n_exchanges " \
            "FROM backup_{}".format(idx)

        self.cursor.execute(q)

        content = np.asarray(self.cursor.fetchall())
        exchange = content[:, 0:3]
        acceptance = content[:, 3:6]
        utility = content[:, 6]
        n_exchanges = content[:, 7]

        backup = {
            "exchanges": exchange,
            "third_good_acceptance": acceptance,
            "utility": utility,
            "n_exchanges": n_exchanges
        }

        return parameters, backup

    def get_id_list(self):

        q = "SELECT name FROM sqlite_master WHERE type='table'"
        self.cursor.execute(q)
        idx_list = np.unique([int(i[0].split('_')[1]) for i in self.cursor.fetchall()])
        return idx_list

    def __del__(self):

        self.connection.close()


def run(i):

    parameters, backup = d.get_parameters_and_backup(idx=i)
    represent_results(backup=backup, parameters=parameters, display=False,
                      fig_name="{}/fig_{}.pdf".format(fig_folder, i))

    elapsed_time_sec = time() - departure

    with k.get_lock():

        k.value += 1

        elapsed_time = str(timedelta(seconds=elapsed_time_sec)).split(".")[0]
        remaining_time_sec = (elapsed_time_sec / k.value) * (n - k.value)
        remaining_time = str(timedelta(seconds=remaining_time_sec)).split(".")[0]

        print("{:05.02f} % [elapsed time: {}, estimated remaining time: {}]".format(
            (k.value/n) * 100, elapsed_time, remaining_time))


if __name__ == "__main__":

    db_path = "../KW.db"
    fig_folder = "../fig"

    if not path.exists(fig_folder):
        mkdir(fig_folder)

    d = DataGetter(db_path=db_path)
    id_list = d.get_id_list()

    departure = time()
    k = Value('i', 0)
    n = len(id_list)
    p = Pool(processes=cpu_count())

    p.map(run, id_list)

