#!/usr/bin/env python
 
from placenta_utilities import *
from os.path import expanduser

#gets the total length of all generations of branches connected to the node, nodes and elements in all generations
#and nodes that have already been seen until a length threshold is reached
def get_branch_length(node,upstream_elem,total_length,length_threshold):

    br_nodes = []
    br_elems = []
    short_branch = False
    branching_node = -1
    connected_elems_no = elems_at_node[node][0]
    #if the node is terminal
    if(connected_elems_no == 1):
        br_nodes.append(node)
        short_branch = False #this is a short disconnected branch - do not remove it (use RemoveDisconnectedBranches.py)

    #if the node is within a branch
    elif (connected_elems_no == 2):
        br_nodes.append(node)
        # for each of the elements
        for i in range(0, connected_elems_no):
            elem = elems_at_node[node][i + 1]  # elements start at column index 1
            if (elem != upstream_elem):
                # add length of the current element
                total_length = total_length + elem_length[elem]
                if (total_length < length_threshold):
                    br_elems.append(elem)
                    # get the second node for the element
                    temp_node1 = elems[elem][1]
                    temp_node2 = elems[elem][2]
                    if (node == temp_node1):
                        node2 = temp_node2
                    if (node == temp_node2):
                        node2 = temp_node1
                    branch_part_info = get_branch_length(node2, elem, total_length, length_threshold)
                    total_length = branch_part_info['length']
                    short_branch = branch_part_info['short_branch']
                    branching_node = branch_part_info['branching_node']
                    br_elems.extend(branch_part_info['br_elems'])
                    br_nodes.extend(branch_part_info['br_nodes'])
                else:
                    short_branch = False

    #if it's a branching node
    else:
        short_branch = True
        branching_node = node

    branch_info = {}
    branch_info['length'] = total_length
    branch_info['short_branch'] = short_branch
    branch_info['branching_node'] = branching_node
    branch_info['br_elems'] = br_elems
    branch_info['br_nodes'] = br_nodes

    return branch_info

home = expanduser("~")

#parameters
#input and output file names
node_in_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step8.exnode'
elems_in_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step8.exelem'
vessel_radius_in_file = home+'/placenta_patient_49/clean_tree/large_vessel_radius_step8.csv'
elems_to_remove_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step8_removed'
node_out_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step9'
elems_out_file = home+'/placenta_patient_49/clean_tree/p49_large_vessels_step9'

vessel_radius_out_file = home+'/placenta_patient_49/clean_tree/large_vessel_radius_step9.csv'
group_name = 'p49_large_vessels_step9'
branch_df_out_file = home+'/placenta_patient_49/clean_tree/step9_branch_df.csv'
short_thin_branches_df_out_file = home+'/placenta_patient_49/clean_tree/step9_short_thin_branches_df.csv'

#terminal branches shorter than the length threshold and with a smaller caliber will be removed
length_threshold = 1
radius_threshold = 5


#read the node file
node_loc = pg.import_exnode_tree(node_in_file)['nodes'][:, 0:4]
num_nodes = len(node_loc)

#read the element file
elems = import_elem_file(elems_in_file)
num_elems = len(elems)

#calculate element lengths
elem_length = get_elem_length(node_loc, elems)

elems_at_node = get_elements_at_a_node(node_loc,elems)

radius_file = pd.read_csv(vessel_radius_in_file)
elem_radius = radius_file.iloc[:]['radius'].tolist()

#branching nodes - nodes that have more than 2 elements connected to them
branching_nodes = []
for i in range(0,num_nodes):
    if (elems_at_node[i][0] > 2):
        branching_nodes.append(i)
#terminal nodes have only one element connected to them
end_nodes = []
for i in range(0,num_nodes):
    if (elems_at_node[i][0] == 1):
        end_nodes.append(i)

branch_df = pd.DataFrame(columns=['branching_node','elems','nodes','length'])

# for each terminal node
# calculate the length of the branch up to the point when a branching node is encountered
# flag the nodes and elements (apart from the branching node) of a short branch for deletion
for node in end_nodes:

    short_branch = False
    br_nodes = []
    br_nodes.append(node)
    elem = elems_at_node[node][1]
    br_elems = []
    # add length of the current element
    total_length = elem_length[elem]
    if (total_length < length_threshold):
        br_elems.append(elem)
        # get the second node for that element
        temp_node1 = elems[elem][1]
        temp_node2 = elems[elem][2]
        if (node == temp_node1):
            node2 = temp_node2
        if (node == temp_node2):
            node2 = temp_node1
        branch_info = get_branch_length(node2,elem,total_length,length_threshold)
        total_length = branch_info['length']
        short_branch = branch_info['short_branch']
        if ((total_length < length_threshold) & short_branch):
            br_elems.extend(branch_info['br_elems'])
            br_nodes.extend(branch_info['br_nodes'])
            branch_df.loc[len(branch_df)] = [branch_info['branching_node'], br_elems, br_nodes, total_length]


#calculate the minimum radius of each branch - branches with a radius below the threshold will be deleted
branch_df.assign(min_radius=np.zeros(len(branch_df)))
for i in range(0,len(branch_df)):
    total_radius = 0
    branch_elems = branch_df.iloc[i]['elems']
    radii = []
    for j in range(0,len(branch_elems)):
        #total_radius = total_radius + elem_radius[branch_elems[j]]
        radii.append(elem_radius[branch_elems[j]])
    #branch_df.at[i, 'avg_radius'] = total_radius/len(branch_elems)
    branch_df.at[i, 'min_radius'] = np.min(radii)

branch_df.to_csv(branch_df_out_file)

