import numpy as np


def represent_results(backup, parameters, display=True, fig_name=None):

    from pylab import plt

    exchanges_list = backup["exchanges"]
    mean_utility_list = backup["utility"]
    n_exchanges_list = backup["n_exchanges"]
    accept_third_object = backup["third_good_acceptance"]

    # What is common to all subplots
    fig = plt.figure(figsize=(25, 12))
    fig.patch.set_facecolor('white')
    x = np.arange(len(exchanges_list))
    n_lines = 2
    n_columns = 3

    # First subplot
    ax = plt.subplot(n_lines, n_columns, 1)
    ax.set_title("Proportion of each type of exchange according to time \n")

    y0 = []
    y1 = []
    y2 = []
    for exchanges in exchanges_list:
        y0.append(exchanges[0])
        y1.append(exchanges[1])
        y2.append(exchanges[2])

    ax.plot(x, y0, label="Exchange (1, 2)", linewidth=2)
    ax.plot(x, y2, label="Exchange (1, 3)", linewidth=2)
    ax.plot(x, y1, label="Exchange (2, 3)", linewidth=2)
    ax.legend()

    # Second subplot

    ax = plt.subplot(n_lines, n_columns, 2)
    ax.set_title("Utility average according to time \n")
    ax.plot(x, mean_utility_list, linewidth=2)

    # Third subplot
    ax = plt.subplot(n_lines, n_columns, 3)
    ax.set_title("Total number of exchanges according to time \n")
    ax.plot(x, n_exchanges_list, linewidth=2)

    # Fourth subplot
    ax = plt.subplot(n_lines, n_columns, 4)
    ax.set_title("Frequency of acceptance of the third good according to time \n")
    ax.plot(x, [i[0] for i in accept_third_object],
            label="Agent I ({}, {})".format(
                parameters["model"].roles[0, 0] + 1,
                parameters["model"].roles[0, 1] + 1), linewidth=2)
    ax.plot(x, [i[1] for i in accept_third_object],
            label="Agent II ({}, {})".format(
                parameters["model"].roles[1, 0] + 1,
                parameters["model"].roles[1, 1] + 1), linewidth=2)
    ax.plot(x, [i[2] for i in accept_third_object],
            label="Agent III ({}, {})".format(
                parameters["model"].roles[2, 0] + 1,
                parameters["model"].roles[2, 1] + 1), linewidth=2)
    ax.legend()

    # Fifth subplot
    ind = np.arange(3)
    width = 0.5
    ax = plt.subplot(n_lines, n_columns, 5)
    ax.set_title("Storing costs \n")
    if parameters["storing_costs"].shape == (3,):
        ax.bar(ind, parameters["storing_costs"], width)
    else:
        ax.bar(ind, parameters["storing_costs"][0], width / 3, label="Agent I")
        ax.bar(ind + width * (1/3), parameters["storing_costs"][1], width / 3, label="Agent II", color="green")
        ax.bar(ind + width * (2/3), parameters["storing_costs"][2], width / 3, label="Agent III", color="red")
        ax.legend()
    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('none')
    ax.set_xticks(ind + width/2)
    ax.set_xticklabels(('$c_1$', '$c_2$', '$c_3$'), fontsize=16)

    # Sixth subplot
    ax = plt.subplot(n_lines, n_columns, 6)
    ax.set_title("Parameters")
    ax.axis('off')
    # ax.set_xticks([]), ax.set_yticks([])
    msg = \
        "Model: {}; \n \n" \
        "Role repartition: {}; \n \n " \
        "Learning rate: {}; \n \n" \
        "Softmax temp: {}; \n \n" \
        "Trials: {}. \n \n" \
        .format(
            parameters["model"],
            parameters["role_repartition"],
            parameters["alpha"],
            parameters["temp"],
            parameters["t_max"]
        )

    ax.text(0.5, 0.5, msg, ha='center', va='center', size=12)

    # Saving
    if fig_name:

        plt.savefig(fig_name)

    # Display
    if display:

        plt.show()

    plt.close()

