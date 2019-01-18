#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd


#read the node file
node_file = pd.read_csv('small_vessels/sv_nodes_v1.exnode', sep="\n", header=None)

num_nodes = (len(node_file) - 6)/4
node_loc = np.zeros((num_nodes, 4))

i=0
for n in range(7,len(node_file),4):
    node_loc[i][0] = i
    node_loc[i][1] = node_file[0][n]
    node_loc[i][1] = node_loc[i][1] * 0.1165
    i=i+1

i=0
for n in range(8,len(node_file),4):
    node_loc[i][2] = node_file[0][n]
    node_loc[i][2] = node_loc[i][2] * 0.1165
    i=i+1

i=0
for n in range(9,len(node_file),4):
    node_loc[i][3] = node_file[0][n]
    node_loc[i][3] = node_loc[i][3] * 0.1165
    i=i+1

#write the new node file
pg.export_ex_coords(node_loc, 'sv_nodes_v1_rescaled', 'small_vessels/sv_nodes_v1_rescaled','exnode')

#read the element file
element_file = pd.read_csv('small_vessels/sv_elems_v1.exelem', sep="\n", header=None)

num_elems = (len(element_file)-31)/5
elems = np.zeros((num_elems, 3), dtype=int)

i=0
for n in range(33, len(element_file),5):
    elems[i][0] = i  # creating new element
    nodes = element_file[0][n].split()
    elems[i][1] = int(nodes[0]) - 1 # starts at this node (-1)
    elems[i][2] = int(nodes[1]) - 1 # ends at this node (-1)
    i = i+1

# write the exelem file - no changes for elements, just increment the version number
pg.export_exelem_1d(elems, 'sv_elems_v1_rescaled', 'small_vessels/sv_elems_v1_rescaled')