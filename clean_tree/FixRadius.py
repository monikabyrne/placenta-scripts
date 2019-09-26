#!/usr/bin/env python

from placenta_utilities import *
from os.path import expanduser

home = expanduser("~")

#input and output file names
node_in_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step16.exnode'
elems_in_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step16.exelem'
vessel_radius_in_file = home+'/placenta_patient_49/clean_tree/large_vessel_radius_step16.csv'

radius_group_name = 'p47_chor_radii_v2'
vessel_radius_out_file = home+'/placenta_patient_49/clean_tree/large_vessel_radius_step17_v2.csv'
radius_out_file_ipfiel = home+'/placenta_patient_49/clean_tree/p49_large_vessel_radius_step17_v2.ipfiel'
radius_out_file_exelem  = home+'/placenta_patient_49/clean_tree/p49_large_vessel_radius_step17_v2'
small_radii_elems_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step16_small_radii_v2'
radius_updates_file = home+'/placenta_patient_49/clean_tree/radius_updates_step17_v2.csv'
branch_info_file = home+'/placenta_patient_49/clean_tree/branch_info_step17_v2.csv'

umbilical_artery_radius = 1.3
umbilical_artery_elems = [0,2200]
smallest_radius = 0.05 #any radii smaller than this will be updated to this value

def get_downstream_branch_elems(node,upstream_elem):

    branch_elements = []
    last_elem = -1
    connected_elems_no = elems_at_node[node][0]

    #if the node is within a branch
    if (connected_elems_no == 2):

        # for each of the elements
        for i in range(0, connected_elems_no):
            elem = elems_at_node[node][i + 1]  # elements start at column index 1
            #get the downstream element
            if (elem != upstream_elem):
                branch_elements.append(elem)
                # get the second node for the element
                temp_node1 = elems[elem][1]
                temp_node2 = elems[elem][2]
                if (node == temp_node1):
                    node2 = temp_node2
                if (node == temp_node2):
                    node2 = temp_node1
                (branch_elements2, last_elem) = get_downstream_branch_elems(node2, elem)
                if len(branch_elements2) > 1:
                    branch_elements.extend(branch_elements2)
                if len(branch_elements2) == 1:
                    branch_elements.append(branch_elements2[0])
    else:
        #if node is at a branching point or terminal
        last_elem = upstream_elem

    return branch_elements, last_elem


def get_upstream_branch_elems(node,downstream_elem):

    branch_elements = []
    first_elem = -1
    connected_elems_no = elems_at_node[node][0]

    #if the node is within a branch
    if (connected_elems_no == 2):

        # for each of the elements
        for i in range(0, connected_elems_no):
            elem = elems_at_node[node][i + 1]  # elements start at column index 1
            #get the upstream element
            if (elem != downstream_elem):
                branch_elements.append(elem)
                # get the first node for the element
                temp_node1 = elems[elem][1]
                temp_node2 = elems[elem][2]
                if (node == temp_node2):
                    node1 = temp_node1
                if (node == temp_node1):
                    node1 = temp_node2
                (branch_elements2, first_elem) = get_upstream_branch_elems(node1, elem)
                if len(branch_elements2) > 1:
                    branch_elements.extend(branch_elements2)
                if len(branch_elements2) == 1:
                    branch_elements.append(branch_elements2[0])
    else:
        #if node is at a branching point or terminal
        first_elem = downstream_elem

    return branch_elements, first_elem

#read the node file
node_loc = pg.import_exnode_tree(node_in_file)['nodes'][:, 0:4]
num_nodes = len(node_loc)

#read the element file
elems = import_elem_file(elems_in_file)
num_elems = len(elems)

#read element radius file
radius_file = pd.read_csv(vessel_radius_in_file)
radius = radius_file.iloc[:]['radius'].tolist()

#output elements with a radius of under 0.3 to check in cmgui
small_radius_elems = radius_file.index.values[(radius_file['radius'] > 0) & (radius_file['radius'] <= 0.3)]
export_elem_subset(small_radius_elems,elems,'small_radii',small_radii_elems_file)

