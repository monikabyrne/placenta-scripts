#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd

point_cloud = pd.read_csv('all_vessels_skeleton.txt',sep="\t", header=None)
point_cloud.columns = ['x','y','z']
num_nodes = len(point_cloud)
print num_nodes
#populate nodes array
#keep every 10th line (for small vessels every 100th line)
node_loc_reduced = np.zeros(((num_nodes/10)+1, 4))
j=0
for i in range(0,num_nodes,10):
    print j
    node_loc_reduced[j][0] = j
    node_loc_reduced[j][1] = point_cloud.iloc[i]['x']
    node_loc_reduced[j][2] = point_cloud.iloc[i]['y']
    node_loc_reduced[j][3] = point_cloud.iloc[i]['z']
    j = j + 1

#write the exnode file
pg.export_ex_coords(node_loc_reduced,'all_vessels_skeleton_reduced','all_vessels_skeleton_reduced','exdata')

