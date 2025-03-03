# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 21:05:45 2025

@author: tlee
"""
from birddb.database import getBirdDataBase
from birddb.plotting import plot_orders, plot_families, plot_genuses, plot_most_photographed
from birddb.plotting import plot_order_comp, plotPhyloTree
import polars as pl

import matplotlib.pyplot as plt

import os

db = getBirdDataBase('D:/Wildlife Photos/Birds/Classification',force_overwrite=False)
#db.add_unsorted_to_database('https://ebird.org/checklist/S216014746')
#db.sort()
#db.save()

#print(db.df)


#plot_orders(db,mode='photos')
#plot_orders(db,mode='species')
#plot_families(db,'Passeriformes',mode='photos')
#plot_genuses(db,'Anatidae',mode='photos')
plot_most_photographed(db,30)
#plot_order_comp(db,'Pelecaniformes',mode='photos')
#plotPhyloTree(db,mode='species',tree_style=2)






