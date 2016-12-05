from multiprocessing import Pool, cpu_count, Value
import numpy as np
from main2 import launch, ModelA, ModelB
from analysis import represent_results
from save import save
from time import time
from datetime import datetime, timedelta
import ctypes
from os import mkdir, path

n = Value('i', 0)
k = Value('i', 0)
db_path = Value(ctypes.c_char_p, b"")
fig_folder = Value(ctypes.c_char_p, b"")


def now():

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run(i):

    with k.get_lock():
        old_k = k.value
        k.value += 1

    print("[{}]: Running {}/{} run...".format(now(), old_k + 1, n.value))
    print()

    a = time()

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
        "model": ModelA()
    }

    backup = \
        launch(parallel=True, **parameters)

    save(parameters=parameters, backup=backup, idx=i, db_path=db_path.value.decode())

    represent_results(backup=backup, parameters=parameters, display=False,
                      fig_name="{}/fig_{}.pdf".format(fig_folder.value.decode(), i))

    b = time()

    print("[{}] Finishing {}/{} run [{}].".format(now(), old_k + 1, n.value, timedelta(seconds=b-a)))
    print()


def main():

    a = time()

    n.value = 100

    db_path.value = "{}".format("../KW.db").encode()

    fig_folder.value = "{}".format("../fig").encode()

    if not path.exists(fig_folder.value.decode()):

        mkdir(fig_folder.value.decode())

    assert not path.exists(db_path.value.decode()), "Db already exists!"

    pool = Pool(processes=cpu_count())
    pool.map(func=run, iterable=range(n.value))

    b = time()

    print("TOTAL RUNNING TIME: {}", timedelta(seconds=b-a))


if __name__ == "__main__":

    main()
