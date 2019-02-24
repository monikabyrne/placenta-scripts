#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd


def renumber_elems(first_node_idx):
    # get all elements connected to the node that we haven't seen
    global element_number
    connected_elems_no = elems_at_node[first_node_idx][0]
    for i in range(0, connected_elems_no):
        elem_idx = elems_at_node[first_node_idx][i + 1]  # elements start at column index 1
        if not seen_elements[elem_idx]:
            seen_elements[elem_idx] = True
            old_to_new_elem[elem_idx] = element_number
            element_number = element_number + 1
            second_node = elems[elem_idx][2]
            second_node_idx_result = node_loc_df.index[node_loc_df['node_no'] == second_node]
            second_node_idx = second_node_idx_result[0]
            renumber_elems(second_node_idx)
    return

#read the node file
node_loc = pg.import_exnode_tree('chorionic_vessels/chor_nodes_cycle3_v4.exnode')['nodes'][:, 0:4]
num_nodes = len(node_loc)


#read the element file
#element_file = pd.read_csv('new_elems_v4.exelem', sep="\n", header=None)
element_file = pd.read_csv('chorionic_vessels/chor_elems_cycle3_v4.exelem', sep="\n", header=None)

num_elems = (len(element_file)-31)/5
elems = np.zeros((num_elems, 3), dtype=int)

i=0
for n in range(31, len(element_file),5):
    elem_no_text = element_file[0][n].split()
    elems[i][0] = elem_no_text[1]
    i = i+1

i=0
for n in range(33, len(element_file), 5):
    nodes = element_file[0][n].split()
    elems[i][1] = int(nodes[0]) - 1 # starts at this node (-1)
    elems[i][2] = int(nodes[1]) - 1 # ends at this node (-1)
    i = i+1


#copy the node_loc array to a data frame to find indices of nodes by node number
node_loc_df = pd.DataFrame(node_loc)
node_loc_df.columns = ['node_no','x', 'y','z']
#populate the elems_at_node array listing the element indices connected to each node
elems_at_node = np.zeros((num_nodes, 10), dtype=int)
for i in range(0,num_elems):

      node1 = elems[i][1]
      node1_idx_result = node_loc_df.index[node_loc_df['node_no'] == node1]
      node1_idx = node1_idx_result[0]
      elems_at_node[node1_idx][0] = elems_at_node[node1_idx][0] + 1
      j = elems_at_node[node1_idx][0]
      #elems_at_node[elems[i][1]][j] = elems[i][0]
      elems_at_node[node1_idx][j] = i

      node2 = elems[i][2]
      node2_idx_result = node_loc_df.index[node_loc_df['node_no'] == node2]
      node2_idx = node2_idx_result[0]
      elems_at_node[node2_idx][0] = elems_at_node[node2_idx][0] + 1
      j = elems_at_node[node2_idx][0]
      #elems_at_node[elems[i][2]][j] = elems[i][0]
      elems_at_node[node2_idx][j] = i

#print elems_at_node to csv
df = pd.DataFrame(elems_at_node)
df.to_csv('elems_at_node_cycle3_v5.csv')


first_node = 1356 #inlet_node
#get node index
first_node_idx_result = node_loc_df.index[node_loc_df['node_no'] == first_node]
first_node_idx =first_node_idx_result[0]
element_number = 0
old_to_new_elem = np.zeros(num_elems, dtype=int)
seen_elements = np.zeros(num_elems, dtype=bool)

renumber_elems(first_node_idx)


#write out the new element and node files


#write the node file (it's the same as the previous version, just upversion the name)
pg.export_ex_coords(node_loc, 'chor_nodes_cycle3_v5', 'chorionic_vessels/chor_nodes_cycle3_v5b', 'exnode')


new_elems = np.zeros((num_elems, 3), dtype=int)

for i in range(0, num_elems):
    new_elem = old_to_new_elem[i]
    new_elems[new_elem][0] = new_elem
    new_elems[new_elem][1] = elems[i][1]
    new_elems[new_elem][2] = elems[i][2]


#write the new element file

pg.export_exelem_1d(new_elems, 'chor_elems_cycle3_v5', 'chorionic_vessels/chor_elems_cycle3_v5b')


#write ipelem file

filename = 'chorionic_vessels/chor_elems_cycle3_v5.ipelem'

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

