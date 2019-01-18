#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd


#read element radius
radius_file = pd.read_csv('chorionic_vessels/large_vessel_radius_cycle2_v1.csv')

radius = radius_file.iloc[:]['radius'].tolist()


#read the element numbers with a small radius (under 5 units)
# after rescaling: look at radii under 0.6

#small_radius_file = pd.read_csv('elements_small_radius.csv')
#elem_list = small_radius_file.iloc[:]['element_numbers'].tolist()

#elements added manually override the radius
#elem_list.extend([142,204,90,347,205]) #1st run
#2nd run - elements where there were sharp jumps between their radius and the radius of connected elements
#elem_list.extend([353,352,346,345,334,333,310,53,44,81,309,1247,335,157,1097,325])

elem_list = [];
elem_list.extend([42,95,127,128,129,130,131,232,233,234,235,236,237,238,274,318,319,320,321,431,432,433]) #cycle 2 version 1
elem_list.extend([433,434,435,436,430,391,388,389,380,644,555,556,557,531,541,542,543,544,545,1429,1428])
elem_list.extend([1353,1354,1355,1386,1417,1418,1419,1420,1421,1422,1423,1424,1425,1426,1427,999,1001,1002,1003])
elem_list.extend([1004,1005,779,822,823,824,825,837,838,839,840,841,830,831,832,833,834,835,900,901,1016])
elem_list.extend([1168,1169,1170,1171,1172,1173,1174,1175,1176,1177,1178,1179,1097,1098,1099,1100,1101,1102,1103])
elem_list.extend([1091,1092,1193,1291,1292,1293,1294,1295,1296,1297,1298,1299,1300,1280,1281,1268,1269,1270])

#run this script again for all elements with sharp radius changes
elem_list.sort()
#print ('elements with a small radius (element index)',elem_list)
print ('manually added elements (element index)',elem_list)
umbilical_artery_elems = [0,1,2,209,210] #these must be in elements with small radius file
print ('umbilical artery elements',umbilical_artery_elems)
villous_tree_stems = [208,138,239,440,441,442,439,322,438,437,1430,645,546,631,1415,1015,842,1180] #set these to 0.7 mm
print ('villous tree stems',villous_tree_stems)

elem_list.extend(umbilical_artery_elems)
elem_list.extend(villous_tree_stems)
elem_list.sort()
print ('all elements whose radius will be updated (element index)',elem_list)

#read the node file
node_file = pd.read_csv('chorionic_vessels/chor_nodes_cycle2_v6.exnode', sep="\n", header=None)

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
element_file = pd.read_csv('chorionic_vessels/chor_elems_cycle2_v6.exelem', sep="\n", header=None)

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

updated_radius = radius[:] #creates a copy of radius
#rescaling radius as 1 unit = 0.1165 mm in the micro-CT images of the placenta
#multiply the current radii by 0.1165 so that 1 unit = 1 mm
#updated_radius = np.multiply(updated_radius,0.1165) radii are in the correct scale already
updated_elem_list = []

for elem_with_small_radius in elem_list:

    if elem_with_small_radius in umbilical_artery_elems:
        #assign a radius of 3 mm to umbilical cord arteries
        updated_radius[elem_with_small_radius] = 3
    elif elem_with_small_radius in villous_tree_stems:
        updated_radius[elem_with_small_radius] = 0.7 #based on images
    else:
        nodes = [elems[elem_with_small_radius][1], elems[elem_with_small_radius][2]]
        #get all elements connected to the nodes
        no_of_elems = 0
        total_radius = 0
        for node in nodes:
            connected_elems = elems_at_node[node][0]

            for j in range(0,connected_elems):
                connected_elem = elems_at_node[node][j+1]
                if (connected_elem not in elem_list) or (connected_elem in updated_elem_list) :
                    no_of_elems = no_of_elems + 1
                    total_radius = total_radius + updated_radius[connected_elem]

        if no_of_elems > 0:
            updated_radius[elem_with_small_radius] = total_radius/no_of_elems
            updated_elem_list.append(elem_with_small_radius)
        else:
            updated_radius[elem_with_small_radius] = 0


version = 'cycle2_v2'


#write the radius file again

radius_info = radius_file[['mean_radius', 'shortest_radius', 'mean_as_percentage_of_shortest']].copy()
#add the radius column
new_radius_file = radius_info.assign(radius=radius,updated_radius=updated_radius)
filename = 'chorionic_vessels/element_radius_' + version + '.csv'
new_radius_file.to_csv(filename)


#assign a radius to nodes
#first element - both nodes will have the same radius as the element - for all other elements assign the element radius
#to the second node

#inlet_element = 1360 #1st run
inlet_element = 0
node_radius = np.zeros(num_nodes, dtype=float)
for i in range(0,num_elems):
    node1 =  elems[i][1]
    node2 =  elems[i][2]
    if i == inlet_element:
        node_radius[node1] = updated_radius[i]
        node_radius[node2] = updated_radius[i]
    else:
        node_radius[node2] = updated_radius[i]

node_radius_df = pd.DataFrame(
    columns=['node', 'radius'])
for node in range(0,num_nodes):
    node_radius_df.loc[node] = [node, node_radius[node]]

filename = 'chorionic_vessels/node_radius_' + version + '.csv'
node_radius_df.to_csv(filename)


#write the node radius to an ipfiel file
filename = 'chorionic_vessels/chorionic_vessel_radii'+ version + '.ipfiel'

f = open(filename, 'w')

f.write("CMISS Version 2.1  ipelem File Version 2\n")
f.write("Heading:\n")
f.write("\n")
f.write("The number of nodes is [     {0}]:      {1}\n".format(num_nodes, num_nodes))
f.write("Do you want prompting for different versions of field variable 1 [N]? Y\n")
f.write("The number of derivatives for field variable 1 is [0]: 0\n")


for n in range(0, num_nodes):
    f.write("\n")
    f.write("Node number [     {0}]:    {1}\n".format(n, n))
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
        upstream_radius = updated_radius[upstream_elem]
        element_radii.append(upstream_radius)

    no_of_downstream_elems = len(downstream_elems)
    downstream_min_radius = 0
    downstream_max_radius = 0
    if no_of_downstream_elems > 0:
        downstream_radii = []
        for j in range(0,len(downstream_elems)):
            downstream_radii.append(updated_radius[downstream_elems[j]])

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

filename = 'chorionic_vessels/element_radii_at_node_' + version + '.csv'
element_radii_at_node.to_csv(filename)