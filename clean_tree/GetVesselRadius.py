#!/usr/bin/env python
 
import placentagen as pg
import numpy as np
import pandas as pd
import scipy.spatial as spatial

#calculates the shortest distance between a point an a plane
def get_point_to_plane_dist(point_coords,A,B,C,D):
    #shortest distance between a point outside of the plane and the plane
    #point (x0,y0,z0) plane Ax+By+Cz = D
    [x0,y0,z0] = point_coords
    distance = np.abs((A*x0 + B*y0 + C*z0 - D) / np.sqrt(A**2 + B**2 + C**2))

    return distance


#read the node file
#node_file = pd.read_csv('new_nodes_500.exnode',sep="\n", header=None) #1st run
#node_file = pd.read_csv('new_nodes_v4.exnode',sep="\n", header=None) #2nd run
#node_file = pd.read_csv('chorionic_vessels/chor_nodes_cycle2_v6.exnode',sep="\n", header=None) #3rd run
node_file = pd.read_csv('small_vessels/sv_nodes_v3.exnode',sep="\n", header=None)

num_nodes = (len(node_file) - 6)/4
node_loc = np.zeros((num_nodes, 4))

i=0
for n in range(7,len(node_file),4):
    node_loc[i][0] = i
    node_loc[i][1] = node_file[0][n]
    i=i+1

i=0
for n in range(8,len(node_file),4):
    node_loc[i][2] = node_file[0][n]
    i=i+1

i=0
for n in range(9,len(node_file),4):
    node_loc[i][3] = node_file[0][n]
    i=i+1

#write the exnode file
#pg.export_ex_coords(node_loc,'test_node_file','test_node_file','exnode')

#read the element file
#element_file = pd.read_csv('new_elems_500.exelem',sep="\n", header=None) #1st run
#element_file = pd.read_csv('new_elems_v4.exelem',sep="\n", header=None) #2nd run
#element_file = pd.read_csv('chorionic_vessels/chor_elems_cycle2_v6.exelem',sep="\n", header=None) #3rd run
element_file = pd.read_csv('small_vessels/sv_elems_v3.exelem',sep="\n", header=None)

num_elems = (len(element_file)-31)/5
elems = np.zeros((num_elems, 3), dtype=int)

i=0
for n in range(33, len(element_file),5):
    elems[i][0] = i  # creating new element
    nodes = element_file[0][n].split()
    elems[i][1] = int(nodes[0]) - 1 # starts at this node (-1)
    elems[i][2] = int(nodes[1]) - 1 # ends at this node (-1)
    i = i+1

# write the exelem file
#pg.export_exelem_1d(elems, 'test_elems', 'test_elems')


#read the vessel surface data points file
#points_file = pd.read_csv('chorionic_vessels/large_vessel_surface_v2.exdata',sep="\n", header=None) #3rd run
points_file = pd.read_csv('small_vessels/small_vessel_surface_rescaled.exdata',sep="\n", header=None) #small vessels


num_points = (len(points_file) - 6)/4
points_loc = np.zeros((num_points, 3))

i=0
for n in range(7,len(points_file),4):
    #points_loc[i][0] = i
    points_loc[i][0] = points_file[0][n]
    i=i+1

i=0
for n in range(8,len(points_file),4):
    points_loc[i][1] = points_file[0][n]
    i=i+1

i=0
for n in range(9,len(points_file),4):
    points_loc[i][2] = points_file[0][n]
    i=i+1

#write the exdata file (this can only be used if points_loc has the node number stored in the first column
#pg.export_ex_coords(points_loc,'large_vessel_surface','large_vessel_surface','exdata')

point_tree = spatial.cKDTree(points_loc)

elems_info_df = pd.DataFrame(columns=['centre_x', 'centre_y', 'centre_z', 'A', 'B', 'C', 'D', 'mean_radius',
                                      'shortest_radius', 'mean_as_percentage_of_shortest', 'radius',
                                      'radius_points','all_points'])

