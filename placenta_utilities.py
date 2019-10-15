#!/usr/bin/env python

import placentagen as pg
import numpy as np
import pandas as pd


def find_inlet_nodes(nodes, elems,elem_connectivity):

    inlet_nodes = []
    inlet_elems = find_inlet_elems(elems,elem_connectivity)
    for i in inlet_elems:
        #first node of the element is the inlet node
        inlet_nodes.append(elems[i][1])

    return inlet_nodes

def find_inlet_elems(elems,elem_connectivity):

    num_elems = len(elems)

    inlet_elems = []
    for i in range(0,num_elems):
       #find the elements that don't have any upstream elements
       if elem_connectivity['elem_up'][i][0] == 0:
           inlet_elems.append(i)

    return inlet_elems

def get_elements_at_a_node(nodes, elems):

    num_elems = len(elems)
    num_nodes = len(nodes)

    elems_at_node = np.zeros((num_nodes, 10), dtype=int)
    for i in range(0, num_elems):
        node1 = elems[i][1]
        elems_at_node[node1][0] = elems_at_node[node1][0] + 1
        j = elems_at_node[node1][0]
        elems_at_node[node1][j] = i

        node2 = elems[i][2]
        elems_at_node[node2][0] = elems_at_node[node2][0] + 1
        j = elems_at_node[node2][0]
        elems_at_node[node2][j] = i

    return elems_at_node


def renumber(inlet_node, elems, anast_exists, anast_elem):
    # get all elements connected to the node that we haven't seen
    global element_number
    global old_to_new_elem
    global seen_elements
    global elems_at_node
    connected_elems_no = elems_at_node[inlet_node][0]
    for i in range(0, connected_elems_no):
        elem = elems_at_node[inlet_node][i + 1]  # elements start at column index 1
        if not seen_elements[elem]:
            seen_elements[elem] = True
            old_to_new_elem[elem] = element_number
            element_number = element_number + 1
            if not anast_exists or (elem != anast_elem): #if this is the anastomosis element stop going downstream to renumber elements
                second_node = elems[elem][2]
                renumber(second_node, elems, anast_exists, anast_elem)
    return

def renumber_elems(node_loc, elems, elem_connectivity, anast_exists, anast_elem):

    global element_number
    global old_to_new_elem
    global elems_at_node
    elems_at_node = get_elements_at_a_node(node_loc, elems)
    num_elems = len(elems)
    old_to_new_elem = np.zeros(num_elems, dtype=int)
    global seen_elements
    seen_elements = np.zeros(num_elems, dtype=bool)

    element_number = 0
    inlet_nodes = find_inlet_nodes(node_loc, elems, elem_connectivity)

    for in_node in inlet_nodes:
        renumber(in_node, elems, anast_exists, anast_elem)

    new_elems = np.zeros((num_elems, 3), dtype=int)

    for i in range(0, num_elems):
        new_elem = old_to_new_elem[i]
        new_elems[new_elem][0] = new_elem
        new_elems[new_elem][1] = elems[i][1]
        new_elems[new_elem][2] = elems[i][2]

    return new_elems,old_to_new_elem


def renumber_elem_radii(elem_radii,old_to_new_elem):
    num_elems = len(elem_radii)
    new_elem_radii = np.zeros(num_elems, dtype=float)
    for i in range(0,num_elems):
        new_elem = old_to_new_elem[i]
        new_elem_radii[new_elem] = elem_radii[i]

    return new_elem_radii


def import_elem_file(filename):
    element_file = pd.read_csv(filename, sep="\n", header=None)

    num_elems = (len(element_file) - 31) / 5
    elems = np.zeros((num_elems, 3), dtype=int)

    i = 0
    for n in range(31, len(element_file), 5):
        elem_no_text = element_file[0][n].split()
        elems[i][0] = int(elem_no_text[1]) - 1 #in python element numbers start at 0, reprosim at 1
        i = i + 1

    i = 0
    for n in range(33, len(element_file), 5):
        nodes = element_file[0][n].split()
        elems[i][1] = int(nodes[0]) - 1  # starts at this node (-1)
        elems[i][2] = int(nodes[1]) - 1  # ends at this node (-1)
        i = i + 1

    return elems

def element_centre_xyz(elem,node_loc,elems):
    node1 = elems[elem][1]
    node2 = elems[elem][2]
    (x1,y1,z1) = node_loc[node1][1:4]
    (x2, y2, z2) = node_loc[node2][1:4]
    x = (x1 + x2)/2
    y = (y1 + y2)/2
    z = (z1 + z2)/2
    return x,y,z


