# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 21:05:45 2025

@author: tlee
"""

from birddb.database import BirdDataBase
import polars as pl
#db = BirdDataBase(datafolder='D://Wildlife Photos/Birds/Classification')
#pl.Config.set_tbl_rows(5)

db = BirdDataBase()
db.add_bulk_to_database('D:\Wildlife Photos\Birds\Classification')

print(db.df)
