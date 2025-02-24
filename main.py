# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 21:05:45 2025

@author: tlee
"""

from birddb.database import getBirdDataBase
from birddb.plotting import plot_orders, plot_families, plot_genuses, plot_most_photographed
import polars as pl

db = getBirdDataBase('D:/Wildlife Photos/Birds/Classification',force_overwrite=False)
#db.add_unsorted_to_database(ebird='https://ebird.org/checklist/S215103770')
#db.sort()
#db.save()

#print(db.df)


#plot_order(db,mode='photos')
#plot_order(db,mode='species')
#plot_families(db,'Anseriformes',mode='photos')
#plot_genuses(db,'Anatidae',mode='photos')
plot_most_photographed(db,20)



