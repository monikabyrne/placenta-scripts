#!/usr/bin/env python

from placenta_utilities import *

#parameters
umbilical_elems = [0, 1, 2, 3, 34636, 34637, 34638, 34639]

#read the node file
node_loc = pg.import_exnode_tree('full_tree_21_anastomosis/full_tree.exnode')['nodes'][:, 0:4]
num_nodes = len(node_loc)

#read the element file
elems = import_elem_file('full_tree_21_anastomosis/arterial_tree.exelem')
num_elems = len(elems)

#import radii
elem_radii = import_elem_radius('full_tree_21_anastomosis/arterial_radius.exelem')
elem_radii = elem_radii.tolist()
elem_length = get_elem_length(node_loc, elems)

#volume of a cylinder V=pi *r**2h
volume_under_one_artery = 0
total_volume = 0
for i in range(0,num_elems):
    if i not in umbilical_elems:
        elem_volume = np.pi * np.power(elem_radii[i],2) * elem_length[i]
        total_volume = total_volume + elem_volume
        if i < 34636:
            volume_under_one_artery = volume_under_one_artery + elem_volume

print volume_under_one_artery
print total_volume


