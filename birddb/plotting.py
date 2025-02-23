# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 17:20:27 2025

@author: tlee
"""

import polars as pl
import matplotlib.pyplot as plt

def plot_order(db,mode: str='species'):
    if mode not in ('species','photos'):
        raise ValueError('Mode must be "species" or "photos"')
    df = db.df
    if mode == 'species':
        df = df.unique(subset=["Species"], keep="first")
        
    orders = set(df['Order'].to_list())
    orders.remove(None)
    orders = sorted(list(orders))
    counts = []
    for order in orders:
        counts.append(df.filter(pl.col('Order') == order).height)
        
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    fig, ax = plt.subplots()
    ax.pie(counts, labels=orders,colors=colors, autopct='%1.1f%%')
    if mode == 'species':
        ax.set_title('Orders Photographed\nUnique Species')
    if mode == 'photos':
        ax.set_title('Orders Photographed\nTimes Photographed')
    plt.show()
    
def plot_family(db, order, mode: str='species'):
    if mode not in ('species','photos'):
        raise ValueError('Mode must be "species" or "photos"')
    df = db.df
    if mode == 'species':
        df = df.unique(subset=["Species"], keep="first")
        
    df = df.filter(pl.col('Order')==order)
    
    fams = set(df['Family'].to_list())
    fams = sorted(list(fams))
    counts = []
    for fam in fams:
        counts.append(df.filter(pl.col('Family') == fam).height)
        
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    fig, ax = plt.subplots()
    plt.suptitle(f'Families Photographed in Order {order}')
    ax.pie(counts, labels=fams,colors=colors, autopct='%1.1f%%')
    if mode == 'species':
        ax.set_title('Unique Species')
    if mode == 'photos':
        ax.set_title('Times Photographed')
    plt.show()
    
def plot_most_photographed(db):
    df = db.df
    species = df.unique(subset=["Species"], keep="first")['Species'].to_list()
    spec_dict = {}
    for specie in species:
        spec_dict[specie] = df.filter(pl.col('Species') == specie).height
        
    spec_dict = dict_sorted = dict(sorted(spec_dict.items(), key=lambda x: x[1], reverse=True))
    
    print(spec_dict)
    
   
