# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 17:58:36 2025

@author: tlee
"""
import polars as pl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from birddb.database import BirdDataBase

class TooManyPhotosError(Exception):
    pass

class Query():
    def __init__(self, db: BirdDataBase, search,flexible: bool=False):
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
            image = mpimg.imread(img)
            plt.imshow(image)
            plt.show()
