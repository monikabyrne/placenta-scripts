#!/usr/bin/env python
 
from placenta_utilities import *
from os.path import expanduser

home = expanduser("~")

#parameters
#input and output file names
node_in_file = home+'/placenta_patient_51/clean_tree/full_tree_21_two_inlets/full_tree.exnode'
elems_in_file = home+'/placenta_patient_51/clean_tree/full_tree_21_two_inlets/full_tree.exelem'
vessel_radius_in_file = home+'/placenta_patient_51/clean_tree/full_tree_21_two_inlets/arterial_radii.csv'

node_out_file = home+'/placenta_patient_51/volume_fed_by_each_artery/full_tree_21_2inlets_renumbered'
elems_out_file = home+'/placenta_patient_51/volume_fed_by_each_artery/full_tree_21_2inlets_renumbered'
group_name = 'p51_full_tree_21_2inlets_renumbered'
vessel_radius_out_file = home+'/placenta_patient_51/volume_fed_by_each_artery/art_radii_full_tree_21_2inlets_renumbered.csv'


#read the node file
node_loc = pg.import_exnode_tree(node_in_file)['nodes'][:, 0:4]
num_nodes = len(node_loc)

#read the element file
elems = import_elem_file(elems_in_file)
num_elems = len(elems)

#get element radii
radius_file = pd.read_csv(vessel_radius_in_file)
elem_radii = radius_file.iloc[:]['radius'].tolist()

#populate the elems_at_node array listing the elements connected to each node
elems_at_node = get_elements_at_a_node(node_loc,elems)

elem_connectivity = pg.element_connectivity_1D(node_loc, elems)
anast_exists = False
(renumbered_elems,old_to_new_elem) = renumber_elems(node_loc, elems, elem_connectivity, anast_exists, 0)


# write the new node file - no updates, just a different file name
pg.export_ex_coords(node_loc, group_name, node_out_file, 'exnode')

#write the new element file
pg.export_exelem_1d(renumbered_elems, group_name, elems_out_file)


#renumber radii
new_elem_radii = renumber_elem_radii(elem_radii,old_to_new_elem)

#write the updated radius file
new_elem_radii_df = pd.DataFrame(new_elem_radii)
new_elem_radii_df.columns = ['radius']
new_elem_radii_df.to_csv(vessel_radius_out_file)