#leave only thin branches
thin_branches_df = branch_df[(branch_df['min_radius'] < radius_threshold)].copy()

thin_branches_df.sort_values(['branching_node','length'],inplace = True)
#update indices in the sorted dataframe
thin_branches_df.index = range(0,len(thin_branches_df))
thin_branches_df['branching_node']=thin_branches_df['branching_node'].apply(int)
 #print to csv
 #thin_branches_df.to_csv('thin_branches_df.csv')
 #count the number of branches per branching node
branch_counts_df = thin_branches_df.groupby('branching_node').size().to_frame('row_count').reset_index()
 #branch_counts_df.to_csv('branch_counts_df.csv')

 #get the maximum length of branches
branch_max_length_df = thin_branches_df.groupby('branching_node')['length'].max().to_frame('max_length').reset_index()
 #branch_max_length_df.to_csv('branch_max_length_df.csv')

 #join the count and maximum length data together
branch_counts_max_length_df = pd.merge(branch_counts_df, branch_max_length_df, how='inner', on = 'branching_node')
 #branch_counts_max_length_df.to_csv('branch_counts_max_length_df.csv')

 #join the count and maximum length data with the branch info containing nodes and element numbers
short_thin_branches_df = pd.merge(branch_counts_max_length_df, thin_branches_df, how='inner', on = 'branching_node')
#short_thin_branches_df.to_csv('short_thin_branches_df.csv')

 #remove the longest branch where there is more than one branch for the same branching node
 # the longest branch will not be deleted
short_thin_branches_df = short_thin_branches_df.loc[(short_thin_branches_df['row_count'] == 1) |
    ((short_thin_branches_df['row_count'] > 1) &
     (short_thin_branches_df['max_length'] != short_thin_branches_df['length']))]
short_thin_branches_df.index = range(0,len(short_thin_branches_df))

short_thin_branches_df.to_csv(short_thin_branches_df_out_file)

# populate arrays of nodes and elements to be removed
short_branch_elems = []
short_branch_nodes = []
for i in range(0,len(short_thin_branches_df)):
    short_branch_elems.extend(short_thin_branches_df.iloc[i]['elems'])
    short_branch_nodes.extend(short_thin_branches_df.iloc[i]['nodes'])

print('short_branch_elems',len(set(short_branch_elems)),set(short_branch_elems))
elems_to_remove = []
elems_to_remove.extend(set(short_branch_elems))
elems_to_remove.sort()
print('elems_to_remove',len(elems_to_remove),elems_to_remove)

export_elem_subset(elems_to_remove,elems,group_name,elems_to_remove_file)

print ('short_branch_nodes',len(set(short_branch_nodes)),set(short_branch_nodes))

nodes_to_remove = []
nodes_to_remove.extend(set(short_branch_nodes))
nodes_to_remove.sort()
print('nodes_to_remove',len(nodes_to_remove),nodes_to_remove)

#remove elements and nodes and write out the new element and node files

old_to_new_node_temp = np.ones(num_nodes, dtype=bool)
old_to_new_node = np.zeros(num_nodes, dtype=int)
for node in nodes_to_remove:
    old_to_new_node_temp[node]=False

j = 0
for i in range(0,num_nodes):
    if (old_to_new_node_temp[i]):
        old_to_new_node[i] = j
        j = j + 1
    else:
        old_to_new_node[i] = -1

#print to csv
#df = pd.DataFrame(old_to_new_node)
#df.to_csv('old_to_new_node_500.csv')

old_to_new_elem_temp = np.ones(num_elems, dtype=bool)
old_to_new_elem = np.zeros(num_elems, dtype=int)
for elem in elems_to_remove:
    old_to_new_elem_temp[elem]=False

j = 0
for i in range(0,num_elems):
    if (old_to_new_elem_temp[i]):
        old_to_new_elem[i] = j
        j = j + 1
    else:
        old_to_new_elem[i] = -1

#print to csv
#df = pd.DataFrame(old_to_new_elem)
#df.to_csv(home+'/placenta_patient_49/clean_tree/step8_old_to_new_elem.csv')

new_node_loc = np.zeros((num_nodes-len(nodes_to_remove), 4))
for i in range(0,num_nodes):
    new_node = old_to_new_node[i]
    if (new_node >= 0):
        new_node_loc[new_node][0] = new_node
        new_node_loc[new_node][1] = node_loc[i][1]
        new_node_loc[new_node][2] = node_loc[i][2]
        new_node_loc[new_node][3] = node_loc[i][3]
#write the new node file
pg.export_ex_coords(new_node_loc, group_name, node_out_file,'exnode')

new_elems = np.zeros((num_elems-len(elems_to_remove), 3), dtype=int)

for i in range(0, num_elems):
    new_elem = old_to_new_elem[i]
    if (new_elem >= 0):
        new_elems[new_elem][0] = new_elem
        new_elems[new_elem][1] = old_to_new_node[elems[i][1]]
        if (old_to_new_node[elems[i][1]] == -1):
            print('elem',i,'new elem',new_elem,'old node',elems[i][1])
        new_elems[new_elem][2] = old_to_new_node[elems[i][2]]
        if (old_to_new_node[elems[i][2]] == -1):
            print('elem', i, 'new elem', new_elem, 'old node', elems[i][2])
#write the new element file
pg.export_exelem_1d(new_elems, group_name, elems_out_file)

#write the radius file again

radius_info = radius_file[['mean_radius', 'shortest_radius', 'mean_as_percentage_of_shortest','radius']].copy()
new_radius_file = radius_info.drop(radius_file.index[elems_to_remove])
new_radius_file.reset_index(inplace=True)
new_radius_file.to_csv(vessel_radius_out_file)