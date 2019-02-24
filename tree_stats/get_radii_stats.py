#!/usr/bin/env python
import placentagen as pg
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

import pandas as pd


def get_elem_length(node_loc,elems):

    num_elems = len(elems)
    lengths = np.zeros(num_elems)

    for ne in range(0, num_elems):
        np1 = elems[ne][1]
        np2 = elems[ne][2]
        point1 = node_loc[np1][1:4]
        point2 = node_loc[np2][1:4]
        lengths[ne] = np.linalg.norm(point1 - point2)

    return lengths


def get_length_and_diameter_ratios(branch_lengths,branch_diameters,branch_start_end_elems,elem_connectivity,path):

    # length ratio: length of the daughter branch/length of parent
    num_elems = len(branch_lengths)
    length_ratios = np.zeros(num_elems)
    # length to diameter ratio = length of branch/diameter of branch by Strahler order
    length_to_diameter_ratios = np.zeros(num_elems)
    # diameter of daugther /diameter of parent ratio
    diameter_ratios = np.zeros(num_elems)
    done_elems = np.zeros(num_elems)
    #look at branching points, elements that have two daughter elements
    test_df = pd.DataFrame(columns=['branch_first_elem','branch_last_elem', 'parent', 'branch_length','parent_length','length_ratio',
                                    'branch_diameter','parent_diameter','branch_length_to_diameter_ratio',
                                    'parent_length_to_diameter_ratio','diameter_ratios'])
    for elem in range(0,num_elems):

        if elem_connectivity['elem_down'][elem][0] == 2:
            #store length to diameter ratio for the parent
            if done_elems[elem] == 0:
                #this is a parent element, branch lengths and diameterd are stored against the last element in the branch
                length_to_diameter_ratios[elem] = branch_lengths[elem]/branch_diameters[elem]
                done_elems[elem] = 1
            # found a parent branch, get daughters
            for x in range(1,3):
                daughter = elem_connectivity['elem_down'][elem][x]
                if done_elems[daughter] == 0:
                    #for a daughter element, find the last element in the branch\
                    last_elem_in_branch = branch_start_end_elems[daughter]
                    length_ratios[last_elem_in_branch] = branch_lengths[last_elem_in_branch]/branch_lengths[elem]
                    length_to_diameter_ratios[last_elem_in_branch] = branch_lengths[last_elem_in_branch]/branch_diameters[last_elem_in_branch]
                    diameter_ratios[last_elem_in_branch] = branch_diameters[last_elem_in_branch]/branch_diameters[elem]
                    done_elems[daughter] = 1
                    test_df.loc[len(test_df)] = [daughter,last_elem_in_branch, elem, branch_lengths[last_elem_in_branch],
                                                 branch_lengths[elem],length_ratios[last_elem_in_branch],
                                                 branch_diameters[last_elem_in_branch],
                                                 branch_diameters[elem],
                                                 length_to_diameter_ratios[last_elem_in_branch],
                                                 length_to_diameter_ratios[elem],
                                                 diameter_ratios[last_elem_in_branch]]

    test_df.to_csv(path +'/ratios.csv')

    return length_ratios,length_to_diameter_ratios,diameter_ratios


def get_branching_angles(node_loc,elems,elem_connectivity,branch_start_end_elems):

    num_elems = len(elems)
    branching_angles = np.zeros(num_elems)
    branching_angles[:] = -1
    #test_df = pd.DataFrame(columns=['element', 'parent', 'branching_angle'])

    for ne in range(0,num_elems):
        # find parent branch (only one parent as this is the arterial tree)

        if elem_connectivity['elem_up'][ne][0] > 0:
            parent_elem = elem_connectivity['elem_up'][ne][1]
            #only if this is a true branching point
            if (elem_connectivity['elem_down'][parent_elem][0] > 1):

                # parent vector
                endNode = int(elems[parent_elem][1])
                startNode = int(elems[parent_elem][2])
                v_parent = node_loc[endNode][1:4] - node_loc[startNode][1:4]
                v_parent = v_parent / np.linalg.norm(v_parent)

                # daughter vector
                #endNode = int(elems[ne][2])
                #startNode = int(elems[ne][1])
                endNode = int(elems[ne][1])
                startNode = int(elems[ne][2])
                v_daughter = node_loc[endNode][1:4] - node_loc[startNode][1:4]
                v_daughter = v_daughter / np.linalg.norm(v_daughter)

                cosang = np.dot(v_parent, v_daughter)
                sinang = np.linalg.norm(np.cross(v_parent, v_daughter))
                #angle = 180 - (np.arctan2(sinang, cosang) * 180)/np.pi #convert radians to degrees
                angle = (np.arctan2(sinang, cosang) * 180) / np.pi  # convert radians to degrees
                #find the last element in the branch
                last_elem_in_branch = branch_start_end_elems[ne]
                branching_angles[last_elem_in_branch] = angle

                #test_df.loc[len(test_df)] = [ne, parent_elem, angle]

            #else:
               #test_df.loc[len(test_df)] = [ne, 0, 0]

        #else:

            #test_df.loc[len(test_df)] = [ne, 0, 0]

    #test_df.to_csv('branching angles_v2.csv')

    return branching_angles


