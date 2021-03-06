#!/usr/bin/env python

from placenta_utilities import *
from os.path import expanduser
home = expanduser("~")

#input and output file names
node_in_file = home+'/placenta_patient_49/matlab_skeleton_graph/p49_skeleton_large_vessels.exnode'
elems_in_file = home+'/placenta_patient_49/matlab_skeleton_graph/p49_skeleton_large_vessels.exelem'
node_out_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step1'
elems_out_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step1'
group_name = 'p49_large_vessels_step1'

#read the node file
node_loc = pg.import_exnode_tree(node_in_file)['nodes'][:, 0:4]
num_nodes = len(node_loc)

#read the element file
elems = import_elem_file(elems_in_file)
num_elems = len(elems)

elems_to_remove_list = []
elems_df = pd.DataFrame(elems)
elems_df.columns = ['elem','node1','node2']
for i in range(0,num_elems):
    #check if more elements exist with the same nodes
    duplicate_elems_index = elems_df.index[((elems_df['node1'] == elems_df.iloc[i]['node1'])
        & (elems_df['node2'] == elems_df.iloc[i]['node2'])) | ((elems_df['node2'] == elems_df.iloc[i]['node1'])
        & (elems_df['node1'] == elems_df.iloc[i]['node2'])) ]
    if(len(duplicate_elems_index)>1):
        for j in range(0,len(duplicate_elems_index)):
            if (duplicate_elems_index[j] != i):
                elems_to_remove_list.append(duplicate_elems_index[j])

elems_to_remove = set(elems_to_remove_list) #get rid of duplicates
elems_to_remove = list(elems_to_remove) #back to list for sorting
elems_to_remove.sort()

#remove elements write out the new element and node files

#write the node file
pg.export_ex_coords(node_loc,group_name,node_out_file,'exnode')

old_to_new_elem_temp = np.ones(num_elems, dtype=bool)
old_to_new_elem = np.zeros(num_elems, dtype=int)
for elem in elems_to_remove:
    old_to_new_elem_temp[elem]=False

j = 0
for i in range(0,num_elems):
    if (old_to_new_elem_temp[i]):
        old_to_new_elem[i] = j
        j = j + 1
    else:
        old_to_new_elem[i] = -1

print ('elems_to_remove',len(elems_to_remove))
print elems_to_remove
print ('num_elems',num_elems)

new_elems = np.zeros((num_elems-len(elems_to_remove), 3), dtype=int)

for i in range(0, num_elems):
    new_elem = old_to_new_elem[i]
    if (new_elem >= 0):
        new_elems[new_elem][0] = new_elem
        new_elems[new_elem][1] = elems[i][1]
        new_elems[new_elem][2] = elems[i][2]

#write the new element file
pg.export_exelem_1d(new_elems, group_name, elems_out_file)

