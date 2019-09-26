#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd
from os.path import expanduser
home = expanduser("~")

#parameters
point_cloud_in_file = home+'/placenta_patient_49/seed_points/p49_seed_points_heterogeneous_5_10_17.txt'
point_cloud_out_file = home+'/placenta_patient_49/seed_points/p49_seed_points_heterogeneous_5_10_17'
group_name = 'p49_seed_points_heterogeneous_5_10_17'

point_cloud = pd.read_csv(point_cloud_in_file,sep="\t", header=None)
point_cloud.columns = ['x','y','z']
num_nodes = len(point_cloud)

#populate nodes array
node_loc = np.zeros((num_nodes, 4))
for i in range(0,num_nodes):
    node_loc[i][0] = i
    node_loc[i][1] = point_cloud.iloc[i]['x']
    node_loc[i][2] = point_cloud.iloc[i]['y']
    node_loc[i][3] = point_cloud.iloc[i]['z']

#write the exnode file
pg.export_ex_coords(node_loc,group_name,point_cloud_out_file,'exdata')