elems_at_node = get_elements_at_a_node(node_loc,elems)

#get tree orders
tree_orders = pg.evaluate_orders(node_loc,elems)
strahler_orders = tree_orders['strahler']

updated_radius = radius[:] #creates a copy of radius

update_radius_info = radius_file[['radius']].copy()
#add the updated radius column
update_radius_info.assign(updated_radius=updated_radius)

#update radii for umbilical artery elements
for elem in umbilical_artery_elems:
    # assign a radius of 1.3 mm to umbilical cord arteries
    updated_radius[elem] = umbilical_artery_radius
    update_radius_info.at[elem,'updated_radius'] = updated_radius[elem]
    update_radius_info.at[elem,'update_type'] = 'umbilical artery'

#set radii for manually added elements
#get all elements with a radius = 0
zero_radius_elems = radius_file.index.values[radius_file['radius'] == 0]

for elem in zero_radius_elems:

    branch_radii = []
    same_order_branch_radii = []
    #get the element nodes
    node1 = elems[elem][1] #upstream node
    node2 = elems[elem][2] #downstream node
    radius_updated = False

    #if the first node is a branching point, the element is a child branch;
    # set the radius to average of downstream elements in the child branch
    if (elems_at_node[node1][0] > 2):
        branch_elems = get_downstream_branch_elems(node2,elem)[0]
        radius_updated = True

    #if the second node is a branching point, the element is a mother branch
    #  set the radius to the average of upstream elements in the mother branch
    if (elems_at_node[node2][0] > 2) and (not radius_updated):
        branch_elems = get_upstream_branch_elems(node1,elem)[0]

    #if none of the nodes are a branching point, the element is within a branch
    #set the radius to the average of upstream and downstream elements in a branch
    if (elems_at_node[node1][0] <= 2) and (elems_at_node[node2][0] <= 2):
        branch_elems = get_downstream_branch_elems(node2, elem)[0]
        upstream_branch_elems = get_upstream_branch_elems(node1,elem)[0]
        if len(upstream_branch_elems) > 1:
            branch_elems.extend(upstream_branch_elems)
        if len(upstream_branch_elems) == 1:
            branch_elems.append(upstream_branch_elems[0])

    branch_elems.sort()
    for br_elem in branch_elems:
        branch_radii.append(updated_radius[br_elem])

    if len(branch_radii) > 0:
        updated_radius[elem] = np.mean(branch_radii)
        update_radius_info.at[elem,'updated_radius'] = updated_radius[elem]
        update_radius_info.at[elem,'update_type'] = '(manually created element) new radius based on other elements in the same branch'
    else:
        #no other elements exist in the branch
        # get elements connected to elem (try the same Strahler order first) and set radius to the mean radii of these connected elements
        # make sure that the radii of connected elements > 0
        for node in (node1,node2):
            connected_elems = elems_at_node[node][0]

            for j in range(0, connected_elems):
                connected_elem = elems_at_node[node][j + 1]
                if (connected_elem != elem) and (updated_radius[connected_elem] > 0):
                    branch_radii.append(updated_radius[connected_elem])
                    if strahler_orders[elem] == strahler_orders[connected_elem]:
                        same_order_branch_radii.append(updated_radius[connected_elem])

        if len(same_order_branch_radii) > 0:
             updated_radius[elem] = np.mean(same_order_branch_radii)
             update_radius_info.at[elem, 'updated_radius'] = updated_radius[elem]
             update_radius_info.at[
                 elem, 'update_type'] = '(manually created element) new radius based on connected elements of the same Strahler order'
        elif len(branch_radii) > 0:
            updated_radius[elem] = np.mean(branch_radii)
            update_radius_info.at[elem,'updated_radius'] = updated_radius[elem]
            update_radius_info.at[elem,'update_type'] = '(manually created element) new radius based on connected elements'

#override outlier radii in a branch with mean radius for the branch

branch_info_df = pd.DataFrame(columns=['branch_start_elem', 'branch_end_elem', 'branch_elems', 'branch_radii', 'mean_radius',
                                       'std', 'outliers', 'updated_branch_radii', 'Strahler_order'])

