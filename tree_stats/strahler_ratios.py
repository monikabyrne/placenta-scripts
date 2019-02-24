#!/usr/bin/env python
import placentagen as pg
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
import pandas as pd
from get_radii_stats import *

#Parameters

#path = 'full_tree_avg_13'
path = 'chorionic_tree_reprosim_results'


#node and element file names, if not given full_tree.exnode and arterial_tree.exelem is used
#node_file = 'full_tree.exnode'
#elem_file = 'arterial_tree.exelem'
node_file = 'chorionic_tree.exnode'
elem_file = 'chorionic_tree.exelem'


print('path = ' + path)

full_geom = {}
full_geom['nodes'] = pg.import_exnode_tree(path + '/' + node_file)['nodes'][:, 0:4]
num_nodes = len(full_geom['nodes'])
print ('num nodes = ' + str(num_nodes))
full_geom['elems'] = pg.import_exelem_tree(path + '/' + elem_file)['elems']
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

#element diameters
elem_radii = import_elem_radius(path + '/radius_perf.exelem')
elem_diameter = elem_radii * 2

#element lengths
lengths = get_elem_length(full_geom['nodes'], full_geom['elems'])

(branch_lengths,branch_diameters,branch_start_end_elems) = \
    get_branch_lengths_and_diameters(full_geom['nodes'], full_geom['elems'],elem_connectivity,lengths,elem_diameter,path)


#get mean element length and diameter by Stahler order
mean_length_by_strahler = np.zeros(max_strahler)
mean_diameter_by_strahler = np.zeros(max_strahler)
count_branch_by_Strahler = np.zeros(max_strahler,dtype=int)

for elem in range(0,num_elems):
    if branch_lengths[elem] > 0:
        #get element order
        order_indx = strahler_orders[elem] - 1
        count_branch_by_Strahler[order_indx] = count_branch_by_Strahler[order_indx] + 1
        mean_length_by_strahler[order_indx] = mean_length_by_strahler[order_indx] + branch_lengths[elem]
        mean_diameter_by_strahler[order_indx] = mean_diameter_by_strahler[order_indx] + branch_diameters[elem]

for order in range(0,max_strahler):
    mean_length_by_strahler[order] = mean_length_by_strahler[order]/count_branch_by_Strahler[order]
    mean_diameter_by_strahler[order] = mean_diameter_by_strahler[order] / count_branch_by_Strahler[order]

orders = []
for i in range(1, max_strahler+1):
    orders.append(i)

#Strahler length ratio

print ('orders', orders)
print ('mean length by Strahler order', mean_length_by_strahler)

(length_ratio, r2) = pg.find_strahler_ratio(orders,mean_length_by_strahler)
print 'Strahler length ratio = ' + str(length_ratio)
print 'r2 = ' + str(r2)


# plot mean branch length by order
plt.bar(orders, mean_length_by_strahler)
heading = 'Mean branch length per Strahler order'
plt.title(heading)
plt.legend()
plt.show()

#Strahler diameter ratio

print ('orders', orders)
print ('mean diameter by Strahler order',mean_diameter_by_strahler)

(diameter_ratio, r2) = pg.find_strahler_ratio(orders,mean_diameter_by_strahler)
print 'Strahler diameter ratio = ' + str(diameter_ratio)
print 'r2 = ' + str(r2)

# plot mean branch diameter by order
plt.bar(orders, mean_diameter_by_strahler)
heading = 'Mean branch diameter per Strahler order'
plt.title(heading)
plt.legend()
plt.show()

#Strahler branching ratio

non_branching_elems = np.zeros(max_strahler, dtype=int)
for i in range(0, num_elems):
    if elem_connectivity['elem_down'][i][0] == 1:
        non_branching_elems[strahler_orders[i] - 1] = non_branching_elems[strahler_orders[i] - 1] + 1

bins = orders[:]
bins.append(max_strahler + 1)
(frequency, orders_temp) = np.histogram(strahler_orders, bins)

freq_final = np.subtract(frequency, non_branching_elems)
print ('orders', orders)
print ('frequency', freq_final)

(branching_ratio, r2) = pg.find_strahler_ratio(orders, freq_final)
print 'Strahler branching ratio = ' + str(branching_ratio)
print 'Strahler r**2 = ' + str(r2)

# plot number of branches by order
plt.bar(orders, freq_final)
heading = 'Number of true branches per Strahler order'
plt.title(heading)
plt.legend()
plt.show()