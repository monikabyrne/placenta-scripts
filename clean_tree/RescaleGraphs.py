#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd


#read the node file
node_file = pd.read_csv('small_vessels/sv_nodes_v1.exnode', sep="\n", header=None)

num_nodes = (len(node_file) - 6)/4
node_loc = np.zeros((num_nodes, 4))

i=0
for n in range(7,len(node_file),4):
    node_loc[i][0] = i
    node_loc[i][1] = node_file[0][n]
    node_loc[i][1] = node_loc[i][1] * 0.1165
    i=i+1

i=0
for n in range(8,len(node_file),4):
    node_loc[i][2] = node_file[0][n]
    node_loc[i][2] = node_loc[i][2] * 0.1165
    i=i+1

i=0
for n in range(9,len(node_file),4):
    node_loc[i][3] = node_file[0][n]
    node_loc[i][3] = node_loc[i][3] * 0.1165
    i=i+1

#write the new node file
pg.export_ex_coords(node_loc, 'sv_nodes_v2', 'sv_nodes_v2','exnode')

#read the element file
element_file = pd.read_csv('small_vessels/sv_elems_v1.exelem', sep="\n", header=None)

num_elems = (len(element_file)-31)/5
elems = np.zeros((num_elems, 3), dtype=int)

i=0
for n in range(33, len(element_file),5):
    elems[i][0] = i  # creating new element
    nodes = element_file[0][n].split()
    elems[i][1] = int(nodes[0]) - 1 # starts at this node (-1)
    elems[i][2] = int(nodes[1]) - 1 # ends at this node (-1)
    i = i+1

# write the exelem file - no changes for elements, just increment the version number
pg.export_exelem_1d(elems, 'sv_elems_v2', 'sv_elems_v2')


#read the vessel surface data points file
points_file = pd.read_csv('large_vessels.exdata',sep="\n", header=None)

num_points = (len(points_file) - 6)/4
points_loc = np.zeros((num_points, 4))

i=0
for n in range(7,len(points_file),4):
    points_loc[i][0] = i
    points_loc[i][1] = points_file[0][n]
    points_loc[i][1] = points_loc[i][1] * 0.1165
    i=i+1

i=0
for n in range(8,len(points_file),4):
    points_loc[i][2] = points_file[0][n]
    points_loc[i][2] = points_loc[i][2] * 0.1165
    i=i+1

i=0
for n in range(9,len(points_file),4):
    points_loc[i][3] = points_file[0][n]
    points_loc[i][3] = points_loc[i][3] * 0.1165
    i=i+1

#write the exdata file (this can only be used if points_loc has the node number stored in the first column
pg.export_ex_coords(points_loc,'large_vessel_surface_v2','large_vessel_surface_v2','exdata')


#write ipelem file

filename = 'new_elems_v9.ipelem'

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
    f.write("Enter the 2 global numbers for basis 1:     {0}     {1}\n".format(elems[n][1]+1, elems[n][2]+1))

f.close()


#write ipnode file

filename = 'new_nodes_v9.ipnode'

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
