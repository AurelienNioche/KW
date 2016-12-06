from multiprocessing import Pool, cpu_count, Value
import numpy as np
from main2 import launch, ModelA, ModelB
from analysis import represent_results
from save import save, get_id_list
from time import time
from datetime import datetime, timedelta
from os import mkdir, path

n = 1000
k = Value('i', 0)
db_path = "../KW.db"
fig_folder = "../fig"
departure = time()


def now():

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run(i):

    parameters = {
        "t_max": 500,
        "alpha": np.random.uniform(0.01, 1),
        "temp": np.random.uniform(0.01, 0.5),
        "role_repartition": np.array([500, 500, 500]),
        "storing_costs": np.array(
            [
                sorted(np.random.random(3) / 2),
                sorted(np.random.random(3) / 2),
                sorted(np.random.random(3) / 2)
            ]
        ),
        "model": ModelB()
    }

    backup = \
        launch(parallel=True, **parameters)

    save(parameters=parameters, backup=backup, idx=i, db_path=db_path)

    represent_results(backup=backup, parameters=parameters, display=False,
                      fig_name="{}/fig_{}.pdf".format(fig_folder, i))

    elapsed_time_sec = time() - departure

    with k.get_lock():

        k.value += 1

        elapsed_time = str(timedelta(seconds=elapsed_time_sec)).split(".")[0]
        remaining_time_sec = (elapsed_time_sec / k.value) * (n - k.value)
        remaining_time = str(timedelta(seconds=remaining_time_sec)).split(".")[0]

        print("{:05.02f} % [elapsed time: {}, estimated remaining time: {}]".format(
            (k.value / n) * 100, elapsed_time, remaining_time))


def main():

    if not path.exists(fig_folder):

        mkdir(fig_folder)

    id_list = get_id_list(db_path=db_path)
    if id_list:
        last_id = max(id_list)
    else:
        last_id = -1

    pool = Pool(processes=cpu_count())
    pool.map(func=run, iterable=np.arange(n) + last_id + 1)


if __name__ == "__main__":

    main()
