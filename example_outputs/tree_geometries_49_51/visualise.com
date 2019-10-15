#patient 51

#to produce the following images:
#skeleton graph of the large vessels in white and a cloud of points in the skeleton of the small vessels based on high fidelity images
#p51 vessel skeleton based on high fidelity images
gfx create material yellow diffuse 0.9 0.7 0.0 alpha 0.4;
gfx read data placenta_p51_point_cloud/all_vessels_skeleton_transformed region vessel_surface;
gfx modify g_element vessel_surface data_points coordinate coordinates material yellow point_size 1;

#p51 chorionic vessels
gfx read node placenta_p51_chorion/p51_chor_tree_2_inlets reg chor_tree;
gfx read elem placenta_p51_chorion/p51_chor_tree_2_inlets reg chor_tree;
gfx modify g_element chor_tree lines coordinate coordinates material default line_width 2;

#Heterogeneous distribution of grown vessels (small vessels in white and large vessels in green)
#p51 chorionic vessels
gfx read node placenta_p51_chorion/p51_chor_tree_2_inlets reg chor_tree;
gfx read elem placenta_p51_chorion/p51_chor_tree_2_inlets reg chor_tree;
gfx modify g_element chor_tree lines coordinate coordinates material green line_width 2;
#p51 remaining vessels
gfx read node placenta_p51_full_tree/full_tree reg tree;
gfx read elem placenta_p51_full_tree/full_tree reg tree;
gfx modify g_element tree lines coordinate coordinates material default;


#patient 49
#to produce the following image:
#skeleton graph of the large vessels in white and a cloud of points in the skeleton of the small vessels based on high fidelity images
#p49 vessel skeleton based on high fidelity images
gfx create material yellow diffuse 0.9 0.7 0.0 alpha 0.4;
gfx read data placenta_p49_point_cloud/p49_all_vessels_skeleton_transformed region vessel_surface;
gfx modify g_element vessel_surface data_points coordinate coordinates material yellow point_size 1;

#p49 chorionic vessels
gfx read node placenta_p49_chorion/p49_large_vessels_v3 reg chor_tree;
gfx read elem placenta_p49_chorion/p49_large_vessels_v3 reg chor_tree;
gfx modify g_element chor_tree lines coordinate coordinates material default line_width 2;


#Heterogeneous distribution of grown vessels (small vessels in white and large vessels in green)
#p49 chorionic vessels
gfx read node placenta_p49_chorion/p49_large_vessels_v3 reg chor_tree;
gfx read elem placenta_p49_chorion/p49_large_vessels_v3 reg chor_tree;
gfx modify g_element chor_tree lines coordinate coordinates material green line_width 2;
#p51 remaining vessels
gfx read node placenta_p49_full_tree/full_tree reg tree;
gfx read elem placenta_p49_full_tree/full_tree reg tree;
gfx modify g_element tree lines coordinate coordinates material default;

gfx cre win;