def elem_stats_by_strahler(elem_info_df,filename,branch_type):

    max_strahler = max(elem_info_df.iloc[:]['Strahler order'].tolist())

    stats_by_strahler_output = pd.DataFrame(columns=['Strahler_order','number_of_branches',
              'branch_length (sd)', 'branch_diameter (sd)', 'number_of_daughter_branches',
              'length_to_diameter_ratio','branching_angle','length_ratio', 'diameter_ratio',
              'branching_ratio'])

    mean_branching_ratio = 0
    previous_no_of_branches = 0
    for i in range(0,max_strahler):
        str_order = i + 1
        if branch_type == 'all':
            elems_for_order_df = elem_info_df[(elem_info_df['Strahler order'] == str_order)].copy()
        elif branch_type == 'major':
            elems_for_order_df = elem_info_df[(elem_info_df['Strahler order'] == str_order) &
                                              (elem_info_df['major_minor'] == 1)].copy()
        elif branch_type == 'minor':
            elems_for_order_df = elem_info_df[(elem_info_df['Strahler order'] == str_order) &
                                              (elem_info_df['major_minor'] == 2)].copy()

        no_elems = len(elems_for_order_df)

        branch_lengths_for_order = np.zeros(no_elems)
        branch_lengths_for_order[:] = elems_for_order_df.iloc[:]['branch_length'].tolist()
        branch_lengths_for_order = branch_lengths_for_order[branch_lengths_for_order > 0]
        no_of_branches = np.count_nonzero(branch_lengths_for_order)

        branch_diameters_for_order = np.zeros(no_elems)
        branch_diameters_for_order[:] = elems_for_order_df.iloc[:]['branch_diameter'].tolist()
        branch_diameters_for_order = branch_diameters_for_order[branch_diameters_for_order > 0]

        length_ratios_for_order = np.zeros(no_elems)
        length_ratios_for_order[:] = elems_for_order_df.iloc[:]['length_ratio'].tolist()
        length_ratios_for_order = length_ratios_for_order[length_ratios_for_order > 0]
        no_of_daughter_branches = np.count_nonzero(length_ratios_for_order)

        diameter_ratios_for_order = np.zeros(no_elems)
        diameter_ratios_for_order[:] = elems_for_order_df.iloc[:]['diameter_ratio'].tolist()
        diameter_ratios_for_order = diameter_ratios_for_order[diameter_ratios_for_order > 0]

        branch_length_to_diameter_for_order = np.zeros(no_elems)
        branch_length_to_diameter_for_order[:] = elems_for_order_df.iloc[:]['length_to_diameter_ratio'].tolist()
        branch_length_to_diameter_for_order = branch_length_to_diameter_for_order[branch_length_to_diameter_for_order > 0]

        if (previous_no_of_branches > 0) and (no_of_branches > 0) and (branch_type == 'all'):
            #calculate branching ratio
            stats_by_strahler_output.loc[i-1, 'branching_ratio'] = np.round_(np.float(previous_no_of_branches)/np.float(no_of_branches),decimals=2)
            mean_branching_ratio = mean_branching_ratio + stats_by_strahler_output.loc[i-1, 'branching_ratio']

        previous_no_of_branches = no_of_branches;


        branching_angles_per_order = np.zeros(no_elems)
        branching_angles_per_order[:] = elems_for_order_df.iloc[:]['branching_angle'].tolist()
        branching_angles_per_order = branching_angles_per_order[branching_angles_per_order > -1]
        no_of_branching_angles = np.count_nonzero(branching_angles_per_order)

        stats_by_strahler_output.loc[i,'Strahler_order'] = str_order

        if no_of_branches > 0:
            stats_by_strahler_output.loc[i, 'number_of_branches'] = no_of_branches
            stats_by_strahler_output.loc[i, 'branch_length (sd)'] = str(np.round_(np.mean(branch_lengths_for_order),decimals=2)) \
                                + ' (' + str(np.round_(np.std(branch_lengths_for_order),decimals=2)) + ')'
            stats_by_strahler_output.loc[i, 'branch_diameter (sd)'] = \
                str(np.round_(np.mean(branch_diameters_for_order),decimals=2)) + ' (' + str(np.round_(np.std(branch_diameters_for_order),decimals=2)) + ')'
            stats_by_strahler_output.loc[i, 'length_to_diameter_ratio'] = \
                str(np.round_(np.mean(branch_length_to_diameter_for_order),decimals=2)) + ' (' \
                                    + str(np.round_(np.std(branch_length_to_diameter_for_order),decimals=2)) + ')'

        if no_of_daughter_branches > 0:
            stats_by_strahler_output.loc[i, 'number_of_daughter_branches'] = no_of_daughter_branches
            stats_by_strahler_output.loc[i, 'length_ratio'] = \
                str(np.round_(np.mean(length_ratios_for_order),decimals=2)) + ' (' \
                    + str(np.round_(np.std(length_ratios_for_order),decimals=2)) + ')'

            stats_by_strahler_output.loc[i, 'diameter_ratio'] = str(np.round_(np.mean(diameter_ratios_for_order),decimals=2)) + ' (' \
                                                                        + str(np.round_(np.std(diameter_ratios_for_order),decimals=2)) + ')'

        if no_of_branching_angles > 0:
            stats_by_strahler_output.loc[i, 'branching_angle'] = str(np.round_(np.mean(branching_angles_per_order),decimals=2)) + ' (' \
                              + str(np.round_(np.std(branching_angles_per_order),decimals=2)) + ')'

    #print totals
    if branch_type == 'all':
        elems_df = elem_info_df.copy()
    elif branch_type == 'major':
        elems_df = elem_info_df[(elem_info_df['major_minor'] == 1)].copy()
    elif branch_type == 'minor':
        elems_df = elem_info_df[(elem_info_df['major_minor'] == 2)].copy()

    no_elems = len(elems_df)

    branch_lengths = np.zeros(no_elems)
    branch_lengths[:] = elems_df.iloc[:]['branch_length'].tolist()
    branch_lengths = branch_lengths[branch_lengths > 0]
    no_of_branches = np.count_nonzero(branch_lengths)

    branch_diameters = np.zeros(no_elems)
    branch_diameters[:] = elems_df.iloc[:]['branch_diameter'].tolist()
    branch_diameters = branch_diameters[branch_diameters > 0]

    length_ratios = np.zeros(no_elems)
    length_ratios[:] = elems_df.iloc[:]['length_ratio'].tolist()
    length_ratios = length_ratios[length_ratios > 0]
    no_of_daughter_branches = np.count_nonzero(length_ratios)

    diameter_ratios = np.zeros(no_elems)
    diameter_ratios[:] = elems_df.iloc[:]['diameter_ratio'].tolist()
    diameter_ratios = diameter_ratios[diameter_ratios > 0]

    branch_length_to_diameter = np.zeros(no_elems)
    branch_length_to_diameter[:] = elems_df.iloc[:]['length_to_diameter_ratio'].tolist()
    branch_length_to_diameter = branch_length_to_diameter[branch_length_to_diameter > 0]

    branching_angles = np.zeros(no_elems)
    branching_angles[:] = elems_df.iloc[:]['branching_angle'].tolist()
    branching_angles = branching_angles[branching_angles > -1]
    no_of_branching_angles = np.count_nonzero(branching_angles)


    i = i + 1
    if no_of_branches > 0:
        stats_by_strahler_output.loc[i, 'number_of_branches'] = no_of_branches
        stats_by_strahler_output.loc[i, 'branch_length (sd)'] = str(
            np.round_(np.mean(branch_lengths), decimals=2)) \
                                                                + ' (' + str(
            np.round_(np.std(branch_lengths), decimals=2)) + ')'
        stats_by_strahler_output.loc[i, 'branch_diameter (sd)'] = \
            str(np.round_(np.mean(branch_diameters), decimals=2)) + ' (' + str(
                np.round_(np.std(branch_diameters), decimals=2)) + ')'
        stats_by_strahler_output.loc[i, 'length_to_diameter_ratio'] = \
            str(np.round_(np.mean(branch_length_to_diameter), decimals=2)) + ' (' \
            + str(np.round_(np.std(branch_length_to_diameter), decimals=2)) + ')'

    if no_of_daughter_branches > 0:
        stats_by_strahler_output.loc[i, 'number_of_daughter_branches'] = no_of_daughter_branches
        stats_by_strahler_output.loc[i, 'length_ratio'] = \
            str(np.round_(np.mean(length_ratios), decimals=2)) + ' (' \
            + str(np.round_(np.std(length_ratios), decimals=2)) + ')'

        stats_by_strahler_output.loc[i, 'diameter_ratio'] = str(
            np.round_(np.mean(diameter_ratios), decimals=2)) + ' (' \
                                                            + str(
            np.round_(np.std(diameter_ratios), decimals=2)) + ')'

    if no_of_branching_angles > 0:
        stats_by_strahler_output.loc[i, 'branching_angle'] = str(
            np.round_(np.mean(branching_angles), decimals=2)) + ' (' \
                                                             + str(
            np.round_(np.std(branching_angles), decimals=2)) + ')'

    mean_branching_ratio = np.round_(mean_branching_ratio/max_strahler,decimals=2)
    stats_by_strahler_output.loc[i, 'branching_ratio'] = mean_branching_ratio

    stats_by_strahler_output.to_csv(filename)
    #print(tabulate(length_by_strahler_output_df, headers=header))

    return 0


