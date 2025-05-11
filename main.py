# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 21:05:45 2025

@author: tlee
"""
from birddb.database import getBirdDataBase
import polars as pl

db = getBirdDataBase('D:/Wildlife Photos/Birds/Classification',force_overwrite=False)
db.sort_new('https://ebird.org/checklist/S235566653')

#qu.search('Purple gallinule')
#print(qu.df)
#qu.deposit(60)

#db.plot(plot_type='photos over time',mode='species')

#=====================Bird DB planned features list============================
# Get much clearer list of actually required libraries









