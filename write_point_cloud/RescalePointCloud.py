#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd
from os.path import expanduser
home = expanduser("~")

#parameters
point_cloud_in_file = home+'/placenta_patient_49/isosurfaces/p49_all_vessels_skeleton_reduced.exdata'
point_cloud_out_file = home+'/placenta_patient_49/isosurfaces/p49_all_vessels_skeleton_rescaled'
group_name = 'p49_seed_points_heterogeneous_7_12_18_rescaled'

voxel_size = 0.1165

#read the placenta surface data points file
points_file = pd.read_csv(point_cloud_in_file,sep="\n", header=None)

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
pg.export_ex_coords(points_loc,group_name,point_cloud_out_file,'exdata')