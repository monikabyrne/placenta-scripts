#!/usr/bin/env python
 
from placenta_utilities import *


#read the node file
node_loc = pg.import_exnode_tree('new_nodes_sb_30_5.exnode')['nodes'][:, 0:4]
num_nodes = len(node_loc)

#read the element file
elems = import_elem_file('new_elems_sb_30_5.exelem')
num_elems = len(elems)


elems_at_node = get_elements_at_a_node(node_loc,elems)


radius_file = pd.read_csv('elem_radius_sb_30_5.csv')
elem_radius = radius_file.iloc[:]['radius'].tolist()

#remove thin branches - we shouldn't have any in the chorionic tree
radius_threshold = 5

elems_to_remove = []
elem_nodes = []

for elem in range(0,num_elems):
    if (elem_radius[elem] < radius_threshold):
        elems_to_remove.append(elem)
        elem_nodes.append(elems[elem][1])
        elem_nodes.append(elems[elem][2])

print('elems_to_remove', len(elems_to_remove), elems_to_remove)

#check if nodes to be removed are not connected to elements which won't be removed
node_candidates = []
node_candidates.extend(set(elem_nodes))
node_candidates.sort()

nodes_to_remove = []

for node in range(0,len(node_candidates)):
    #get elements connected to the node
    connected_elems = elems_at_node[node][0]
    leave_node = False
    for j in range(1,connected_elems+1):
        elem2 = elems_at_node[node][j]
        if elem2 not in elems_to_remove:
            leave_node = True
    if not leave_node:
        nodes_to_remove.append(node)

print('nodes_to_remove',len(nodes_to_remove),nodes_to_remove)

#remove elements and nodes and write out the new element and node files

old_to_new_node_temp = np.ones(num_nodes, dtype=bool)
old_to_new_node = np.zeros(num_nodes, dtype=int)
for node in nodes_to_remove:
    old_to_new_node_temp[node]=False

j = 0
for i in range(0,num_nodes):
    if (old_to_new_node_temp[i]):
        old_to_new_node[i] = j
        j = j + 1
    else:
        old_to_new_node[i] = -1


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


new_node_loc = np.zeros((num_nodes-len(nodes_to_remove), 4))
for i in range(0,num_nodes):
    new_node = old_to_new_node[i]
    if (new_node >= 0):
        new_node_loc[new_node][0] = new_node
        new_node_loc[new_node][1] = node_loc[i][1]
        new_node_loc[new_node][2] = node_loc[i][2]
        new_node_loc[new_node][3] = node_loc[i][3]
#write the new node file
pg.export_ex_coords(new_node_loc,'new_nodes_tb_'+str(radius_threshold),
                    'new_nodes_tb_'+str(radius_threshold),'exnode')

new_elems = np.zeros((num_elems-len(elems_to_remove), 3), dtype=int)

for i in range(0, num_elems):
    new_elem = old_to_new_elem[i]
    if (new_elem >= 0):
        new_elems[new_elem][0] = new_elem
        new_elems[new_elem][1] = old_to_new_node[elems[i][1]]
        if (old_to_new_node[elems[i][1]] == -1):
            print('elem',i,'new elem',new_elem,'old node',elems[i][1])
        new_elems[new_elem][2] = old_to_new_node[elems[i][2]]
        if (old_to_new_node[elems[i][2]] == -1):
            print('elem', i, 'new elem', new_elem, 'old node', elems[i][2])
#write the new element file
pg.export_exelem_1d(new_elems, 'new_elems_tb_'+str(radius_threshold)
                    , 'new_elems_tb_'+str(radius_threshold))

#write the radius file again
radius_info = radius_file[['mean_radius', 'shortest_radius', 'mean_as_percentage_of_shortest','radius']].copy()
new_radius_file = radius_info.drop(radius_file.index[elems_to_remove])
new_radius_file.reset_index(inplace=True)
filename = 'elem_radius_tb_' +str(radius_threshold) + '.csv'
new_radius_file.to_csv(filename)