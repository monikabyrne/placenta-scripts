#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd


#read element radius
radius_file = pd.read_csv('elem_radius_large_vessels_v8.csv')

radius = radius_file.iloc[:]['updated_radius'].tolist()


#read the node file
node_file = pd.read_csv('new_nodes_v8.exnode', sep="\n", header=None)

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


#read the element file
element_file = pd.read_csv('new_elems_v8.exelem', sep="\n", header=None)

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




version = 'large_vessels_v9'


#assign a radius to nodes
#first element - both nodes will have the same radius as the element - for all other elements assign the element radius
#to the second node

inlet_element = 1359
node_radius = np.zeros(num_nodes, dtype=float)
for i in range(0,num_elems):
    node1 =  elems[i][1]
    node2 =  elems[i][2]
    if i == inlet_element:
        node_radius[node1] = radius[i]
        node_radius[node2] = radius[i]
    else:
        node_radius[node2] = radius[i]

node_radius_df = pd.DataFrame(
    columns=['node', 'radius'])
for node in range(0,num_nodes):
    node_radius_df.loc[node] = [node, node_radius[node]]

filename = 'node_radius_' + version + '.csv'
node_radius_df.to_csv(filename)


#write the node radius to an ipfiel file
filename = 'elem_radius_'+ version + '.ipfiel'

f = open(filename, 'w')

f.write("CMISS Version 2.1  ipelem File Version 2\n")
f.write("Heading:\n")
f.write("\n")
f.write("The number of nodes is [     {0}]:      {1}\n".format(num_nodes, num_nodes))
f.write("Do you want prompting for different versions of field variable 1 [N]? Y\n")
f.write("The number of derivatives for field variable 1 is [0]: 0\n")


for n in range(0, num_nodes):
    f.write("\n")
    f.write("Node number [     {0}]:    {1}\n".format(n+1, n+1))
    f.write("The number of versions for field variable 1 is [1]:  1\n")
    #use scientific notation for radius values
    f.write("The field variable 1 value is [ {0:.5e}]:  {1:.5e}\n".format(node_radius[n], node_radius[n]))

f.close()

#write a csv file listing nodes, elements at a node, and stats on element radii: min radius, max radius,
# mean radius and standard deviation in radii values

element_radii_at_node = pd.DataFrame(
    columns=['node', 'upstream_element', 'upstream_radius', 'no_of_downstream_elems', 'downstream_elements',
             'downstream_min_radius', 'downstream_max_radius', 'mean_elem_radii', 'min_elem_radius',
             'max_elem_radius', 'elem_radius_std'])

for node in range(0,num_nodes):
    no_of_connected_elems = elems_at_node[node][0]
    upstream_elem = -1
    downstream_elems = []
    for i in range(0, no_of_connected_elems):
        elem = elems_at_node[node][i+1]
        #get element nodes
        node1 = elems[elem][1]
        node2 = elems[elem][2]
        if node == node2:
            upstream_elem = elem
        else:
            downstream_elems.append(elem)

    element_radii = []
    upstream_radius = 0
    if upstream_elem != -1:
        upstream_radius = radius[upstream_elem]
        element_radii.append(upstream_radius)

    no_of_downstream_elems = len(downstream_elems)
    downstream_min_radius = 0
    downstream_max_radius = 0
    if no_of_downstream_elems > 0:
        downstream_radii = []
        for j in range(0,len(downstream_elems)):
            downstream_radii.append(radius[downstream_elems[j]])

        element_radii.extend(downstream_radii)
        downstream_min_radius = np.min(downstream_radii)
        downstream_max_radius = np.max(downstream_radii)

    mean_elem_radii = np.mean(element_radii)
    min_elem_radius = np.min(element_radii)
    max_elem_radius = np.max(element_radii)
    elem_radius_std = np.std(element_radii)

    element_radii_at_node.loc[node] = [node, upstream_elem, upstream_radius, no_of_downstream_elems,
                                       downstream_elems, downstream_min_radius, downstream_max_radius,
                                       mean_elem_radii, min_elem_radius, max_elem_radius, elem_radius_std]

filename = 'element_radii_at_node_' + version + '.csv'
element_radii_at_node.to_csv(filename)