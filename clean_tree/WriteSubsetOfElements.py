#!/usr/bin/env python
 

from placenta_utilities import *
from os.path import expanduser

home = expanduser("~")

#parameters
#input and output file names
elems_in_file = home+'/placenta_patient_49/growing/het_27k/full_tree.exelem'
elem_subset_out_file = home+'/placenta_patient_49/growing/het_27k/full_tree_Strahler_0'
group_name = 'p49_het27k_Strahler_0'

#read the element numbers with a small radius (under 5 units)
#radius_file = pd.read_csv('elements_small_radius.csv') #1st run
#radius_file = pd.read_csv('elements_sharp_radius_changes.csv')

#elem_list = radius_file.iloc[:]['element_numbers'].tolist()
elem_list = [3328,3329,3330,3331,3332,3333,3334,3335,3336,4237,4238,
             4986,4987,4988,4989,4990,4991,4992,4993,4994,4995,4996,4997,4998,4999,5000,5001,5002]


#read the element file
elems = import_elem_file(elems_in_file)
num_elems = len(elems)

export_elem_subset(elem_list,elems,group_name,elem_subset_out_file)



