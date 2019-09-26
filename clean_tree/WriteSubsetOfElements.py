#!/usr/bin/env python
 

from placenta_utilities import *
from os.path import expanduser

home = expanduser("~")

#parameters
#input and output file names
elems_in_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step4.exelem'
elem_subset_out_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step4_subset.exelem'
group_name = 'p49_large_vessels_step4_subset'

#read the element numbers with a small radius (under 5 units)
#radius_file = pd.read_csv('elements_small_radius.csv') #1st run
#radius_file = pd.read_csv('elements_sharp_radius_changes.csv')

#elem_list = radius_file.iloc[:]['element_numbers'].tolist()
elem_list = [151,201,202,861]

#read the element file
elems = import_elem_file(elems_in_file)
num_elems = len(elems)

export_elem_subset(elem_list,elems,group_name,elem_subset_out_file)



