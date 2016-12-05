import numpy as np
from tqdm import tqdm
from module.useful_functions import softmax
from analysis import represent_results


class ModelA(object):

    roles = np.array([
        [1, 0, 2],
        [2, 1, 0],
        [0, 2, 1]
    ], dtype=int)

    def __str__(self):

        return "Model A"


class ModelB(object):

    roles = np.array([
        [2, 0, 1],
        [0, 1, 2],
        [1, 2, 0]
    ], dtype=int)

    def __str__(self):

        return "Model B"


class Agent(object):

    def __init__(self, alpha, temp, prod, cons, third, storing_costs, agent_type, model, idx):

        self.P = prod
        self.C = cons
        self.T = third

        self.model = model

        self.storing_costs = storing_costs

        self.in_hand = self.P

        self.agent_type = agent_type
        self.idx = idx

        # ------- STRATEGIES ------- #

        # Dimension 0: strategies,
        # Dimension 1: object in hand (i, k),
        # Dimension 2: proposed object (i, j, k),
        # We suppose that :
        # - An agent always accepts his consumption good
        # - An agent always refuse the exchange if the proposed object is the same that the one he has in hand
        # - Strategies therefore contrast by attitude of the agent towards the third good if he has his production
        #    good in hand, and the production good if he has his third good in hand
        self.strategies = np.array([
            [[0, 1, 0],
             [np.nan, np.nan, np.nan],
             [0, 1, 0]],
            [[0, 1, 1],
             [np.nan, np.nan, np.nan],
             [0, 1, 0]],
            [[0, 1, 0],
             [np.nan, np.nan, np.nan],
             [1, 1, 0]],
            [[0, 1, 1],
             [np.nan, np.nan, np.nan],
             [1, 1, 0]],
        ])
        self.strategies_values = np.random.random(len(self.strategies))
        self.n_strategies = len(self.strategies)
        self.followed_strategy = 0

        self.utility = 0
        self.consumption = 0

        self.abs_to_relative = np.array([
            [
                np.where(self.model.roles[0] == 0)[0][0],
                np.where(self.model.roles[0] == 1)[0][0],
                np.where(self.model.roles[0] == 2)[0][0]
            ],
            [
                np.where(self.model.roles[1] == 0)[0][0],
                np.where(self.model.roles[1] == 1)[0][0],
                np.where(self.model.roles[1] == 2)[0][0]
            ],
            [
                np.where(self.model.roles[2] == 0)[0][0],
                np.where(self.model.roles[2] == 1)[0][0],
                np.where(self.model.roles[2] == 2)[0][0]
            ]
        ], dtype=int)

        # Take object with absolute reference to give object relating to agent
        self.int_to_ijk = self.abs_to_relative[agent_type]

        # ----- RL PARAMETERS ---- #

        self.alpha = alpha
        self.temp = temp

    def are_you_satisfied(self, proposed_object):
        return self.strategies[self.followed_strategy, self.int_to_ijk[self.in_hand], self.int_to_ijk[proposed_object]]

    def consume(self):
        self.consumption = self.in_hand == self.C

        if self.consumption:
            self.in_hand = self.P

        self.utility = \
            0.5 + self.consumption / 2 - self.storing_costs[self.in_hand]

        assert 0 <= self.utility <= 1

    # ------------------------ RL PART ------------------------------------------------------ #

    def learn(self):
        self.strategies_values[self.followed_strategy] += \
            self.alpha * (self.utility - self.strategies_values[self.followed_strategy])

    def select_strategy(self):
        p_values = softmax(self.strategies_values, self.temp)
        self.followed_strategy = np.random.choice(np.arange(len(self.strategies_values)), p=p_values)


