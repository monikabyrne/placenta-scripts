#!/usr/bin/env python

import placentagen as pg
import numpy as np
import pandas as pd


# read the node file
node_file = pd.read_csv('new_nodes_500.exnode', sep="\n", header=None)

num_nodes = (len(node_file) - 6) / 4
node_loc = np.zeros((num_nodes, 4))

i = 0
for n in range(7, len(node_file), 4):
    node_loc[i][0] = i
    node_loc[i][1] = node_file[0][n]
    i = i + 1

i = 0
for n in range(8, len(node_file), 4):
    node_loc[i][2] = node_file[0][n]
    i = i + 1

i = 0
for n in range(9, len(node_file), 4):
    node_loc[i][3] = node_file[0][n]
    i = i + 1

# write the exnode file
# pg.export_ex_coords(node_loc,'test_node_file','test_node_file','exnode')


# read the element file
element_file = pd.read_csv('new_elems_500.exelem', sep="\n", header=None)

num_elems = (len(element_file) - 31) / 5
elems = np.zeros((num_elems, 3), dtype=int)

i = 0
for n in range(33, len(element_file), 5):
    elems[i][0] = i  # creating new element
    nodes = element_file[0][n].split()
    elems[i][1] = int(nodes[0]) - 1  # starts at this node (-1)
    elems[i][2] = int(nodes[1]) - 1  # ends at this node (-1)
    i = i + 1

# write the exelem file
# pg.export_exelem_1d(elems, 'test_elems', 'test_elems')


# calculate element lengths
elem_length = np.zeros((num_elems))
for i in range(0, num_elems):
    node1 = elems[i][1]
    node2 = elems[i][2]
    x1 = node_loc[node1][1]
    y1 = node_loc[node1][2]
    z1 = node_loc[node1][3]

    x2 = node_loc[node2][1]
    y2 = node_loc[node2][2]
    z2 = node_loc[node2][3]
    # calculate the length of each element
    elem_length[i] = np.sqrt(np.float_power(x2 - x1, 2) + np.float_power(y2 - y1, 2) + np.float_power(z2 - z1, 2))

# print elem_length to csv
df1 = pd.DataFrame(elem_length)
df1.to_csv('elem_length_new_elems_500.csv')