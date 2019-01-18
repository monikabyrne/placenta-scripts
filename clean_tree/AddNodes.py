#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd

#read the large vessel node file
node_file = pd.read_csv('chorionic_vessels/chor_nodes_v1.exnode', sep="\n", header=None)
num_nodes_lv = (len(node_file) - 6)/4
print('num_nodes_lv',num_nodes_lv)
#read the node file
node_file_sv = pd.read_csv('small_vessels/sv_nodes_v3.exnode', sep="\n", header=None)
num_nodes_sv = (len(node_file_sv) - 6)/4
print('num_nodes_sv',num_nodes_sv)
num_nodes = num_nodes_lv + num_nodes_sv
print('num_nodes',num_nodes)
node_loc = np.zeros((num_nodes, 4))

i=0
for n in range(7,len(node_file),4):
    node_loc[i][0] = i
    node_loc[i][1] = node_file[0][n]
    i=i+1

i=0
for n in range(8,len(node_file),4):
    node_loc[i][2] = node_file[0][n]

    i=i+1

i=0
for n in range(9,len(node_file),4):
    node_loc[i][3] = node_file[0][n]
    i=i+1

offset = i
print('offset',offset)
i = offset
for n in range(7, len(node_file_sv), 4):
    node_loc[i][0] = i
    node_loc[i][1] = node_file_sv[0][n]
    i = i + 1

i = offset
for n in range(8, len(node_file_sv), 4):
    node_loc[i][2] = node_file_sv[0][n]

    i = i + 1

i = offset
for n in range(9, len(node_file_sv), 4):
    node_loc[i][3] = node_file_sv[0][n]
    i = i + 1


#write the new node file
pg.export_ex_coords(node_loc, 'combined_nodes_v1', 'chorionic_vessels/combined_nodes_v1','exnode')