filename = 'chorionic_vessels/chor_nodes_cycle3_v5.ipnode'

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
    node_num = node_loc_df['node_no'][n]
    f.write("\n")
    f.write("Node number[     {0}]:    {1}\n".format(int(node_num+1), int(node_num+1)))
    f.write("The number of versions for nj=1 is [1]:  1\n")
    f.write("The Xj(1) coordinate is [ 0.00000E+00]:    {0}\n".format(node_loc[n][1]))
    f.write("The number of versions for nj=2 is [1]:  1\n")
    f.write("The Xj(2) coordinate is [ 0.00000E+00]:    {0}\n".format(node_loc[n][2]))
    f.write("The number of versions for nj=3 is [1]:  1\n")
    f.write("The Xj(3) coordinate is [ 0.00000E+00]:    {0}\n".format(node_loc[n][3]))

f.close()



#read the radius file and write out ipfiel file again
radius_file = pd.read_csv('chorionic_vessels/chorionic_element_radii_cycle3_v1.csv')

elem_numbers = radius_file.iloc[:]['elem_numbers'].tolist()
elem_radius = radius_file.iloc[:]['updated_radius'].tolist()

total_elems = len(elem_numbers)
#write the radius file again
new_elem_radius_df = pd.DataFrame(columns=['radius'])


elems_df = pd.DataFrame(elems)
elems_df.columns = ['elem_no','node1', 'node2']
#elems_df.to_csv('elems_df.csv')


for i in range(0,total_elems):
    old_elem_no = elem_numbers[i]
    #get the index for the old element number
    elem_idx_result = elems_df.index[elems_df['elem_no'] == old_elem_no + 1]
    elem_idx = elem_idx_result[0]
    new_elem = old_to_new_elem[elem_idx]
    new_elem_radius_df.loc[new_elem] = [elem_radius[i]]


filename = 'full_tree/chorionic_element_radii_cycle3_v5.csv'
new_elem_radius_df.sort_index(inplace=True)
new_elem_radius_df.to_csv(filename)

#assign a radius to nodes
#first element - both nodes will have the same radius as the element - for all other elements assign the element radius
#to the second node
new_elem_radius = new_elem_radius_df.iloc[:]['radius'].tolist()

inlet_element = 0
node_radius = np.zeros(num_nodes, dtype=float)
for i in range(0,num_elems):
    node2 =  new_elems[i][2]
    node2_idx_result = node_loc_df.index[node_loc_df['node_no'] == node2]
    node2_idx = node2_idx_result[0]
    if i == inlet_element:
        node1 = new_elems[i][1]
        node1_idx_result = node_loc_df.index[node_loc_df['node_no'] == node1]
        node1_idx = node1_idx_result[0]

        node_radius[node1_idx] = new_elem_radius[i]
        node_radius[node2_idx] = new_elem_radius[i]
    else:
        node_radius[node2_idx] = new_elem_radius[i]

node_radius_df = pd.DataFrame(
    columns=['node', 'radius'])
for node_idx in range(0,num_nodes):
    node_num = node_loc_df['node_no'][node_idx]
    node_radius_df.loc[node_idx] = [node_num, node_radius[node_idx]]

filename = 'full_tree/chorionic_node_radii_cycle3_v5.csv'
node_radius_df.to_csv(filename)


#write the node radius to an ipfiel file
filename = 'full_tree/chorionic_element_radii_cycle3_v5.ipfiel'

f = open(filename, 'w')

f.write("CMISS Version 2.1  ipelem File Version 2\n")
f.write("Heading:\n")
f.write("\n")
f.write("The number of nodes is [     {0}]:      {1}\n".format(num_nodes, num_nodes))
f.write("Do you want prompting for different versions of field variable 1 [N]? Y\n")
f.write("The number of derivatives for field variable 1 is [0]: 0\n")


for n in range(0, num_nodes):
    node_num = node_loc_df['node_no'][n]
    f.write("\n")
    f.write("Node number [     {0}]:    {1}\n".format(int(node_num+1), int(node_num+1)))
    f.write("The number of versions for field variable 1 is [1]:  1\n")
    #use scientific notation for radius values
    f.write("The field variable 1 value is [ {0:.10e}]:  {1:.10e}\n".format(node_radius[n], node_radius[n]))

f.close()
