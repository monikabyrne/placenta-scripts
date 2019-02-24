#!/usr/bin/env python


from get_radii_stats import *

#Parameters

path = 'full_tree_avg_13'
#path = 'test_tree'
#path = 'chorionic_tree_reprosim_results'

#chorionic_elements = 1427
#chorionic_elements = 3
chorionic_elements = 0

#node and element file names, if not given full_tree.exnode and arterial_tree.exelem is used
node_file = 'full_tree.exnode'
elem_file = 'arterial_tree.exelem'
#node_file = 'chorionic_tree.exnode'
#elem_file = 'chorionic_tree.exelem'


print('path = ' + path)

full_geom = {}
full_geom['nodes'] = pg.import_exnode_tree(path + '/' + node_file)['nodes'][:, 0:4]
num_nodes = len(full_geom['nodes'])
print ('num nodes = ' + str(num_nodes))
full_geom['elems'] = pg.import_exelem_tree(path + '/' + elem_file)['elems']
num_elems = len(full_geom['elems'])
print ('num elems = ' + str(num_elems))

tree_orders = pg.evaluate_orders(full_geom['nodes'], full_geom['elems'])
strahler_orders = tree_orders['strahler']
generations = tree_orders['generation']
print('max strahler order = ' + str(max(strahler_orders)))
print('max horsfield order = ' + str(max(tree_orders['horsfield'])))
print('max generations = ' + str(max(generations)))

# get element connectivity to count the number of non-branching elements in the chorionic tree
# get second nodes for chorionic elements -  add to count if number of connected elements is less than three
max_strahler = max(strahler_orders)
elem_connectivity = pg.element_connectivity_1D(full_geom['nodes'], full_geom['elems'])

#element diameters
elem_radii = import_elem_radius(path + '/radius_perf.exelem')
elem_diameter = elem_radii * 2


lengths = get_elem_length(full_geom['nodes'], full_geom['elems'])
total_length = sum(lengths) / 1000  # length in meters
print('Total length of vasculature (m) = ' + str(total_length))
#df = pd.DataFrame(lengths)
#df.to_csv('lengths.csv')

(branch_lengths,branch_diameters,branch_start_end_elems) = \
    get_branch_lengths_and_diameters(full_geom['nodes'], full_geom['elems'],elem_connectivity,lengths,elem_diameter,path)

branching_angles = get_branching_angles(full_geom['nodes'], full_geom['elems'], elem_connectivity,branch_start_end_elems)

#major and minor branches
(major_minor) = get_major_and_minor_branches(num_elems,elem_connectivity,branch_diameters,branch_start_end_elems)

#length ratios are stored for daughter branches only (against the last element in the branch)
(length_ratios,length_to_diameter_ratios,diameter_ratios) = \
    get_length_and_diameter_ratios(branch_lengths,branch_diameters,branch_start_end_elems, elem_connectivity,path)



# create a dataframe with element Strahler orders, lengths, angles etc
elem_info_df = pd.DataFrame(columns=['Strahler order','major_minor','branch_length','branch_diameter',
                                     'length_ratio', 'diameter_ratio','length_to_diameter_ratio',
                                     'branching_angle'])

elem_info_df['Strahler order'] = strahler_orders
elem_info_df['major_minor'] = major_minor
elem_info_df['branch_length'] = branch_lengths
elem_info_df['branch_diameter'] = branch_diameters
elem_info_df['length_ratio'] = length_ratios
elem_info_df['diameter_ratio'] = diameter_ratios
elem_info_df['length_to_diameter_ratio'] = length_to_diameter_ratios
elem_info_df['branching_angle'] = branching_angles

elem_info_df.to_csv(path +'/element_info.csv')

if chorionic_elements > 0:
    # chorionic elements
    chorionic_elems_df = elem_info_df.iloc[0:chorionic_elements]
    # chorionic_elems_df.to_csv('chorionic_elemens.csv')

    # IVS elements
    ivs_elems_df = elem_info_df.iloc[chorionic_elements:]
    # ivs_elems_df.to_csv('ivs_elems.csv')


# branch properties by Strahler order

branch_types = ['all', 'major', 'minor']

for bt in range(0,3):
    branch_type = branch_types[bt]
    filename = path + '/' + branch_type+ '_branch_stats_by_Strahler_order.csv'
    print 'Saving element stats by Strahler order for all elements in file ' + filename
    elem_stats_by_strahler(elem_info_df,filename,branch_type)

    if chorionic_elements > 0:
        filename = path + '/' + branch_type + '_chorionic_branch_stats_by_Strahler_order.csv'
        print 'Saving element stats by Strahler order for chorionic elements in file ' + filename
        elem_stats_by_strahler(chorionic_elems_df,filename,branch_type)

        filename = path + '/' + branch_type + '_IVS_branch_stats_by_Strahler_order.csv'
        print 'Saving element stats by Strahler order for IVS elements in file ' + filename
        elem_stats_by_strahler(ivs_elems_df,filename,branch_type)



print_parent_and_daughter_diameters(num_elems,elem_connectivity,branch_diameters,
                                        branch_start_end_elems,major_minor,path)