#!/usr/bin/env python


from placenta_utilities import *
from os.path import expanduser

home = expanduser("~")

#parameters
#input and output file names
node_in_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step16.exnode'
elems_in_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step16.exelem'
vessel_radius_in_file = home+'/placenta_patient_49/clean_tree/large_vessel_radius_step16.csv'

radius_group_name = 'p49_chor_radii'
vessel_radius_out_file = home+'/placenta_patient_49/clean_tree/p49_large_vessel_radius_step16'
strahler_group_name = 'p49_chor_strahler'
strahler_out_file = home+'/placenta_patient_49/clean_tree/p49_large_vessel_strahler'
gen_group_name = 'p49_chor_generation'
gen_out_file = home+'/placenta_patient_49/clean_tree/p49_large_vessel_generation'

#read the radius file and write out exelem file with the radius
radius_file = pd.read_csv(vessel_radius_in_file)
elem_radius = radius_file.iloc[:]['radius'].tolist()
export_solution_2(elem_radius, radius_group_name, vessel_radius_out_file, 'radius')


#output Strahler orders as exelem

full_geom = {}
full_geom['nodes'] = pg.import_exnode_tree(node_in_file)['nodes'][:, 0:4]
full_geom['elems'] = pg.import_exelem_tree(elems_in_file)['elems']

tree_orders = pg.evaluate_orders(full_geom['nodes'],full_geom['elems'])
export_solution_2(tree_orders['strahler'], strahler_group_name, strahler_out_file, 'strahler_order')
export_solution_2(tree_orders['generation'], gen_group_name, gen_out_file, 'generation')

print 'max_strahler', max(tree_orders['strahler'])
print 'max_generation', max(tree_orders['generation'])