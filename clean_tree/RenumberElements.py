#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd


def renumber_elems(first_node):
    # get all elements connected to the node that we haven't seen
    global element_number
    connected_elems_no = elems_at_node[first_node][0]
    for i in range(0, connected_elems_no):
        elem = elems_at_node[first_node][i + 1]  # elements start at column index 1
        if not seen_elements[elem]:
            seen_elements[elem] = True
            old_to_new_elem[elem] = element_number
            element_number = element_number + 1
            second_node = elems[elem][2]
            renumber_elems(second_node)
    return

#read the node file
#node_file = pd.read_csv('new_nodes_v4.exnode', sep="\n", header=None)
node_file = pd.read_csv('new_nodes_v9.exnode', sep="\n", header=None)

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
#element_file = pd.read_csv('new_elems_v4.exelem', sep="\n", header=None)
element_file = pd.read_csv('new_elems_v9.exelem', sep="\n", header=None)


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

#print elems_at_node to csv
#df = pd.DataFrame(elems_at_node)
#df.to_csv('elems_at_node.csv')


first_node = 1360 #inlet_node
element_number = 0
old_to_new_elem = np.zeros(num_elems, dtype=int)
seen_elements = np.zeros(num_elems, dtype=bool)

renumber_elems(first_node)


#write out the new element and node files
version = '_v10'


#write the node file (it's the same as the previous version, just upversion the name)
name = 'new_nodes'+ version
pg.export_ex_coords(node_loc, name, name, 'exnode')



new_elems = np.zeros((num_elems, 3), dtype=int)

for i in range(0, num_elems):
    new_elem = old_to_new_elem[i]
    new_elems[new_elem][0] = new_elem
    new_elems[new_elem][1] = elems[i][1]
    new_elems[new_elem][2] = elems[i][2]


#write the new element file
name = 'new_elems'+ version
pg.export_exelem_1d(new_elems, name, name)


#write ipelem file

filename = 'new_elems_v10.ipelem'

f = open(filename, 'w')

f.write("CMISS Version 2.1  ipelem File Version 2\n")
f.write("Heading:\n")
f.write("\n")
f.write("The number of elements is [     {0}]:      {1}\n".format(num_elems, num_elems))

for n in range(0, num_elems):
    f.write("\n")
    f.write("Element number[     {0}]:    {1}\n".format(n+1, n+1))
    f.write("The number of geometric Xj-coordinates is [3]: 3\n")
    f.write("The basis function type for geometric variable 1 is [1]:  1\n")
    f.write("The basis function type for geometric variable 2 is [1]:  1\n")
    f.write("The basis function type for geometric variable 3 is [1]:  1\n")
    f.write("Enter the 2 global numbers for basis 1:     {0}     {1}\n".format(new_elems[n][1]+1, new_elems[n][2]+1))

f.close()


#write ipnode file

filename = 'new_nodes_v10.ipnode'

f = open(filename, 'w')

f.write("CMISS Version 2.1  ipelem File Version 2\n")
f.write("Heading:\n")
f.write("\n")
f.write("The number of nodes is [     {0}]:      {1}\n".format(num_nodes, num_nodes))
f.write("Number of coordinates [3]: 3\n")
f.write("Do you want prompting for different versions of nj=1 [N]? Y\n")
f.write("Do you want prompting for different versions of nj=2 [N]? Y\n")
f.write("Do you want prompting for different versions of nj=3 [N]? Y\n")
f.write("The number of derivatives for coordinate 1 is [0]: 0\n")
f.write("The number of derivatives for coordinate 2 is [0]: 0\n")
f.write("The number of derivatives for coordinate 3 is [0]: 0\n")

for n in range(0, num_nodes):
    f.write("\n")
    f.write("Node number[     {0}]:    {1}\n".format(n+1, n+1))
    f.write("The number of versions for nj=1 is [1]:  1\n")
    f.write("The Xj(1) coordinate is [ 0.00000E+00]:    {0}\n".format(node_loc[n][1]))
    f.write("The number of versions for nj=2 is [1]:  1\n")
    f.write("The Xj(2) coordinate is [ 0.00000E+00]:    {0}\n".format(node_loc[n][2]))
    f.write("The number of versions for nj=3 is [1]:  1\n")
    f.write("The Xj(3) coordinate is [ 0.00000E+00]:    {0}\n".format(node_loc[n][3]))

f.close()



#read the radius file and write out ipfiel file again
radius_file = pd.read_csv('elem_radius_large_vessels_v8.csv')


elem_radius = radius_file.iloc[:]['updated_radius'].tolist()

#write the radius file again
new_elem_radius_df = pd.DataFrame(columns=['radius'])

for i in range(0,num_elems):
    new_elem = old_to_new_elem[i]
    new_elem_radius_df.loc[new_elem] = [elem_radius[i]]


filename = 'elem_radius'+ version + '.csv'
new_elem_radius_df.sort_index(inplace=True)
new_elem_radius_df.to_csv(filename)

#assign a radius to nodes
#first element - both nodes will have the same radius as the element - for all other elements assign the element radius
#to the second node
new_elem_radius = new_elem_radius_df.iloc[:]['radius'].tolist()

inlet_element = 0
node_radius = np.zeros(num_nodes, dtype=float)
for i in range(0,num_elems):
    node1 =  new_elems[i][1]
    node2 =  new_elems[i][2]
    if i == inlet_element:
        node_radius[node1] = new_elem_radius[i]
        node_radius[node2] = new_elem_radius[i]
    else:
        node_radius[node2] = new_elem_radius[i]

node_radius_df = pd.DataFrame(
    columns=['node', 'radius'])
for node in range(0,num_nodes):
    node_radius_df.loc[node] = [node, node_radius[node]]

filename = 'node_radius_' + version + '.csv'
node_radius_df.to_csv(filename)


#write the node radius to an ipfiel file
filename = 'elem_radius'+ version + '.ipfiel'

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
    f.write("The field variable 1 value is [ {0:.10e}]:  {1:.10e}\n".format(node_radius[n], node_radius[n]))

f.close()
