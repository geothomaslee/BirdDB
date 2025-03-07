# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 21:05:45 2025

@author: tlee
"""
from birddb.database import getBirdDataBase
import polars as pl

db = getBirdDataBase('D:/Wildlife Photos/Birds/Classification',force_overwrite=False)
#db.sort_new('https://ebird.org/checklist/S216728975')

from birddb.plotting import plot_orders_over_time
plot_orders_over_time(db)



#db.sort_new('https://ebird.org/checklist/S216056879')

#=====================Bird DB planned features list============================
# Photography taken over time
#   Stacked bar chart of orders would be cool
# Get much clearer list of actually required libraries









