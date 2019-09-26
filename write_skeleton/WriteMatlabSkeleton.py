#!/usr/bin/env python
 

import placentagen as pg
import numpy as np
import pandas as pd
from os.path import expanduser
home = expanduser("~")

#input and output file names
node_in_file = home+'/placenta_patient_49/matlab_skeleton_graph/nodes_large_vessels.csv'
elems_in_file = home+'/placenta_patient_49/matlab_skeleton_graph/elements_large_vessels.csv'
node_out_file = home+'/placenta_patient_49/matlab_skeleton_graph/p49_skeleton_large_vessels'
elems_out_file = home+'/placenta_patient_49/matlab_skeleton_graph/p49_skeleton_large_vessels'
group_name = 'p49_skeleton_large_vessels'

node_info = pd.read_csv(node_in_file)

nodes = node_info[['comx', 'comy', 'comz']].copy()
nodes.columns = ['y', 'x','z'] #swap x and y coordinates, so that they're the same as imagej skeleton
num_nodes = len(nodes)

#populate nodes array
node_loc = np.zeros((num_nodes, 4))
for i in range(0,num_nodes):
    node_loc[i][0] = i
    node_loc[i][1] = nodes.iloc[i]['x']
    node_loc[i][2] = nodes.iloc[i]['y']
    node_loc[i][3] = nodes.iloc[i]['z']

#write the exnode file
pg.export_ex_coords(node_loc,group_name,node_out_file,'exnode')

#populate elems array
element_info = pd.read_csv(elems_in_file)
elements = element_info[['n1','n2']].copy()
elements.columns = ['n1', 'n2']
num_elems = len(elements)

elems = np.zeros((num_elems, 3), dtype=int)

for i in range(0,num_elems):
    elems[i][0] = i  # creating new element;
    #export_exelem_1d adds 1 to all values
    elems[i][1] = elements.iloc[i]['n1'] -1  # starts at this node
    elems[i][2] = elements.iloc[i]['n2'] -1  # ends at this node

#write the exelem file
pg.export_exelem_1d(elems,group_name,elems_out_file)
 