def import_elem_radius(file_name):
    element_file = pd.read_csv(file_name, sep="\n", header=None)

    num_elems = (len(element_file) - 8) / 3
    elem_radius = np.zeros(num_elems)
    i = 0
    for n in range(10, len(element_file), 3):
       radii = element_file[0][n].split()
       elem_radius[i] = radii[0]
       i = i + 1

    return elem_radius


def get_branch_lengths_and_diameters(node_loc,elems,elem_connectivity,lengths,elem_diameter,path):

    num_elems = len(elems)
    num_nodes = len(node_loc)

    # populate the elems_at_node array listing the elements connected to each node
    elems_count_at_node = np.zeros(num_nodes)
    for i in range(0, num_elems):
        for x in range(1, 3):
            node = elems[i][x]
            elems_count_at_node[node] = elems_count_at_node[node] + 1


    # branching points have one parent and 2 daughter branches - lengths and diameters are stored under
    # all element numbers that start or end the branch - this is needed to calculate diameter and length ratios
    branching_elem_lengths = np.zeros(num_elems)
    branching_elem_diameters = np.zeros(num_elems)

    #store the element indices for elements that start and end a branch branch_start_end_elems[start_elem] = end_elem
    branch_start_end_elems = np.zeros(num_elems,dtype=int)


    # these arrays store lengths and diameters against the last element in the branch only, so that we
    # can count the number of branches per Strahler order
    branch_lengths = np.zeros(num_elems)
    branch_diameters = np.zeros(num_elems)

    done_elem = np.zeros(num_elems)
    for ne in range(0, num_elems):
        # this is a branching parent as it has more than one daughter
        if (elem_connectivity['elem_down'][ne][0] > 1):

            if done_elem[ne] == 0:

                parent_start_found = False
                parent_branch_length = 0
                elems_in_branch = 0
                parent_branch_diameter = 0
                next_element = ne
                while not parent_start_found:

                    parent_branch_length = parent_branch_length + lengths[next_element]
                    elems_in_branch = elems_in_branch + 1
                    parent_branch_diameter = parent_branch_diameter + elem_diameter[next_element]
                    # get the first node for the parent
                    first_node = elems[next_element][1]
                    # if this node is not a branching point or a terminal point, keep looking for a branching point upstream
                    if elems_count_at_node[first_node] == 2:
                        next_element = elem_connectivity['elem_up'][next_element][1]
                    else:
                        parent_start_found = True

                parent_branch_diameter = parent_branch_diameter / elems_in_branch  # to get the mean diameter of all elements in the branch
                #branching_elem_lengths[ne] = parent_branch_length
                #branching_elem_diameters[ne] = parent_branch_diameter
                branch_start_end_elems[next_element] = ne

                # this is the last element in the branch
                branch_lengths[ne] = parent_branch_length
                branch_diameters[ne] = parent_branch_diameter
                done_elem[ne] = 1

            # get daughter branches
            for d in range(1, 3):
                daughter = elem_connectivity['elem_down'][ne][d]

                if done_elem[daughter] == 0:

                    daughter_end_found = False
                    daughter_branch_length = 0
                    elems_in_branch = 0
                    daughter_branch_diameter = 0
                    next_element = daughter
                    while not daughter_end_found:

                        daughter_branch_length = daughter_branch_length + lengths[next_element]
                        elems_in_branch = elems_in_branch + 1
                        daughter_branch_diameter = daughter_branch_diameter + elem_diameter[next_element]
                        # get the second node for the daughter
                        second_node = elems[next_element][2]
                        # if this node is not a branching point or a terminal point, keep looking for a branching point upstream
                        if elems_count_at_node[second_node] == 2:
                            next_element = elem_connectivity['elem_down'][next_element][1]
                        else:
                            daughter_end_found = True

                    daughter_branch_diameter = daughter_branch_diameter / elems_in_branch  # to get the mean diameter of all elements in the branch
                    #branching_elem_lengths[daughter] = daughter_branch_length
                    #branching_elem_diameters[daughter] = daughter_branch_diameter
                    branch_start_end_elems[daughter] = next_element

                    # this is the last element in the branch
                    branch_lengths[next_element] = daughter_branch_length
                    branch_diameters[next_element] = daughter_branch_diameter
                    done_elem[daughter] = 1

    df = pd.DataFrame(branch_start_end_elems)
    df.to_csv(path + '/branch_start_end_elems.csv')

    return branch_lengths,branch_diameters,branch_start_end_elems


