#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd
from os.path import expanduser
home = expanduser("~")

#parameters
point_cloud_in_file = home+'/placenta_patient_49/seed_points/p49_seed_points_uniform_every_10_units.txt'
point_cloud_out_file = home+'/placenta_patient_49/seed_points/p49_seed_points_uniform_10_step_9'
group_name = 'p49_seed_points_uniform_10_step_9'

#reduce the number of seed points - keep only every nth point
step = 9

point_cloud = pd.read_csv(point_cloud_in_file,sep="\t", header=None)
point_cloud.columns = ['x','y','z']
num_nodes = len(point_cloud)
print num_nodes
#populate nodes array
#keep every 10th line (for small vessels every 100th line)
node_loc_reduced = np.zeros(((num_nodes/step)+1, 4))
j=0
for i in range(0,num_nodes,step):
    node_loc_reduced[j][0] = j
    node_loc_reduced[j][1] = point_cloud.iloc[i]['x']
    node_loc_reduced[j][2] = point_cloud.iloc[i]['y']
    node_loc_reduced[j][3] = point_cloud.iloc[i]['z']
    j = j + 1


print 'Number of points in exdata file: ', j
#write the exnode file
pg.export_ex_coords(node_loc_reduced,group_name,point_cloud_out_file,'exdata')

