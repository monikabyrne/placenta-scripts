#!/usr/bin/env python

import placentagen as pg
import numpy as np
import pandas as pd
from scipy.stats.stats import pearsonr,spearmanr
import numpy as np
import matplotlib.pyplot as plt

path = 'full_tree_patient_51_21_v2/'


terminal_flow_by_generation = pd.read_csv(path + 'terminal flow per generation.csv')
generations = terminal_flow_by_generation.iloc[:]['generation'].tolist()
flow_by_generation = terminal_flow_by_generation.iloc[:]['terminal_blood_flow'].tolist()

print('Pearson correlation of blood flow flow and generation at terminal branch: '
      + str(pearsonr(generations,flow_by_generation)))

print ('Spearman correlation of blood flow and generation at terminal branch: '+
       str(spearmanr(generations,flow_by_generation)))


plt.scatter(generations,flow_by_generation)
heading = 'Terminal blood flow and branching generation'
plt.title(heading)
plt.show()


#plot arterial vessel diameter by Strahler order
art_diameter_by_strahler = pd.read_csv(path + 'mean_arterial_diameter_by_strahler.csv')
strahler_orders = art_diameter_by_strahler.iloc[:]['Strahler_order'].tolist()

n_groups = len(strahler_orders)

mean_diameters = art_diameter_by_strahler.iloc[:]['mean_diameter'].tolist()
std_diameters = art_diameter_by_strahler.iloc[:]['std'].tolist()

fig, ax = plt.subplots()

index = np.arange(n_groups)
bar_width = 0.35

opacity = 0.4
error_config = {'ecolor': '0.3'}

rects1 = ax.bar(index, mean_diameters, bar_width,
                alpha=opacity, color='g',
                yerr=std_diameters, error_kw=error_config,
                label='Branch diameter')


ax.set_xlabel('Strahler order')
ax.set_ylabel('Branch diameter (mm)')
ax.set_title('Arterial branch diameter by Strahler order')
ax.set_xticks(index + bar_width / 2)
ax.set_xticklabels(strahler_orders)
ax.legend()

fig.tight_layout()
plt.show()

#plot the number of arterial elements by Strahler order

num_elems = art_diameter_by_strahler.iloc[:]['number_of_elements'].tolist()

fig, ax = plt.subplots()

index = np.arange(n_groups)
bar_width = 0.35

opacity = 0.4

rects1 = ax.bar(index, num_elems, bar_width,
                alpha=opacity, color='b',
                label='Branch diameter')


ax.set_xlabel('Strahler order')
ax.set_ylabel('Number of elements')
ax.set_title('Number of arterial elements by Strahler order')
ax.set_xticks(index + bar_width / 2)
ax.set_xticklabels(strahler_orders)
ax.legend()

fig.tight_layout()
plt.show()
