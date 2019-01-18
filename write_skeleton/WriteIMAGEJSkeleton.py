#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd


branch_info = pd.read_csv('no_pruning_of_loops_branch_info_large_vessels.csv')

node_coordinates_v1 = branch_info[['V1 x', 'V1 y', 'V1 z']].copy()
node_coordinates_v1.columns = ['x', 'y','z']
total_rows = len(node_coordinates_v1)
node_coordinates_v2 = branch_info[['V2 x', 'V2 y', 'V2 z']].copy()
node_coordinates_v2.columns = ['x', 'y','z']
#update indices so that we can join the 2 dataframes
node_coordinates_v2.index = range(total_rows,total_rows*2)
node_coordinates_combined = [node_coordinates_v1, node_coordinates_v2]
node_coordinates = pd.concat(node_coordinates_combined)
unique_nodes = node_coordinates.drop_duplicates()
num_nodes = len(unique_nodes)
nodes = unique_nodes.sort_values(['x', 'y','z'],inplace=True)
#update indices in the sorted dataframe
nodes.index = range(0,num_nodes)

#populate nodes array
node_loc = np.zeros((num_nodes, 4))
for i in range(0,num_nodes):
    node_loc[i][0] = i
    node_loc[i][1] = nodes.iloc[i]['x']
    node_loc[i][2] = nodes.iloc[i]['y']
    node_loc[i][3] = nodes.iloc[i]['z']

#write the exnode file
pg.export_ex_coords(node_loc,'p51_large_vessels_v2','p51_large_vessels_v2','exnode')


#populate elems array
num_elems = len(branch_info)
elems = np.zeros((num_elems, 3), dtype=int)

for i in range(0,num_elems):
    #get indices for node 1 and 2
    node1_index = nodes.index[
        (nodes['x'] == branch_info.iloc[i]['V1 x']) & (nodes['y'] == branch_info.iloc[i]['V1 y']) & (
            nodes['z'] == branch_info.iloc[i]['V1 z'])]
    node2_index = nodes.index[
        (nodes['x'] == branch_info.iloc[i]['V2 x']) & (nodes['y'] == branch_info.iloc[i]['V2 y']) & (
            nodes['z'] == branch_info.iloc[i]['V2 z'])]

    elems[i][0] = i  # creating new element
    elems[i][1] = node1_index[0] # starts at this node (using node index so don't need to take away 1)
    elems[i][2] = node2_index[0] # ends at this node


#write the exelem file
pg.export_exelem_1d(elems,'p51_large_vessels_v2','p51_large_vessels_v2')
 

