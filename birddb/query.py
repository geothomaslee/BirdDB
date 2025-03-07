# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 17:58:36 2025

@author: tlee
"""
import shutil
import os
import re
from datetime import datetime
from glob import glob

import polars as pl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from tqdm import tqdm

from birddb.database import BirdDataBase

class TooManyPhotosError(Exception):
    pass

class Query():
    def __init__(self, db: BirdDataBase, search,flexible: bool=False):
        self.db = db
        if isinstance(search,str):
            self.df = self._search_str(db, search)
        if isinstance(search, list):
            self.df = self._search_list(db, search)
        if isinstance(search, dict):
            self.df = self._search_dict(db, search)

    def __str__(self):
        return str(self.df)

    def _search_str(self, db, search,cols=None):
        df = db.df
        if cols is None:
            cols = df.columns
        clean_search = search.replace('-', '').replace(' ', '').lower()
        exprs = [pl.col(col).str.replace_all(r"[-\s]", "").str.to_lowercase().str.contains(clean_search) for col in cols]
        return df.filter(pl.any_horizontal(exprs))

    def _search_list(self,db,search):
        for i, _src in enumerate(search):
            if not isinstance(_src, str):
                raise TypeError('If query is given a list, items in list must be strings')
            if i == 0:
                df = self._search_str(db,_src)
                continue
            df = pl.concat([df,self._search_str(db,_src)],how='vertical')
        return df

    def _search_dict(self,db,search):
        for key in search:
            if key not in db.df.columns:
                raise ValueError(f'Could not find column {key}')

        for i, (k, v) in enumerate(search.items()):
            if i == 0:
                df = self._search_str(db,v,cols=[k])
                continue
            df = pl.concat([df,self._search_str(db,v,cols=[k])],how='vertical')
        return df

    def show_images(self,photo_limit=10):
        imgs =self.df['Path'].to_list()
        if len(imgs) > photo_limit:
            raise TooManyPhotosError('WARNING: Too many photos called. Set photo_limit higher to plot more')

        for img in imgs:
            fig, ax = plt.subplots()
            ax.imshow(mpimg.imread(img))
            ax.set_axis_off()
            plt.show()

    def deposit(self,photo_limit=20):
        imgs = self.df['Path'].to_list()
        if len(imgs) > photo_limit:
            raise TooManyPhotosError('WARNING: Too many photos called. Set photo_limit higher to plot more')

        dep_dir = f'{self.db.dataFolder}/Query-{datetime.now().strftime("%Y-%m-%d--%H.%M.%S")}'
        os.mkdir(dep_dir)

        print(f'Depositing queried photos to {dep_dir}...')
        for img in tqdm(imgs):
            shutil.copy(img,f'{dep_dir}')

    def clear(self):
        query_list = glob(f'{self.db.dataFolder}/Query-*')
        for q in query_list:
            shutil.rmtree(q)

