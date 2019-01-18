#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd


def fix_elem_direction(first_node,seen_elements,elems_at_node):
    # get all elements connected to the node that we haven't seen
    connected_elems_no = elems_at_node[first_node][0]
    for i in range(0, connected_elems_no):
        elem = elems_at_node[first_node][i + 1]  # elements start at column index 1
        if not seen_elements[elem]:
            if elems[elem][1] != first_node:
                # swap nodes
                elems[elem][2] = elems[elem][1]
                elems[elem][1] = first_node
                print('swapping nodes for element',elem)
            seen_elements[elem] = True
            second_node = elems[elem][2]
            fix_elem_direction(second_node,seen_elements,elems_at_node)
    return seen_elements

#read the node file
#node_file = pd.read_csv('new_nodes_v4.exnode', sep="\n", header=None)
node_file = pd.read_csv('chorionic_vessels/chor_nodes_cycle2_v4.exnode', sep="\n", header=None)

num_nodes = (len(node_file) - 6)/4
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

#write the exnode file
#pg.export_ex_coords(node_loc,'test_node_file','test_node_file','exnode')


#read the element file
#element_file = pd.read_csv('new_elems_v4.exelem', sep="\n", header=None)
element_file = pd.read_csv('chorionic_vessels/chor_elems_cycle2_v4.exelem', sep="\n", header=None)


num_elems = (len(element_file)-31)/5
elems = np.zeros((num_elems, 3), dtype=int)

i=0
for n in range(33, len(element_file),5):
    elems[i][0] = i  # creating new element
    nodes = element_file[0][n].split()
    elems[i][1] = int(nodes[0]) - 1 # starts at this node (-1)
    elems[i][2] = int(nodes[1]) - 1 # ends at this node (-1)
    i = i+1

# write the exelem file
#pg.export_exelem_1d(elems, 'test_elems', 'test_elems')


#populate the elems_at_node array listing the elements connected to each node
elems_at_node = np.zeros((num_nodes, 10), dtype=int)
for i in range(0,num_elems):

      elems_at_node[elems[i][1]][0] = elems_at_node[elems[i][1]][0] + 1
      j = elems_at_node[elems[i][1]][0]
      elems_at_node[elems[i][1]][j] = elems[i][0]

      elems_at_node[elems[i][2]][0] = elems_at_node[elems[i][2]][0] + 1
      j = elems_at_node[elems[i][2]][0]
      elems_at_node[elems[i][2]][j] = elems[i][0]

#print elems_at_node to csv
#df = pd.DataFrame(elems_at_node)
#df.to_csv('elems_at_node.csv')


first_node = 1360 #inlet_node

#for each element at this node, make sure that the node is the first node for the element
seen_elements = np.zeros((num_elems), dtype=bool)
fix_elem_direction(first_node,seen_elements,elems_at_node)

#write the new node file
pg.export_ex_coords(node_loc, 'chor_nodes_cycle2_v5', 'chorionic_vessels/chor_nodes_cycle2_v5', 'exnode')


#write the new element file
pg.export_exelem_1d(elems, 'chor_elems_cycle2_v5', 'chorionic_vessels/chor_elems_cycle2_v5')

