#!/usr/bin/env python

import placentagen as pg
import numpy as np
import pandas as pd


def find_inlet_node(nodes, elems,elem_connectivity):

    num_elems = len(elems)
    i = 0
    inlet_found = False
    inlet_node = -1
    while not inlet_found and i< num_elems:
       #find the element that doesn't have any upstream elements
       if elem_connectivity['elem_up'][i][0] == 0:
           inlet_found = True
       else:
           i = i + 1
    if inlet_found:
        #first node of the element is the inlet node
        inlet_node = elems[i][1]

    return inlet_node

def find_inlet_elem(elems,elem_connectivity):

    num_elems = len(elems)
    i = 0
    inlet_found = False
    inlet_elem = -1
    while not inlet_found and i< num_elems:
       #find the element that doesn't have any upstream elements
       if elem_connectivity['elem_up'][i][0] == 0:
           inlet_found = True
       else:
           i = i + 1
    if inlet_found:
       inlet_elem = i

    return inlet_elem

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


def renumber(first_node,elems,anastomosis):
    # get all elements connected to the node that we haven't seen
    global element_number
    global old_to_new_elem
    global seen_elements
    global elems_at_node
    connected_elems_no = elems_at_node[first_node][0]
    for i in range(0, connected_elems_no):
        elem = elems_at_node[first_node][i + 1]  # elements start at column index 1
        if not seen_elements[elem]:
            seen_elements[elem] = True
            old_to_new_elem[elem] = element_number
            element_number = element_number + 1
            if elem != anastomosis: #if this is the anastomosis element stop going downstream to renumber elements
                second_node = elems[elem][2]
                renumber(second_node,elems,anastomosis)
    return

def renumber_elems(node_loc, elems, elem_connectivity,anastomosis):

    first_node = find_inlet_node(node_loc, elems, elem_connectivity)
    global element_number
    global old_to_new_elem
    global elems_at_node
    elems_at_node = get_elements_at_a_node(node_loc, elems)
    num_elems = len(elems)
    old_to_new_elem = np.zeros(num_elems, dtype=int)
    global seen_elements
    seen_elements = np.zeros(num_elems, dtype=bool)

    element_number = 0
    renumber(first_node,elems,anastomosis)

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
        elems[i][0] = elem_no_text[1]
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
    inlet_element = find_inlet_elem(elems, elem_connectivity)
    num_nodes = len(node_loc)
    num_elems = len(elems)

    node_radius = np.zeros(num_nodes, dtype=float)
    for i in range(0, num_elems):
        node1 = elems[i][1]
        node2 = elems[i][2]
        if i == inlet_element:
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