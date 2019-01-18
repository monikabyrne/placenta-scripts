#!/usr/bin/env python
import placentagen as pg
import numpy as np
import pandas as pd


#read the node file
node_file = pd.read_csv('chorionic_vessels/chor_nodes_v2.exnode',sep="\n", header=None)

num_nodes = (len(node_file) - 6)/4
node_loc = np.zeros((num_nodes, 4))


#get the last node number in the file
[text,last_node] = node_file.iloc[len(node_file)-4][0].split()
old_to_new_node = np.zeros(int(last_node)+1, int)
i=0
for n in range(6,len(node_file),4):
    line = node_file[0][n]
    [text, node_number] = line.split()
    old_to_new_node[int(node_number)] = i
    i=i+1


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

#write the exnode file
pg.export_ex_coords(node_loc,'chor_nodes_v3','chorionic_vessels/chor_nodes_v3','exnode')


#read the element file
element_file = pd.read_csv('chorionic_vessels/chor_elems_v2.exelem',sep="\n", header=None)

num_elems = (len(element_file)-31)/5
elems = np.zeros((num_elems, 3), dtype=int)

i=0
for n in range(33, len(element_file),5):
    elems[i][0] = i  # creating new element
    nodes = element_file[0][n].split()
    elems[i][1] = old_to_new_node[int(nodes[0])]  # starts at this node
    elems[i][2] = old_to_new_node[int(nodes[1])]  # ends at this node
    i = i+1


# write the exelem file
pg.export_exelem_1d(elems, 'chor_elems_v3', 'chorionic_vessels/chor_elems_v3')