def centre_between_two_nodes_xyz(node1, node2,node_loc):
    (x1,y1,z1) = node_loc[node1][1:4]
    (x2, y2, z2) = node_loc[node2][1:4]
    x = (x1 + x2)/2
    y = (y1 + y2)/2
    z = (z1 + z2)/2
    return x,y,z

#this function returns the coordinates of a node that is a desired distance away from the first node
#of an element
#new node coordinates are calculated by scaling a unit vector for the element to the desired distance
def split_element_xyz(elem, node_loc, elems, distance):
    node1 = elems[elem][1]
    node1_coords = np.array(node_loc[node1][1:4])
    unit_vector = get_unit_vector_for_elem(elem, node_loc, elems)
    new_node = node1_coords + distance * unit_vector

    return new_node

#create a vector by subtracting the coordinates of node1 from node2 and normalise this vector by dividing it by
#its length
def get_unit_vector_for_elem(elem, node_loc, elems):

    node1 = elems[elem][1]
    node2 = elems[elem][2]
    (x1,y1,z1) = node_loc[node1][1:4]
    (x2,y2,z2) = node_loc[node2][1:4]

    elem_length = np.sqrt(np.float_power(x2 - x1, 2) + np.float_power(y2 - y1, 2) + np.float_power(z2 - z1, 2))

    unit_vector = np.array([(x2 - x1)/elem_length, (y2 - y1)/elem_length, (z2 - z1)/elem_length])

    return unit_vector


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


def write_radius_as_ipfiel(node_loc,elems, elem_radii, filename):
    # assign a radius to nodes
    # first element - both nodes will have the same radius as the element - for all other elements assign the element radius
    # to the second node
    elem_connectivity = pg.element_connectivity_1D(node_loc, elems)
    inlet_elements = find_inlet_elems(elems, elem_connectivity)
    num_nodes = len(node_loc)
    num_elems = len(elems)

    node_radius = np.zeros(num_nodes, dtype=float)
    for i in range(0, num_elems):
        node1 = elems[i][1]
        node2 = elems[i][2]
        if i in inlet_elements:
            node_radius[node1] = elem_radii[i]
            node_radius[node2] = elem_radii[i]
        else:
            node_radius[node2] = elem_radii[i]

    f = open(filename, 'w')

    f.write("CMISS Version 2.1  ipelem File Version 2\n")
    f.write("Heading:\n")
    f.write("\n")
    f.write("The number of nodes is [     {0}]:      {1}\n".format(num_nodes, num_nodes))
    f.write("Do you want prompting for different versions of field variable 1 [N]? Y\n")
    f.write("The number of derivatives for field variable 1 is [0]: 0\n")

    for n in range(0, num_nodes):
        f.write("\n")
        f.write("Node number [     {0}]:    {1}\n".format(n + 1, n + 1))
        f.write("The number of versions for field variable 1 is [1]:  1\n")
        # use scientific notation for radius values
        f.write("The field variable 1 value is [ {0:.5e}]:  {1:.5e}\n".format(node_radius[n], node_radius[n]))

    f.close()

    return


def get_elem_length(node_loc, elems):

    num_elems = len(elems)
    #calculate element lengths
    elem_length = np.zeros((num_elems))
    for i in range(0,num_elems):
        node1 = elems[i][1]
        node2 = elems[i][2]
        x1 = node_loc[node1][1]
        y1 = node_loc[node1][2]
        z1 = node_loc[node1][3]

        x2 = node_loc[node2][1]
        y2 = node_loc[node2][2]
        z2 = node_loc[node2][3]
        # calculate the length of each element
        elem_length[i] = np.sqrt(np.float_power(x2 - x1,2) + np.float_power(y2 - y1,2) + np.float_power(z2 - z1,2))

    return elem_length


def write_ipelem(elems,filename):

    num_elems = len(elems)
    f = open(filename, 'w')

    f.write("CMISS Version 2.1  ipelem File Version 2\n")
    f.write("Heading:\n")
    f.write("\n")
    f.write("The number of elements is [     {0}]:      {1}\n".format(num_elems, num_elems))

    for n in range(0, num_elems):
        f.write("\n")
        f.write("Element number[     {0}]:    {1}\n".format(n + 1, n + 1))
        f.write("The number of geometric Xj-coordinates is [3]: 3\n")
        f.write("The basis function type for geometric variable 1 is [1]:  1\n")
        f.write("The basis function type for geometric variable 2 is [1]:  1\n")
        f.write("The basis function type for geometric variable 3 is [1]:  1\n")
        f.write("Enter the 2 global numbers for basis 1:     {0}     {1}\n".format(elems[n][1] + 1, elems[n][2] + 1))

    f.close()

    return 0

