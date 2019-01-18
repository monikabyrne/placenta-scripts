#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd

#gets the total length of all generations of branches connected to the node, nodes and elements in all generations
#and nodes that have already been seen until a length threshold is reached
def get_downstream_length(node,upstream_elem,total_length,length_threshold):
    gr_nodes = []
    gr_nodes.append(node)
    # get all elements connected to the node (apart from the upstream element) and sum up their lengths
    connected_elems_no = elems_at_node[node][0]
    gr_elems = []

    # for each of the elements
    for i in range(0,connected_elems_no):
        elem = elems_at_node[node][i + 1]  # elements start at column index 1
        if ((elem != upstream_elem) & (total_length < length_threshold)):
            gr_elems.append(elem)
            #add length of the current element
            total_length = total_length + elem_length[elem]
            if (total_length < length_threshold):
                # get the second node for the element
                temp_node1 = elems[elem][1]
                temp_node2 = elems[elem][2]
                if (node == temp_node1):
                    node2 = temp_node2
                if (node == temp_node2):
                    node2 = temp_node1
                subgroup_info = get_downstream_length(node2,elem,total_length,length_threshold)
                total_length = subgroup_info['length']
                gr_elems.extend(subgroup_info['gen_elems'])
                gr_nodes.extend(subgroup_info['gen_nodes'])

    group_info = {}
    group_info['length'] = total_length
    group_info['gen_elems'] = gr_elems
    group_info['gen_nodes'] = gr_nodes

    return group_info


#read the node file
#node_file = pd.read_csv('skeleton_mb_2.exnode',sep="\n", header=None) #1st run
#node_file = pd.read_csv('nodes_corrected_v2.exnode',sep="\n", header=None) #2nd run
#node_file = pd.read_csv('new_nodes_50_v2.exnode', sep="\n", header=None) #3rd run (remove node 147)
#node_file = pd.read_csv('new_nodes_v3.exnode', sep="\n", header=None) #4th run large vessels
#node_file = pd.read_csv('sv_nodes_v1.exnode', sep="\n", header=None)  #1st run small vessels
node_file = pd.read_csv('chorionic_vessels/chor_nodes_cycle2_v2.exnode', sep="\n", header=None)

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
#element_file = pd.read_csv('skeleton_mb_2.exelem',sep="\n", header=None) #1st run
#element_file = pd.read_csv('elems_corrected_v2.exelem',sep="\n", header=None) #2nd run
#element_file = pd.read_csv('new_elems_50_v2.exelem', sep="\n", header=None) #3rd run
#element_file = pd.read_csv('new_elems_v3.exelem', sep="\n", header=None) #4th run large vessels
element_file = pd.read_csv('chorionic_vessels/chor_elems_cycle2_v2.exelem', sep="\n", header=None) #1st run small vessels

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


#calculate element lengths
elem_length = np.zeros((num_elems))
for i in range(0,num_elems):
    node1 = elems[i][1]
    node2 = elems[i][2]
    x1 = node_loc[node1][1]
    y1 = node_loc[node1][2]
    z1 = node_loc[node1][3]

    x2 = node_loc[node2][1]
    y2 = node_loc[node2][2]
    z2 = node_loc[node2][3]
    # calculate the length of each element
    elem_length[i] = np.sqrt(np.float_power(x2 - x1,2) + np.float_power(y2 - y1,2) + np.float_power(z2 - z1,2))

#print elem_length to csv
#df1 = pd.DataFrame(elem_length)
#df1.to_csv('elem_length.csv')

#populate the elems_at_node array listing the elements connected to each node
elems_at_node = np.zeros((num_nodes, 20), dtype=int)
for i in range(0,num_elems):

      elems_at_node[elems[i][1]][0] = elems_at_node[elems[i][1]][0] + 1
      j = elems_at_node[elems[i][1]][0]
      elems_at_node[elems[i][1]][j] = elems[i][0]

      elems_at_node[elems[i][2]][0] = elems_at_node[elems[i][2]][0] + 1
      j = elems_at_node[elems[i][2]][0]
      elems_at_node[elems[i][2]][j] = elems[i][0]

#print elems_at_node to csv
df = pd.DataFrame(elems_at_node)
#df.to_csv('elems_at_node.csv')

orphan_nodes = []
for i in range(0,num_nodes):
    if (elems_at_node[i][0] == 0):
        orphan_nodes.append(i)

print('orphan nodes',len(orphan_nodes),orphan_nodes)

#first look at nodes that just have one element connected - candidate starting points
end_nodes = []
for i in range(0,num_nodes):
    if (elems_at_node[i][0] == 1):
        end_nodes.append(i)

#remove short disconnected branches

#calculate which groups of elements and nodes are below a length threshold - these nodes and elements will be
#removed later
#length_threshold = 500 #1st run
length_threshold = 100
short_group_elems = []
short_group_nodes = []