elem_connectivity = pg.element_connectivity_1D(node_loc,elems)

elems_count_at_node = elems_at_node[:,0]
done_elem = np.zeros(num_elems)

branching_nodes = []
for i in range(0,num_nodes):
    if (elems_at_node[i][0] == 3):
        branching_nodes.append(i)

processed_elems = np.zeros(num_elems)
branch_count = 0

for br_node in branching_nodes:

    #get all elements connected to the branching node
    connected_elems = elems_at_node[node][0]

    for j in range(0, connected_elems):
        connected_elem = elems_at_node[br_node][j + 1]
        # if connected element hasn't already been processed
        if not processed_elems[connected_elem]:
            #is node the first or second node of the element?
            #if it's the first node, get the remaining downstream elements in the branch
            node1 = elems[connected_elem][1]  # upstream node
            node2 = elems[connected_elem][2]  # downstream node
            branch_elems = []
            first_elem = -1
            last_elem = -1
            if br_node == node1:
                (branch_elems, last_elem) = get_downstream_branch_elems(node2, connected_elem)
                if len(branch_elems) == 0:
                    last_elem = connected_elem
                first_elem = connected_elem
            if br_node == node2:
                (branch_elems, first_elem) = get_upstream_branch_elems(node1, connected_elem)
                if len(branch_elems) == 0:
                    first_elem = connected_elem
                last_elem = connected_elem
            #add current element to the branch and sort
            branch_elems.append(connected_elem)
            branch_elems.sort()
            branch_radii = []
            updated_branch_radii = []
            outliers = []
            for br_elem in branch_elems:
                processed_elems[br_elem] = True
                branch_radii.append(round(updated_radius[br_elem],2))
            mean_radius = np.mean(branch_radii)
            std = 0

            # calculate which radii are 1 standard deviation from the mean and override those with mean radius for the branch
            if len(branch_elems) > 2:
                std = np.std(branch_radii)
                for br_elem in branch_elems:
                    br_elem_radius = updated_radius[br_elem]
                    if (br_elem_radius > mean_radius + std) or (br_elem_radius < mean_radius - std):
                        outliers.append(round(br_elem_radius,2))
                        updated_radius[br_elem] = mean_radius
                        update_radius_info.at[br_elem, 'updated_radius'] = updated_radius[br_elem]
                        update_radius_info.at[
                            br_elem, 'update_type'] = 'set outlier radius to mean radius for branch'
                for br_elem in branch_elems:
                    updated_branch_radii.append(round(updated_radius[br_elem], 2))

            branch_info_df.loc[branch_count] = [first_elem, last_elem, branch_elems, branch_radii,
                                                mean_radius, std, outliers, updated_branch_radii, strahler_orders[connected_elem]]
            branch_count = branch_count + 1


#override radii for elements with a radius smaller than the allowed smallest_radius
for elem in range(0,num_elems):
    if updated_radius[elem] < smallest_radius:
        updated_radius[elem] = smallest_radius
        update_radius_info.at[elem, 'updated_radius'] = updated_radius[elem]
        update_radius_info.at[
        elem, 'update_type'] = 'radius smaller than allowed, updating to smallest allowed radius of '+ str(smallest_radius)

# print warning if elements without a radius exist
zero_radius = [i for i, radius in enumerate(updated_radius) if radius == 0]
if len(zero_radius) > 0:
    print 'Warning, elements without a radius still exist'
    print zero_radius

#write the radius file again as csv, exelem and ipfiel
updated_radii_df = pd.DataFrame(updated_radius)
updated_radii_df.columns = ['radius']
updated_radii_df.to_csv(vessel_radius_out_file)

export_solution_2(updated_radius, radius_group_name, radius_out_file_exelem, 'radius')
write_radius_as_ipfiel(node_loc,elems, updated_radius, radius_out_file_ipfiel)

#export information explaining radius updates
update_radius_info.to_csv(radius_updates_file)

#export branch info
branch_info_df.to_csv(branch_info_file)