#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd


#read the node file
#node_file = pd.read_csv('skeleton_mb.exnode',sep="\n", header=None) #1st run
#node_file = pd.read_csv('new_nodes_v2.exnode',sep="\n", header=None) #2nd run large vessels
#node_file = pd.read_csv('small_vessels/skeleton_sv.exnode',sep="\n", header=None) #1st run small vessels
node_file = pd.read_csv('chorionic_vessels/chor_nodes_v1.exnode',sep="\n", header=None)

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
#element_file = pd.read_csv('skeleton_mb.exelem',sep="\n", header=None) #1st run
#element_file = pd.read_csv('new_elems_v2.exelem',sep="\n", header=None) #2nd run large vessels
#element_file = pd.read_csv('small_vessels/skeleton_sv.exelem',sep="\n", header=None) #1st run small vessels
element_file = pd.read_csv('chorionic_vessels/chor_elems_v1.exelem',sep="\n", header=None)

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
pg.export_ex_coords(node_loc,'chor_nodes_v2','chorionic_vessels/chor_nodes_v2','exnode')

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
pg.export_exelem_1d(new_elems, 'chor_elems_v2', 'chorionic_vessels/chor_elems_v2')

