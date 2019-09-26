#!/usr/bin/env python

from placenta_utilities import *
from os.path import expanduser

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

home = expanduser("~")

#parameters
#input and output file names
node_in_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step14.exnode'
elems_in_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step14.exelem'

node_out_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step15'
elems_out_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step15'
group_name = 'p49_large_vessels_step15'

#we need to specify inlet nodes, as finding them is based on correct element direction
inlet_nodes = [104,1999]

#read the node file
node_loc = pg.import_exnode_tree(node_in_file)['nodes'][:, 0:4]
num_nodes = len(node_loc)

#read the element file
elems = import_elem_file(elems_in_file)
num_elems = len(elems)

#populate the elems_at_node array listing the elements connected to each node
elems_at_node = get_elements_at_a_node(node_loc,elems)

#for each element at this node, make sure that the node is the first node for the element
seen_elements = np.zeros((num_elems), dtype=bool)

for first_node in inlet_nodes:
    fix_elem_direction(first_node,seen_elements,elems_at_node)

# write the new node file
pg.export_ex_coords(node_loc, group_name, node_out_file, 'exnode')

#write the new element file
pg.export_exelem_1d(elems, group_name, elems_out_file)
