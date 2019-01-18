#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd

#read the placenta surface data points file
points_file = pd.read_csv('small_vessels.exdata',sep="\n", header=None)

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
pg.export_ex_coords(points_loc,'small_vessel_surface_rescaled','small_vessel_surface_rescaled','exdata')