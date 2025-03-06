# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 21:05:45 2025

@author: tlee
"""
from birddb.database import getBirdDataBase
import polars as pl

db = getBirdDataBase('D:/Wildlife Photos/Birds/Classification',force_overwrite=False)
db.sort_new('https://ebird.org/checklist/S216728975')





qu = db.search('Tufted titmouse')
qu.show_images()





#db.sort_new('https://ebird.org/checklist/S216056879')

#=====================Bird DB planned features list============================
# Fix bug with genus
# Photography taken over time
#   Stacked bar chart of orders would be cool
# Ability to actually display photos
# Query functions so you can search for species without having to known how DataFrames work
#   Strings as single queries
#   Dictionary where key=column and value=value, and return all matching values?
#   Ability to display photos that are queried, or move them to a directory for better viewing ability
# Get much clearer list of actually required libraries









