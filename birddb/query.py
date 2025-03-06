# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 17:58:36 2025

@author: tlee
"""
import shutil
import os
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
            self._search_str(db.df, search)

    def __str__(self):
        return str(self.df)

    def _search_str(self,df, search):
        self.df = df.filter(pl.any_horizontal(pl.all().eq(search)))

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

