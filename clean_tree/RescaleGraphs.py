#!/usr/bin/env python

from placenta_utilities import *


voxel_size = 0.1165


#read the node file
node_loc = pg.import_exnode_tree('small_vessels/sv_nodes_v1.exnode')['nodes'][:, 0:4]
num_nodes = len(node_loc)

#rescale node coordinates - multiply by voxel size
for i in range(0,num_nodes):
    for n in range(1,4):
        node_loc[i][n] = node_loc[i][n] * voxel_size


#write the new node file
pg.export_ex_coords(node_loc, 'sv_nodes_v2', 'sv_nodes_v2','exnode')

#read the element file
elems = import_elem_file('small_vessels/sv_elems_v1.exelem')
num_elems = len(elems)

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
    points_loc[i][1] = points_loc[i][1] * voxel_size
    i=i+1

i=0
for n in range(8,len(points_file),4):
    points_loc[i][2] = points_file[0][n]
    points_loc[i][2] = points_loc[i][2] * voxel_size
    i=i+1

i=0
for n in range(9,len(points_file),4):
    points_loc[i][3] = points_file[0][n]
    points_loc[i][3] = points_loc[i][3] * voxel_size
    i=i+1

#write the exdata file (this can only be used if points_loc has the node number stored in the first column
pg.export_ex_coords(points_loc,'large_vessel_surface_v2','large_vessel_surface_v2','exdata')


#write ipelem file
filename = 'new_elems_v9.ipelem'
write_ipelem(elems,filename)

#write ipnode file
filename = 'new_nodes_v9.ipnode'
write_ipnode(node_loc, filename)

