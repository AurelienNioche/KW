from sqlite3 import connect
from os import path
import numpy as np
from main2 import ModelB


class Database(object):

    def __init__(self, db_path):

        self.db_path = db_path

    def save(self, idx, parameters, backup):

        # print("Database: Saving idx {}.".format(idx))
        connection = connect(database=self.db_path)
        cursor = connection.cursor()

        q = "CREATE TABLE 'parameters_{}' (" \
            "ID INTEGER PRIMARY KEY, " \
            "t_max INTEGER, " \
            "temp REAL, " \
            "alpha REAL, " \
            "model TEXT, " \
            "x1 INTEGER, " \
            "x2 INTEGER, " \
            "x3 INTEGER, " \
            "c11 INTEGER, " \
            "c12 INTEGER, " \
            "c13 INTEGER, " \
            "c21 INTEGER, " \
            "c22 INTEGER, " \
            "c23 INTEGER, " \
            "c31 INTEGER, " \
            "c32 INTEGER, " \
            "c33 INTEGER " \
            ")".format(idx)

        cursor.execute(q)

        q = "CREATE TABLE 'backup_{}' (" \
            "ID INTEGER PRIMARY KEY, " \
            "exchange12 REAL," \
            "exchange13 REAL," \
            "exchange23 REAL," \
            "acceptance1 REAL," \
            "acceptance2 REAL," \
            "acceptance3 REAL, " \
            "utility REAL, " \
            "n_exchanges INTEGER" \
            ")".format(idx)

        cursor.execute(q)

        # -------- FILL TABLES ---------- #

        # ---- Parameters table --------- #

        q = "INSERT INTO 'parameters_{}' VALUES (".format(idx) + "?, " * 16 + "?)"

        cursor.execute(q,
                       [
                           1,
                           parameters["t_max"],
                           parameters["temp"],
                           parameters["alpha"],
                           str(parameters["model"]),
                           int(parameters["role_repartition"][0]),
                           int(parameters["role_repartition"][1]),
                           int(parameters["role_repartition"][2]),
                           parameters["storing_costs"][0, 0],
                           parameters["storing_costs"][0, 1],
                           parameters["storing_costs"][0, 2],
                           parameters["storing_costs"][1, 0],
                           parameters["storing_costs"][1, 1],
                           parameters["storing_costs"][1, 2],
                           parameters["storing_costs"][2, 0],
                           parameters["storing_costs"][2, 1],
                           parameters["storing_costs"][2, 2],
                       ])

        # ------- Backup table ------ #

        exchanges = backup["exchanges"]
        third_good_acceptance = backup["third_good_acceptance"]
        utility = backup["utility"].reshape(parameters["t_max"], 1)
        n_exchanges = backup["n_exchanges"].reshape(parameters["t_max"], 1)
        id_column = np.arange(parameters["t_max"]).reshape(parameters["t_max"], 1)

        q = "INSERT INTO 'backup_{}' VALUES (".format(idx) + "?, " * 8 + "?)"
        cursor.executemany(
            q,
            np.hstack((
                id_column,
                exchanges,
                third_good_acceptance,
                utility,
                n_exchanges
            ))
        )

        connection.commit()
        connection.close()
        # print("Database: Done for idx {}.".format(idx))

    def get_id_list(self):

        connection = connect(self.db_path)
        cursor = connection.cursor()
        q = "SELECT name FROM sqlite_master WHERE type='table'"
        cursor.execute(q)
        idx_list = np.unique([int(i[0].split('_')[1]) for i in cursor.fetchall()])
        return idx_list


def save(parameters, backup, db_path=path.expanduser("~/Desktop/KW.db"), idx=0):

    d = Database(db_path=db_path)
    d.save(idx=idx, parameters=parameters,
           backup=backup)


def get_id_list(db_path):

    d = Database(db_path=db_path)
    return d.get_id_list()


def test():

    parameters = {
        "t_max": 100,
        "alpha": 0.1,
        "temp": 0.01,
        "role_repartition": np.array([500, 500, 500], dtype=int),
        "storing_costs": np.array(
            [
                [0.48, 0.49, 0.5],
                [0.05, 0.06, 0.07],
                [0.15, 0.2, 0.5]
            ]
        ),
        "model": ModelB()
    }

    backup = {
        "exchanges": np.random.random((parameters["t_max"], 3)),
        "third_good_acceptance": np.random.random((parameters["t_max"], 3)),
        "utility": np.random.random(parameters["t_max"]),
        "n_exchanges": np.random.randint(500, size=parameters["t_max"])
    }

    d = Database(db_path=path.expanduser("~/Desktop/KW.pdf"))
    d.save(idx=0, parameters=parameters,
           backup=backup)


if __name__ == "__main__":

    test()
