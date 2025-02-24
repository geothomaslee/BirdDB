# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 17:20:27 2025

@author: tlee
"""

import polars as pl
import matplotlib.pyplot as plt
import numpy as np

def plot_orders(db,mode: str='species'):
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
    
def plot_families(db, order, mode: str='species'):
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
    ax.pie(counts, labels=fams,colors=colors, autopct='%1.1f%%',
           wedgeprops={'linewidth': 2.0, 'edgecolor': 'white'},)
    
    if mode == 'species':
        ax.set_title('Unique Species')
    if mode == 'photos':
        ax.set_title('Times Photographed')
    plt.show()
    
def plot_genuses(db, family, mode: str='species'):
    if mode not in ('species','photos'):
        raise ValueError('Mode must be "species" or "photos"')
    df = db.df
    if mode == 'species':
        df = df.unique(subset=["Species"], keep="first")
        
    df = df.filter(pl.col('Family')==family)
    
    gens = set(df['Genus'].to_list())
    gens = sorted(list(gens))
    counts = []
    for gen in gens:
        counts.append(df.filter(pl.col('Genus') == gen).height)
        
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    fig, ax = plt.subplots()
    plt.suptitle(f'Genuses Photographed in Family {gen}')
    ax.pie(counts, labels=gens,colors=colors, autopct='%1.1f%%',
           wedgeprops={'linewidth': 2.0, 'edgecolor': 'white'},)
    
    if mode == 'species':
        ax.set_title('Unique Species')
    if mode == 'photos':
        ax.set_title('Times Photographed')
    plt.show()
    
    
def plot_most_photographed(db,n: int=10):
    df = db.df
    
    species = df.unique(subset=["Species"], keep="first")['Species'].to_list()
    spec_dict = {}
    for specie in species:
        spec_dict[specie] = df.filter(pl.col('Species') == specie).height
        
    spec_dict = dict_sorted = dict(sorted(spec_dict.items(), key=lambda x: x[1], reverse=True))
    spec_dict = dict(list(spec_dict.items())[:n])
    
    for spec in spec_dict:
        if list(spec_dict.values())[-1] == list(spec_dict.values())[-2]:
            new_dict = {key: val for key, val in spec_dict.items() if val != list(spec_dict.values())[-1]}
            
    species = list(new_dict.keys())
    counts = list(new_dict.values())      
    
    rotation = 55
            
    fig, ax = plt.subplots()
    ax.bar(species,counts)
    ax.set_title('Most Photographed Species')
    ax.set_ylabel('Times Photographed')
    plt.xticks(rotation=rotation,
               ha='right' if rotation < 90 else 'center')
    plt.show()
    
def plot_species_tree(db):
    pass
    
   
