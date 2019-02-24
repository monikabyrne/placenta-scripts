#!/usr/bin/env python
import placentagen as pg
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

import pandas as pd


def get_tree_stats(path):

    print('path = '+ path)

    full_geom = {}
    full_geom['nodes'] = pg.import_exnode_tree(path + '/full_tree.exnode')['nodes'][:, 0:4]
    num_nodes = len(full_geom['nodes'])
    print ('num nodes = ' + str(num_nodes))
    full_geom['elems'] = pg.import_exelem_tree(path + '/full_tree.exelem')['elems']
    num_elems = len(full_geom['elems'])
    print ('num elems = ' + str(num_elems))

    tree_orders = pg.evaluate_orders(full_geom['nodes'],full_geom['elems'])
    strahler_orders = tree_orders['strahler']
    generations = tree_orders['generation']
    print('max strahler order = ' + str(max(strahler_orders)))
    print('max horsfield order = ' + str(max(tree_orders['horsfield'])))
    print('max generations = ' + str(max(generations)))

    #get element connectivity to count the number of non-branching elements in the chorionic tree
    #get second nodes for chorionic elements -  add to count if number of connected elements is less than three

    max_strahler = max(strahler_orders)

    elem_connectivity = pg.element_connectivity_1D(full_geom['nodes'],full_geom['elems'])
    non_branching_elems = np.zeros(max_strahler, dtype=int)
    for i in range(0, num_elems):
        if elem_connectivity['elem_down'][i][0] == 1 :
            non_branching_elems[strahler_orders[i]-1] = non_branching_elems[strahler_orders[i]-1] + 1

    print('Number of non-branching elements per Strahler order:')
    header = ['Strahler order','number of non-branching elements']
    non_branching_elems_df = pd.DataFrame(non_branching_elems)
    print(tabulate(non_branching_elems_df, headers=header))

    bins = []
    for i in range(1, max_strahler+2):
        bins.append(i)

    (frequency,orders_temp) = np.histogram(tree_orders['strahler'],bins)
    orders = orders_temp[0:max_strahler]
    freq_final = np.subtract(frequency,non_branching_elems)
    print ('orders', orders)
    print ('frequency',freq_final)

    #plot number of branches by order
    plt.bar(orders, freq_final)
    heading = 'Number of true branches per Strahler order'
    plt.title(heading)
    plt.legend()
    plt.show()

    #plot number of branches with higher strahler order >= 6
    if max_strahler > 6:
        plt.bar(orders[5:max_strahler], freq_final[5:max_strahler])
        heading = 'Number of true branches per Strahler order >= 6'
        plt.title(heading)
        plt.legend()
        plt.show()

    (branching_ratio, r2) = pg.find_strahler_ratio(orders,freq_final)
    print ('Strahler branching ratio = ' + str(branching_ratio))
    print ('Strahler r**2 = ' + str(r2))


    #Average and min terminal generation(pathlength between the inlet and terminal unit
    path_generations = generations[(strahler_orders == 1)]

    print('Average number of generations at terminal units = ' + str(np.mean(path_generations)))
    print('Minimum number of generations at terminal units = ' + str(np.min(path_generations)))


    return 0

