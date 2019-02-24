#!/usr/bin/env python

from placenta_utilities import *

#parameters
#indices of elements between which an anastomosis is to be inserted
first_elem = 2
#second_elem = 6
second_elem = 828
anastomosis_radius = 1.8 #mm the same as the umbilical artery

#read the node file
node_loc = pg.import_exnode_tree('full_tree_21/full_tree.exnode')['nodes'][:, 0:4]
num_nodes = len(node_loc)

#read the element file
elems = import_elem_file('full_tree_21/full_tree.exelem')
num_elems = len(elems)

#import radii
#radius_file = pd.read_csv('full_tree/chorionic_element_radii_cycle3_v5.csv')
#elem_radii = radius_file.iloc[:]['radius'].tolist()
elem_radii = import_elem_radius('full_tree_21/arterial_radius_21_v2.exelem')
elem_radii = elem_radii.tolist()
#create a new node half way between the first element
(x,y,z) = element_centre_xyz(first_elem,node_loc,elems)

new_node1 = len(node_loc)
node_loc = np.vstack([node_loc,[new_node1, x, y, z]])

#create a new element that starts with the new node and ends with the second node of the first element
i = len(elems)
elems = np.vstack([elems,[i,new_node1,elems[first_elem][2]]])
elem_radii.append(elem_radii[first_elem]) #copy radius from the first element

#update the 2nd node of the first element to the new node
elems[first_elem][2] = new_node1

#create another new node half way between the second element
(x,y,z) = element_centre_xyz(second_elem,node_loc,elems)
new_node2 = len(node_loc)
node_loc = np.vstack([node_loc,[new_node2, x, y, z]])

#create a new element that starts with the new node and ends with the second node of the second element
i = len(elems)
elems = np.vstack([elems,[i,new_node2,elems[second_elem][2]]])
elem_radii.append(elem_radii[second_elem])

#update the 2nd node of the second element to this new node
elems[second_elem][2] = new_node2

#create a new element between the two new nodes - this is the anastomosis
i = len(elems)
elems = np.vstack([elems,[i,new_node1,new_node2]])
elem_radii.append(anastomosis_radius)
anastomosis = i
print 'anastomosis element index= ' + str(anastomosis)

#write out the new node file
pg.export_ex_coords(node_loc, 'full_tree_anast', 'full_tree_anastomosis/full_tree_anast', 'exnode')



#renumber elements (when processing anastomosis, ignore branches downstream of it)
elem_connectivity = pg.element_connectivity_1D(node_loc, elems)
(renumbered_elems,old_to_new_elem) = renumber_elems(node_loc, elems, elem_connectivity,anastomosis)

#write out the new element file
pg.export_exelem_1d(renumbered_elems, 'full_tree_anast', 'full_tree_anastomosis/full_tree_anast')


#renumber radii
new_elem_radii = renumber_elem_radii(elem_radii,old_to_new_elem)

#write the updated radius file

#new_elem_radius_df = pd.DataFrame(new_elem_radii)
#new_elem_radius_df.columns = ['radius']
#new_elem_radius_df.to_csv('chorionic_vessels/chor_radii_anast.csv')
filename = 'full_tree_anastomosis/full_tree_anast_radii.ipfiel'
write_radius_as_ipfiel(node_loc,renumbered_elems, new_elem_radii, filename)