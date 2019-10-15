#!/usr/bin/env python

import placentagen as pg
import numpy as np
import pandas as pd
from scipy.stats.stats import pearsonr,spearmanr
import numpy as np
import matplotlib.pyplot as plt


from os.path import expanduser

home = expanduser("~")
#parameters
path1 = home + '/placenta_patient_49/results/p49_heterogeneous'
path2 = home + '/placenta_patient_49/results/p49_uniform'


def get_stats(path,column_name,sd_exists):

    tree1_stats = pd.read_csv(path + '/all_branch_stats_by_Strahler_order.csv')
    max_orders = len(tree1_stats) - 1  # last row contains totals

    orders = tree1_stats.iloc[:-1]['Strahler_order'].tolist()  # don't load the last totals row
    strahler_orders = map(int, orders)
    print strahler_orders

    # n_groups = len(strahler_orders)

    mean_measure_sd = tree1_stats.iloc[:-1][column_name].tolist()
    mean_measure = np.zeros(max_orders)
    sd_measure = np.zeros(max_orders)

    if (sd_exists):
        for i in range(0, max_orders):
                values = mean_measure_sd[i].split()  # split the mean and sd values
                mean_measure[i] = values[0]
                sd = values[1]
                sd = sd[1:-1]  # remove brackets
                sd_measure[i] = sd
    else:
        mean_measure = mean_measure_sd

    return mean_measure, sd_measure


def plot_measure(mean_measure1, sd_measure1,mean_measure2, sd_measure2,label1,label2,ylabel,title):

    ind = np.arange(len(mean_measure1))  # the x locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind + 1 - width / 2, mean_measure1, width, yerr=sd_measure1,
                    color='SkyBlue', label=label1)
    rects2 = ax.bar(ind + 1 + width / 2, mean_measure2, width, yerr=sd_measure2,
                    color='IndianRed', label=label2)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(ind + 1)
    #ax.set_xticklabels(('G1', 'G2', 'G3', 'G4', 'G5'))
    ax.legend()

    def autolabel(rects, xpos='center'):
        """
        Attach a text label above each bar in *rects*, displaying its height.

        *xpos* indicates which side to place the text w.r.t. the center of
        the bar. It can be one of the following {'center', 'right', 'left'}.
        """

        xpos = xpos.lower()  # normalize the case of the parameter
        ha = {'center': 'center', 'right': 'left', 'left': 'right'}
        offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off

        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() * offset[xpos], 1.01 * height,
                    '{}'.format(height), ha=ha[xpos], va='bottom')

    #autolabel(rects1, "left")
    #autolabel(rects2, "right")

    plt.show()

    return 0

def adjust_array_length(series1,series2):
    if len(series1) > len(series2):
        # pad series2 with 0s
        for i in range(0, len(series1)-len(series2)):
            series2 = np.append(series2, 0)

    if len(series1) < len(series2):
        #pad series1 with 0s
        for i in range(0, len(series2)-len(series1)):
            series1 = np.append(series1, 0)

    return series1, series2


print('path1 = ' + path1)
print('path2 = ' + path2)

#load stats
sd_exists = 1
(mean_length1,sd_length1) = get_stats(path1,'branch_length (sd)',sd_exists)
print 'path1'
print 'mean length by Strahler order ' + str(mean_length1)
(mean_length2,sd_length2) = get_stats(path2,'branch_length (sd)',sd_exists)
print 'path2'
print 'mean length by Strahler order ' + str(mean_length2)
(mean_length1,mean_length2) = adjust_array_length(mean_length1,mean_length2)
(sd_length1,sd_length2) = adjust_array_length(sd_length1,sd_length2)

label1 = 'Heterogeneous'
label2 = 'Uniform'
ylabel = 'Mean length'
title = 'Mean length by Strahler order'
plot_measure(mean_length1,sd_length1,mean_length2,sd_length2,label1,label2,ylabel,title)

sd_exists = 1
(mean_diameter1,sd_diameter1) = get_stats(path1,'branch_diameter (sd)',sd_exists)
print 'path1'
print 'mean diameter by Strahler order ' + str(mean_diameter1)
(mean_diameter2,sd_diameter2) = get_stats(path2,'branch_diameter (sd)',sd_exists)
print 'path2'
print 'mean diameter by Strahler order ' + str(mean_diameter2)
(mean_diameter1,mean_diameter2) = adjust_array_length(mean_diameter1,mean_diameter2)
(sd_diameter1,sd_diameter2) = adjust_array_length(sd_diameter1,sd_diameter2)

label1 = 'Heterogeneous'
label2 = 'Uniform'
ylabel = 'Mean diameter'
title = 'Mean diameter by Strahler order'
plot_measure(mean_diameter1,sd_diameter1,mean_diameter2,sd_diameter2,label1,label2,ylabel,title)


sd_exists = 0
(number_of_branches1,dummy_sd1) = get_stats(path1,'number_of_branches',sd_exists)
print 'path1'
print 'number of branches by Strahler order ' + str(number_of_branches1)
(number_of_branches2,dummy_sd2) = get_stats(path2,'number_of_branches',sd_exists)
print 'path2'
print 'number of branches by Strahler order ' + str(number_of_branches2)
(number_of_branches1,number_of_branches2) = adjust_array_length(number_of_branches1,number_of_branches2)
(dummy_sd1,dummy_sd2) = adjust_array_length(dummy_sd1,dummy_sd2)

label1 = 'Heterogeneous'
label2 = 'Uniform'
ylabel = 'Number of branches'
title = 'Number of branches by Strahler order'
plot_measure(number_of_branches1,dummy_sd1,number_of_branches2,dummy_sd2,label1,label2,ylabel,title)