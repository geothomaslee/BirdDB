# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 21:05:45 2025

@author: tlee
"""

from birddb.database import getBirdDataBase
from birddb.plotting import plot_order, plot_family, plot_most_photographed
import polars as pl

db = getBirdDataBase('D:/Wildlife Photos/Birds/Classification',force_overwrite=True)

db.add_unsorted_to_database(ebird='https://ebird.org/checklist/S210041434')
db.sort()
db.save()

print(db.df)

#plot_order(db,mode='photos')
#plot_order(db,mode='species')
#plot_family(db,'Pelecaniformes',mode='photos')
#plot_most_photographed(db)


