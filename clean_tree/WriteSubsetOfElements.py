#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd

#read the element numbers with a small radius (under 5 units)
#radius_file = pd.read_csv('elements_small_radius.csv') #1st run
#radius_file = pd.read_csv('elements_sharp_radius_changes.csv')

#elem_list = radius_file.iloc[:]['element_numbers'].tolist()
elem_list = [151,201,202,861]
elem_list.sort()

#read the element file
element_file = pd.read_csv('new_elems_v8.exelem', sep="\n", header=None)

num_elems = (len(element_file)-31)/5
elems = np.zeros((num_elems, 3), dtype=int)

i=0
for n in range(33, len(element_file),5):
    elems[i][0] = i  # creating new element
    nodes = element_file[0][n].split()
    elems[i][1] = int(nodes[0]) - 1 # starts at this node (-1)
    elems[i][2] = int(nodes[1]) - 1 # ends at this node (-1)
    i = i+1

# write the exelem file
#pg.export_exelem_1d(elems, 'test_elems', 'test_elems')

subset_of_elems = np.zeros((len(elem_list), 3), dtype=int)
i = 0
for short_radius_elem in elem_list:
    subset_of_elems[i][0] = elems[short_radius_elem][0]
    subset_of_elems[i][1] = elems[short_radius_elem][1]
    subset_of_elems[i][2] = elems[short_radius_elem][2]
    i = i + 1


version = '_v1'

#write the new element file
#name = 'elems_with_short_radius'+ version #1st run
name = 'subset_of_elems'+ version
pg.export_exelem_1d(subset_of_elems, name, name)