def write_ipnode(node_loc, filename):

    num_nodes = len(node_loc)

    f = open(filename, 'w')
    f.write("CMISS Version 2.1  ipelem File Version 2\n")
    f.write("Heading:\n")
    f.write("\n")
    f.write("The number of nodes is [     {0}]:      {1}\n".format(num_nodes, num_nodes))
    f.write("Number of coordinates [3]: 3\n")
    f.write("Do you want prompting for different versions of nj=1 [N]? Y\n")
    f.write("Do you want prompting for different versions of nj=2 [N]? Y\n")
    f.write("Do you want prompting for different versions of nj=3 [N]? Y\n")
    f.write("The number of derivatives for coordinate 1 is [0]: 0\n")
    f.write("The number of derivatives for coordinate 2 is [0]: 0\n")
    f.write("The number of derivatives for coordinate 3 is [0]: 0\n")

    for n in range(0, num_nodes):
        f.write("\n")
        f.write("Node number[     {0}]:    {1}\n".format(n + 1, n + 1))
        f.write("The number of versions for nj=1 is [1]:  1\n")
        f.write("The Xj(1) coordinate is [ 0.00000E+00]:    {0}\n".format(node_loc[n][1]))
        f.write("The number of versions for nj=2 is [1]:  1\n")
        f.write("The Xj(2) coordinate is [ 0.00000E+00]:    {0}\n".format(node_loc[n][2]))
        f.write("The number of versions for nj=3 is [1]:  1\n")
        f.write("The Xj(3) coordinate is [ 0.00000E+00]:    {0}\n".format(node_loc[n][3]))

    f.close()

    return 0


######
# Modified from placentagen (https://github.com/VirtualPregnancy/placentagen), Author Rachel Smith
# Writes values to a cmgui exelem file
# Inputs: data - an N x 1 array with a value for each element in the tree
#         groupname - group name that will appear in cmgui
#         filename - name that the file is saved as
#         name - name that values will be called in cmgui
# Outputs: an "exelem" file containing the data value for each element, named according to names specified
######

def export_solution_2(data, groupname, filename, name):
    # Write header
    type = "exelem"
    data_num = len(data)
    filename = filename + '.' + type
    f = open(filename, 'w')
    f.write(" Group name: %s\n" % groupname)
    f.write("Shape. Dimension=1\n")
    f.write("#Scale factor sets=0\n")
    f.write("#Nodes=0\n")
    f.write(" #Fields=1\n")
    f.write("1) " + name + ", field, rectangular cartesian, #Components=1\n")
    f.write(name + ".  l.Lagrange, no modify, grid based.\n")
    f.write(" #xi1=1\n")

    # Write element values
    for x in range(0, data_num):
        f.write(" Element:            %s 0 0\n" % int(x + 1))
        f.write("   Values:\n")
        f.write("          %s" % np.squeeze(data[x]))
        f.write("   %s \n" % np.squeeze(data[x]))
    f.close()

    return 0


def export_elem_subset(elem_subset,elems,group_name,filename):
    elem_subset.sort()
    subset_of_elems = np.zeros((len(elem_subset), 3), dtype=int)
    i = 0
    for element in elem_subset:
        subset_of_elems[i][0] = elems[element][0]
        subset_of_elems[i][1] = elems[element][1]
        subset_of_elems[i][2] = elems[element][2]
        i = i + 1
    pg.export_exelem_1d(subset_of_elems, group_name, filename)

    return 0


def export_node_subset(node_subset,node_loc,group_name,filename):
    node_subset.sort()
    subset_of_nodes = np.zeros((len(node_subset), 4))
    i = 0
    for node in node_subset:
        subset_of_nodes[i][0] = node_loc[node][0]
        subset_of_nodes[i][1] = node_loc[node][1]
        subset_of_nodes[i][2] = node_loc[node][2]
        subset_of_nodes[i][3] = node_loc[node][3]
        i = i + 1
    pg.export_ex_coords(subset_of_nodes, group_name, filename, 'exnode')

    return 0


def export_datapoint_subset(datapoint_subset,data_points,group_name,filename):
    datapoint_subset.sort()
    subset_of_points = np.zeros((len(datapoint_subset), 4))
    i = 0
    for point in datapoint_subset:
        subset_of_points[i][0] = data_points[point][0]
        subset_of_points[i][1] = data_points[point][1]
        subset_of_points[i][2] = data_points[point][2]
        subset_of_points[i][3] = data_points[point][3]
        i = i + 1
    pg.export_ex_coords(subset_of_points, group_name, filename, 'exdata')

    return 0