class Economy(object):

    def __init__(self, role_repartition, t_max, alpha, temp, storing_costs, model, parallel=None):

        self.t_max = t_max

        self.alpha = alpha
        self.temp = temp

        self.role_repartition = role_repartition

        self.storing_costs = storing_costs

        self.n_agent = sum(role_repartition)

        self.model = model

        self.parallel = parallel

        # -------- #

        self.agents = None

        # -------- #

        # For future back up
        self.backup = {
            "exchanges": np.zeros((t_max, 3)),
            "third_good_acceptance": np.zeros((t_max, 3)),
            "n_exchanges": np.zeros(t_max, dtype=int),
            "utility": np.zeros(t_max),
        }

        # ---- #

        self.exchange_order = {0: (0, 1), 1: (0, 2), 2: (1, 2)}

    def create_agents(self):

        agents = []

        agent_idx = 0

        for agent_type, n in enumerate(self.role_repartition):

            i, j, k = self.model.roles[agent_type]

            for ind in range(n):
                a = Agent(
                    alpha=self.alpha,
                    temp=self.temp,
                    prod=i, cons=j, third=k,
                    storing_costs=self.storing_costs[agent_type],
                    agent_type=agent_type,
                    model=self.model,
                    idx=agent_idx)

                agents.append(a)
                agent_idx += 1

        return agents

    def play(self):

        self.agents = self.create_agents()
        _ = self.agents

        if not self.parallel:

            for t in tqdm(range(self.t_max)):

                self.make_computation_for_t(t)
        else:
            for t in range(self.t_max):
                self.make_computation_for_t(t)

        return self.backup

    def make_computation_for_t(self, t):

        exchanges = {(0, 1): 0, (0, 2): 0, (1, 2): 0}
        n_exchange = 0
        utility = 0
        third_good_acceptance = np.zeros(3)
        proposition_of_third_object = np.zeros(3)

        _ = self.agents

        for agent in self.agents:
            agent.select_strategy()

        # Take a random order among the indexes of the agents.
        agent_pairs = np.random.choice(self.n_agent, size=(self.n_agent // 2, 2), replace=False)

        for i, j in agent_pairs:

            i_object = _[i].in_hand
            j_object = _[j].in_hand

            # Each agent is "initiator' of an exchange during one period.
            i_agreeing = _[i].are_you_satisfied(j_object)
            j_agreeing = _[j].are_you_satisfied(i_object)

            # Consider particular case of offering third object
            if _[j].in_hand == _[i].T and _[i].in_hand == _[i].P:
                proposition_of_third_object[_[i].agent_type] += 1

            if _[i].in_hand == _[j].T and _[j].in_hand == _[j].P:
                proposition_of_third_object[_[j].agent_type] += 1

            if i_agreeing and j_agreeing:

                if _[j].in_hand == _[i].T:
                    third_good_acceptance[_[i].agent_type] += 1

                if _[i].in_hand == _[j].T:
                    third_good_acceptance[_[j].agent_type] += 1

                _[i].in_hand = j_object
                _[j].in_hand = i_object

                exchange_type = tuple(sorted([i_object, j_object]))
                exchanges[exchange_type] += 1
                n_exchange += 1

        # Each agent consumes at the end of each round and adapt his behavior.
        for agent in self.agents:
            agent.consume()
            agent.learn()

            # Keep a trace from utilities
            utility += agent.utility

        for key in exchanges.keys():
            exchanges[key] = exchanges[key] / n_exchange

        third_good_acceptance[:] = third_good_acceptance / proposition_of_third_object

        utility = utility / self.n_agent

        # For back up
        self.backup["exchanges"][t] = \
            exchanges[self.exchange_order[0]], \
            exchanges[self.exchange_order[1]], \
            exchanges[self.exchange_order[2]]

        self.backup["third_good_acceptance"][t] = third_good_acceptance
        self.backup["utility"][t] = utility
        self.backup["n_exchanges"][t] = n_exchange


def launch(**kwargs):

    e = Economy(**kwargs)
    return e.play()


def main():

    parameters = {
        "t_max": 10,
        "alpha": 0.1,
        "temp": 0.01,
        "role_repartition": np.array([500, 500, 500]),
        "storing_costs": np.array(
            [
                [0.48, 0.49, 0.5],
                [0.05, 0.06, 0.07],
                [0.15, 0.2, 0.5]
            ]
        ),
        "model": ModelB()
    }

    back_up = \
        launch(**parameters)

    represent_results(backup=back_up, parameters=parameters, save=True)


if __name__ == "__main__":

    main()
