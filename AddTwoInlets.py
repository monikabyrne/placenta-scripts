#!/usr/bin/env python

from placenta_utilities import *
from os.path import expanduser

home = expanduser("~")

#parameters
#input and output file names
node_in_file = home+'/placenta_patient_51/clean_tree/full_tree_21/full_tree.exnode'
elems_in_file = home+'/placenta_patient_51/clean_tree/full_tree_21/full_tree.exelem'
radii_in_file = home+'/placenta_patient_51/clean_tree/full_tree/chorionic_element_radii_cycle3_v5.csv'
#number of chorionic elements and nodes so that we can update the radius file
chor_elems = 1427
chor_nodes = 1428


node_out_file = home+'/placenta_patient_51/clean_tree/full_tree_21_two_inlets/full_tree'
elems_out_file = home+'/placenta_patient_51/clean_tree/full_tree_21_two_inlets/full_tree'
radii_out_file_csv = home+'/placenta_patient_51/clean_tree/full_tree_21_two_inlets/chorionic_element_radii_cycle3_v5_two_inlets.csv'
radii_out_file_ipfiel = home+'/placenta_patient_51/clean_tree/full_tree_21_two_inlets/chorionic_element_radii_cycle3_v5_two_inlets.ipfiel'
group_name = 'p51_full_tree_two_inlets'


#indices of the original inlet element
inlet_elem = 0
#indices of elements that will be moved and will become inlets
new_inlets = [1,827]

#indices of umbilical elements that need to be removed
elems_to_remove = [0]


#read the node file
node_loc = pg.import_exnode_tree(node_in_file)['nodes'][:, 0:4]
num_nodes = len(node_loc)

#read the element file
elems = import_elem_file(elems_in_file)
num_elems = len(elems)

#import radii
radius_file = pd.read_csv(radii_in_file)
elem_radii = radius_file.iloc[:]['radius'].tolist()

#get the z coordinate of the first node of the current inlet element
node1 = elems[inlet_elem][1]
z = node_loc[node1][3]

#node1 will be the first node of the second inlet
second_inlet = new_inlets[1]
elems[second_inlet][1] = node1

for elem in new_inlets:
    #update locations of the first nodes of the new inlets
    node1 = elems[elem][1]
    node2 = elems[elem][2]
    node_loc[node1][1] = node_loc[node2][1]
    node_loc[node1][2] = node_loc[node2][2]
    node_loc[node1][3] = z


print('elems_to_remove', len(elems_to_remove), elems_to_remove)
# some umbilical elements will be removed
old_to_new_elem_temp = np.ones(num_elems, dtype=bool)
old_to_new_elem = np.zeros(num_elems, dtype=int)
for elem in elems_to_remove:
    old_to_new_elem_temp[elem] = False

j = 0
for i in range(0, num_elems):
    if (old_to_new_elem_temp[i]):
        old_to_new_elem[i] = j
        j = j + 1
    else:
        old_to_new_elem[i] = -1


# remove elements and write out the new element and node files

# write the new node file
pg.export_ex_coords(node_loc, group_name, node_out_file, 'exnode')

new_elems = np.zeros((num_elems - len(elems_to_remove), 3), dtype=int)

for i in range(0, num_elems):
    new_elem = old_to_new_elem[i]
    if (new_elem >= 0):
        new_elems[new_elem][0] = new_elem
        new_elems[new_elem][1] = elems[i][1]
        new_elems[new_elem][2] = elems[i][2]

# write the new element file
pg.export_exelem_1d(new_elems, group_name, elems_out_file)


#write the radius file
new_radius_file = radius_file.drop(radius_file.index[elems_to_remove])
new_radius_file.reset_index(inplace=True)
new_radius_file.to_csv(radii_out_file_csv)

new_elem_radii = new_radius_file.iloc[:]['radius'].tolist()
num_elem_radii = chor_elems - len(elems_to_remove)
num_node_radii = chor_nodes


#df = pd.DataFrame(new_node_loc[0:num_node_radii,:])
#df.to_csv(home + '/placenta_patient_51/clean_tree/full_tree_21_two_inlets/new_node_loc_part.csv')

#df = pd.DataFrame(new_node_loc)
#df.to_csv(home + '/placenta_patient_51/clean_tree/full_tree_21_two_inlets/new_node_loc.csv')

write_radius_as_ipfiel(node_loc[0:num_node_radii,:],new_elems[0:num_elem_radii,:], new_elem_radii, radii_out_file_ipfiel)