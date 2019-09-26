#!/usr/bin/env python
 
from placenta_utilities import *
from os.path import expanduser

home = expanduser("~")

#parameters
#input and output file names
node_in_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step13.exnode'
elems_in_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step13.exelem'
vessel_radius_in_file = home+'/placenta_patient_49/clean_tree/large_vessel_radius_step13.csv'

mult_br_node_out_file = home+'/placenta_patient_49/clean_tree/p49_multiple_branching_nodes_step13'
mult_br_group_name = 'multiple_branching_nodes_step13'

node_out_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step14'
elems_out_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step14'
vessel_radius_out_file = home+'/placenta_patient_49/clean_tree/large_vessel_radius_step14.csv'
group_name = 'p49_large_vessels_step14'
multiple_branches_file = home+'/placenta_patient_49/clean_tree/p49_step14_multiple_branches.csv'

use_radius = False #if set to False the longest element will be split to accommodate additional branching points
                   #if set to True the thickest element will be split
dummy_elem_length_param = 0.1


#read the node file
node_loc = pg.import_exnode_tree(node_in_file)['nodes'][:, 0:4]
num_nodes = len(node_loc)

#read the element file
elems = import_elem_file(elems_in_file)
num_elems = len(elems)

elems_at_node = get_elements_at_a_node(node_loc,elems)

#get branching nodes with more than 3 elements
multiple_branches = []
for i in range(0,num_nodes):
    if (elems_at_node[i][0] > 3):
        multiple_branches.append(i)

export_node_subset(multiple_branches, node_loc, mult_br_group_name, mult_br_node_out_file)

#calculate element lengths
elem_length = get_elem_length(node_loc, elems)

#get element radii
radius_file = pd.read_csv(vessel_radius_in_file)
elem_radius = radius_file.iloc[:]['radius'].tolist()

#export element length and radius at each multiple branching node

multiple_branches_df = pd.DataFrame(columns=['branching_node', 'element', 'element_radius', 'element_length'])

i = 0
for node in multiple_branches:
    connected_elems_no = elems_at_node[node][0]

    for j in range(0,connected_elems_no):
        elem = elems_at_node[node][j + 1]  # elements start at column index 1
        multiple_branches_df.loc[i] = [node, elem, elem_radius[elem],elem_length[elem]]
        i = i + 1


if use_radius:
    multiple_branches_df.sort_values(['branching_node', 'element_radius'],inplace=True)
else:
    multiple_branches_df.sort_values(['branching_node', 'element_length'], inplace=True)

#update indices in the sorted dataframe
multiple_branches_df.reset_index(inplace=True)
multiple_branches_df.drop('index', axis=1, inplace=True) #need to drop the old index column
multiple_branches_df.to_csv(multiple_branches_file)

print 'multiple_branches', multiple_branches

for node in multiple_branches:

    if use_radius:
        #get the element with the biggest radius
        elem_to_split = int(multiple_branches_df.iloc[multiple_branches_df.loc[multiple_branches_df['branching_node']
                                            == node]['element_radius'].idxmax()]['element'])
    else:
        #get the longest element
        elem_to_split = int(multiple_branches_df.iloc[multiple_branches_df.loc[multiple_branches_df['branching_node']
                                                        == node]['element_length'].idxmax()]['element'])
    print 'node', node, 'elem_to_split', elem_to_split

    # how many extra elements do we have (we can only have 2 branches = up to 3 elements) = extra_elems
    extra_elem_no = connected_elems_no = elems_at_node[node][0] - 3
    print 'extra_elems', extra_elem_no

    if use_radius:
        #get extra elements with the smallest radii
        extra_elems_df = multiple_branches_df.loc[multiple_branches_df['branching_node']
                                                             == node].head(extra_elem_no).copy()
    else:
        #get extra elements with the shortest length
        extra_elems_df = multiple_branches_df.loc[multiple_branches_df['branching_node']
                                                             == node].head(extra_elem_no).copy()
    print extra_elems_df
    extra_elems = extra_elems_df.iloc[:]['element'].tolist()

    if node != elems[elem_to_split][1]:
        # update direction for the element that will be split - from branching node to the other node
        elems[elem_to_split][2] = elems[elem_to_split][1]
        elems[elem_to_split][1] = node

    #split the element into shorter elements so that the branching points for extra elements can be moved
    elem_to_split_len = elem_length[elem_to_split]

    #check if element is long enough to accommodate splitting into multiple elements with dummy_elem_length
    if elem_to_split_len > dummy_elem_length_param * extra_elem_no:
        dummy_elem_length = dummy_elem_length_param
    else:
        dummy_elem_length = elem_to_split_len/(extra_elem_no + 1) - 0.01

    print 'dummy_elem_length',dummy_elem_length

    for extra_elem in extra_elems:

        extra_elem = int(extra_elem)

        # create a new node on the thickest element
        (x, y, z) = split_element_xyz(elem_to_split, node_loc, elems, dummy_elem_length)
        new_node = len(node_loc)
        node_loc = np.vstack([node_loc, [new_node, x, y, z]])

        # create a new element that starts with node 1 of elem_to_split and ends with the new node
        i = len(elems)
        elems = np.vstack([elems, [i, elems[elem_to_split][1], new_node]])

        radius_file.loc[i] = radius_file.loc[elem_to_split]

        #elem_radius.append(elem_radius[elem_to_split])  # copy radius from the first element

        # update the first node of the element to split to the new node
        elems[elem_to_split][1] = new_node

        #update the branching node for extra element to the new node
        if node == elems[extra_elem][1]:
            elems[extra_elem][1] = new_node
        else:
            elems[extra_elem][2] = new_node

# write the new node file
pg.export_ex_coords(node_loc, group_name, node_out_file, 'exnode')

#write the new element file
pg.export_exelem_1d(elems, group_name, elems_out_file)


#export the vessel radius file
radius_file.drop(radius_file.columns[0], axis=1, inplace=True) #need to drop the old index column
radius_file.to_csv(vessel_radius_out_file)