for node in end_nodes:

    gr_nodes = []
    gr_nodes.append(node)
    # get the single element attached to this node
    elem = elems_at_node[node][1]
    gr_elems = []
    gr_elems.append(elem)
    # add length of the current element
    total_length = elem_length[elem]
    if (total_length < length_threshold):
        # get the second node for that element
        temp_node1 = elems[elem][1]
        temp_node2 = elems[elem][2]
        if (node == temp_node1):
            node2 = temp_node2
        if (node == temp_node2):
            node2 = temp_node1
        group_info = get_downstream_length(node2,elem,total_length,length_threshold)
        total_length = group_info['length']
        if (total_length < length_threshold):
            gr_elems.extend(group_info['gen_elems'])
            gr_nodes.extend(group_info['gen_nodes'])
            #populate arrays of nodes and elements to be removed
            short_group_elems.extend(gr_elems)
            short_group_nodes.extend(gr_nodes)

print('short_group_elems',len(set(short_group_elems)),set(short_group_elems))
elems_to_remove = []
elems_to_remove.extend(set(short_group_elems))
#elems_to_remove.extend([1372, 1373]) #temp
elems_to_remove.sort()
print('elems_to_remove',len(elems_to_remove),elems_to_remove)

print ('short_group_nodes',len(set(short_group_nodes)),set(short_group_nodes))


#nodes which are not connected to any elements
nodes_to_remove = orphan_nodes
#short disconnected branches
nodes_to_remove.extend(set(short_group_nodes))

#nodes_to_remove.extend([147]) #temp
nodes_to_remove.sort()
print('nodes_to_remove',len(nodes_to_remove),nodes_to_remove)


#copy elements and nodes that will be removed to a separate file
for elem in elems_to_remove:
    #check if all element nodes will be removed too
    node1 = elems[elem][1]
    node2 = elems[elem][2]
    if (node1 not in nodes_to_remove):
        print ('element',elem, 'node',node1,'not in nodes to remove')
    if (node2 not in nodes_to_remove):
        print ('element',elem, 'node',node2,'not in nodes to remove')


version = '_v2'

old_to_new_node_temp = np.zeros(num_nodes, dtype=bool)
old_to_new_node = np.zeros(num_nodes, dtype=int)
for node in nodes_to_remove:
    old_to_new_node_temp[node]=True

j = 0
for i in range(0,num_nodes):
    if (old_to_new_node_temp[i]):
        old_to_new_node[i] = j
        j = j + 1
    else:
        old_to_new_node[i] = -1


old_to_new_elem_temp = np.zeros(num_elems, dtype=bool)
old_to_new_elem = np.zeros(num_elems, dtype=int)
for elem in elems_to_remove:
    old_to_new_elem_temp[elem]=True

j = 0
for i in range(0,num_elems):
    if (old_to_new_elem_temp[i]):
        old_to_new_elem[i] = j
        j = j + 1
    else:
        old_to_new_elem[i] = -1

nodes_remove_loc = np.zeros((len(nodes_to_remove), 4))
for i in range(0,num_nodes):
    new_node = old_to_new_node[i]
    if (new_node >= 0):
        nodes_remove_loc[new_node][0] = new_node
        nodes_remove_loc[new_node][1] = node_loc[i][1]
        nodes_remove_loc[new_node][2] = node_loc[i][2]
        nodes_remove_loc[new_node][3] = node_loc[i][3]
#write the new node file
name = 'nodes_remove_'+str(length_threshold) + version
pg.export_ex_coords(nodes_remove_loc, name, name, 'exnode')


elems_remove = np.zeros((len(elems_to_remove), 3), dtype=int)

for i in range(0, num_elems):
    new_elem = old_to_new_elem[i]
    if (new_elem >= 0):
        elems_remove[new_elem][0] = new_elem
        elems_remove[new_elem][1] = old_to_new_node[elems[i][1]]
        if (old_to_new_node[elems[i][1]] == -1):
            print('elem',i,'new elem',new_elem,'old node',elems[i][1])
        elems_remove[new_elem][2] = old_to_new_node[elems[i][2]]
        if (old_to_new_node[elems[i][2]] == -1):
            print('elem', i, 'new elem', new_elem, 'old node', elems[i][2])
#write the new element file
name = 'elems_remove_'+str(length_threshold) + version
pg.export_exelem_1d(elems_remove, name, name)

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


#print to csv
#df = pd.DataFrame(old_to_new_node)
#df.to_csv('old_to_new_node.csv')

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
#name = 'sv_nodes_'+str(length_threshold) + version
pg.export_ex_coords(new_node_loc, 'chor_nodes_cycle2_v3', 'chorionic_vessels/chor_nodes_cycle2_v3', 'exnode')


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
#name = 'sv_elems_'+str(length_threshold) + version
pg.export_exelem_1d(new_elems, 'chor_elems_cycle2_v3', 'chorionic_vessels/chor_elems_cycle2_v3')