#for each element
for i in range(0,num_elems):
#for i in range(80,90):
#for i in [83]:
    print('processing element',i)
    #get the element nodes
    node1 = elems[i][1]
    node2 = elems[i][2]
    #get node coordinates
    x1 = node_loc[node1][1]
    y1 = node_loc[node1][2]
    z1 = node_loc[node1][3]

    x2 = node_loc[node2][1]
    y2 = node_loc[node2][2]
    z2 = node_loc[node2][3]

    #get the centre of mass between the two nodes
    centre_x=(x1+x2)/2
    centre_y=(y1+y2)/2
    centre_z=(z1+z2)/2
    centre = [centre_x,centre_y,centre_z]
    #get  the direction of the vector passing through these nodes - subtract the position vectors of the two nodes
    A = x2-x1
    B = y2-y1
    C = z2-z1

    #find a plane perpendicular to the element passing through the central point of the element
    #plane equation: Ax + By + Cz = D where vector N = (A, B, C) is the normal(perpendicular) to
    #the plane; N = direction of the element

    #find D by plugging in coordinates of the element's central point through which the plane passes
    D = A*centre_x + B*centre_y + C*centre_z

    #plane equation
    #A*x + B*y + C*z = D

    # get points in the blood vessel surface within a set radius from the centre of an element

    #radius set to 35 before rescaling; 4 after rescaling for large vessels, 2 for small vessels
    surface_points = point_tree.data[point_tree.query_ball_point(centre, 2)]

    if len(surface_points) > 0:

        # print surface points for element 0
        #if ((i == 0) or (i == 2) or (i == 5) or (i == 10)):
        #    df1 = pd.DataFrame(surface_points)
        #    filename = 'chorionic_vessels/surface_points_elem_' + str(i) + '.csv'
        #    df1.to_csv(filename)

        points_distance = pd.DataFrame(
            columns=['point_x', 'point_y', 'point_z', 'A', 'B', 'C', 'D', 'distance_to_plane', 'distance_to_centre'])


        for j in range(0, len(surface_points)):
            distance_to_plane = 0
            if (A * surface_points[j][0] + B * surface_points[j][1] + C * surface_points[j][2] == D):
                # the point is on the plane
                distance_to_plane = 0
            else:
                # the point is not on the plane
                distance_to_plane = get_point_to_plane_dist(surface_points[j], A, B, C, D)

            distance_to_centre = np.abs(np.sqrt(
                (centre_x - surface_points[j][0]) ** 2 + (centre_y - surface_points[j][1]) ** 2 + (
                centre_z - surface_points[j][2]) ** 2))
            points_distance.loc[j] = [surface_points[j][0], surface_points[j][1], surface_points[j][2], A, B, C, D,
                                  distance_to_plane, distance_to_centre]

        #if (i == 83):
        #    filename = 'points_distance_elem_' + str(i) + '.csv'
        #    points_distance.to_csv(filename)
        #    print ('centre', centre)
        #    print ('node1', [x1, y1, z1])
        #    print ('node2', [x2, y2, z2])

        # get points within 1 unit of the plane and more than 0 distance from centre
        radius_points = points_distance[(points_distance['distance_to_plane'] <= 1)
                                        & (points_distance['distance_to_centre'] > 0)].copy()
        num_points = len(radius_points)

        radius = 0
        mean_radius = 0
        shortest_radius = 0
        mean_as_percentage_of_shortest = 0
        short_radius_cutoff = 5
        mean_percentage_cutoff = 250

        if num_points > 0:
            radius_points.assign(alpha=np.zeros(num_points), alpha_sector=np.zeros(num_points),
                             beta=np.zeros(num_points),beta_sector=np.zeros(num_points),
                             epsilon=np.zeros(num_points),epsilon_sector=np.zeros(num_points))
            radius_points.index = range(0,num_points) #update indices

            for j in range(0,num_points):
                #get direction angles for each point on vessel surface in degrees and assign them to a sector with a set angle
                sector_angle = 22.5
                #length between the point and element centre
                length = radius_points.iloc[j]['distance_to_centre']
                alpha = np.degrees(np.arccos((radius_points.iloc[j]['point_x'] - centre[0])/length))
                radius_points.at[j, 'alpha'] = alpha
                beta = np.degrees(np.arccos((radius_points.iloc[j]['point_y'] - centre[1]) / length))
                radius_points.at[j, 'beta'] = beta
                epsilon = np.degrees(np.arccos((radius_points.iloc[j]['point_z'] - centre[2])/length))
                radius_points.at[j, 'epsilon'] = epsilon
                radius_points.at[j, 'alpha_sector'] = (alpha // sector_angle + 1)*sector_angle
                radius_points.at[j, 'beta_sector'] = (beta // sector_angle + 1)*sector_angle
                radius_points.at[j, 'epsilon_sector'] = (epsilon // sector_angle + 1)*sector_angle

            #if (i== 1907):
            #    filename = 'radius_points_elem_' + str(i) + '.csv'
            #    radius_points.to_csv(filename)

            #list radii within each sector
            radius_point_sectors = radius_points.groupby(['alpha_sector', 'beta_sector',
                                    'epsilon_sector']).distance_to_centre.apply(list).to_frame('sector_radii').reset_index()
            radius_point_sectors.assign(sector_mean_radius=np.zeros(len(radius_point_sectors)))

            #for each row in radius_point_sectors remove outliers from radius lengths within a sector
            for j in range(0,len(radius_point_sectors)):
                sector_radii = radius_point_sectors.iloc[j]['sector_radii']
                sector_radius = 0
                if len(sector_radii) > 1:
                    sector_radii_std = np.std(sector_radii)
                    sector_radii_mean = np.mean(sector_radii)
                    sector_radii_min = np.min(sector_radii)
                    sector_radii_no_outliers = []
                    #remove radii greater than two standard deviations from the minimum value
                    for k in range(0,len(sector_radii)):
                        if (sector_radii[k] <= sector_radii_min + 2*sector_radii_std):
                            sector_radii_no_outliers.append(sector_radii[k])
                    sector_radius = np.mean(sector_radii_no_outliers)
                elif len(sector_radii) == 0:
                    sector_radius = 0
                else: #len(sector_radii) == 1
                    sector_radius = sector_radii[0]

                radius_point_sectors.at[j,'sector_mean_radius'] = sector_radius

            radii = radius_point_sectors.iloc[:]['sector_mean_radius'].tolist()

            if len(radii) > 1:
                radii_std = np.std(radii)
                radii_mean = np.mean(radii)
                radii_no_outliers = []

                for j in range(0,len(radii)):
                    #exclude radii which are more than 2 standard deviations away from the mean
                    if (radii[j] > radii_mean - 2*radii_std) & (radii[j] < radii_mean + 2*radii_std):
                        radii_no_outliers.append(radii[j])
                mean_radius = np.mean(radii_no_outliers)
                shortest_radius = np.min(radii_no_outliers)
            elif len(radii) == 0:
                mean_radius = 0
                shortest_radius = 0
            else:
                mean_radius = radii[0]
                shortest_radius = radii[0]

            if (mean_radius > 0) & (shortest_radius > 0):
                mean_as_percentage_of_shortest = (mean_radius / shortest_radius) * 100

        # set radius to mean_radius unless mean_percentage is greater than cutoff and the shortest radius
        # is smaller than cutoff - use the shortest radius then

        if mean_radius > shortest_radius:
            if mean_as_percentage_of_shortest <= mean_percentage_cutoff:
                radius = mean_radius
            elif shortest_radius > short_radius_cutoff:
                radius = mean_radius
            else:
                radius = shortest_radius
        else:
            radius = shortest_radius

        elems_info_df.loc[i] = [centre_x, centre_y, centre_z, A, B, C, D, mean_radius, shortest_radius,
                                mean_as_percentage_of_shortest, radius, len(radius_points), len(points_distance)]
    else:

        elems_info_df.loc[i] = [centre_x, centre_y, centre_z, A, B, C, D, 0, 0,
                            0,0,0,0]

#print to csv
elems_info_df.to_csv('small_vessels/small_vessel_radius_cycle2_v1.csv')