def get_major_and_minor_branches(num_elems,elem_connectivity,branch_diameters,branch_start_end_elems):

    major_minor = np.zeros(num_elems)
    #1 - major 2-minor

    for ne in range(0, num_elems):
        # this is a branching element as it has more than one daughter branch
        if (elem_connectivity['elem_down'][ne][0] > 1):
            # get daughter branches
            daughter1 = elem_connectivity['elem_down'][ne][1]
            daughter2 = elem_connectivity['elem_down'][ne][2]
            #get last elements for daughter branches
            last_elem_in_daughter1 = branch_start_end_elems[daughter1]
            last_elem_in_daughter2 = branch_start_end_elems[daughter2]

            if branch_diameters[last_elem_in_daughter1] >= branch_diameters[last_elem_in_daughter2]:
                major_minor[last_elem_in_daughter1] = 1 #major branch
                major_minor[last_elem_in_daughter2] = 2 #minor branch
            else:
                major_minor[last_elem_in_daughter2] = 1
                major_minor[last_elem_in_daughter1] = 2

    return major_minor

def print_parent_and_daughter_diameters(num_elems,elem_connectivity,branch_diameters,
                                        branch_start_end_elems,major_minor,path):
    test_df = pd.DataFrame(columns=['parent','parent_diameter', 'major_branch',
                                    'major_diameter','minor_branch','minor_diameter'])
    for ne in range(0, num_elems):
        # this is a branching element as it has more than one daughter branch
        if (elem_connectivity['elem_down'][ne][0] > 1):
            # get daughter branches
            daughter1 = elem_connectivity['elem_down'][ne][1]
            daughter2 = elem_connectivity['elem_down'][ne][2]
            #get last elements for daughter branches
            last_elem_in_daughter1 = branch_start_end_elems[daughter1]
            last_elem_in_daughter2 = branch_start_end_elems[daughter2]

            if major_minor[last_elem_in_daughter1] == 1: # major branch
                major_branch = last_elem_in_daughter1
                minor_branch = last_elem_in_daughter2

            if major_minor[last_elem_in_daughter2] == 1: # major branch
                major_branch = last_elem_in_daughter2
                minor_branch = last_elem_in_daughter1


            test_df.loc[len(test_df)] = [ne, branch_diameters[ne],
                                         major_branch, branch_diameters[major_branch],
                                         minor_branch, branch_diameters[minor_branch]]

    test_df.to_csv(path + '/major_minor_diameters.csv')

    return 0