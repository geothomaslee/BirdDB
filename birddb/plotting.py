# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 17:20:27 2025

@author: tlee
"""
import math

import polars as pl
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from collections import defaultdict

from birddb.plot_sankey import plot_sankey_tree

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

def plotPhyloTree(db,mode:str = 'Species',tree_style=1):
    plot_sankey_tree(db,mode=mode,tree_style=tree_style)

def plot_order_comp(db,order,mode: str='species'):
    if mode not in ('species','photos'):
        raise ValueError('Mode must be "species" or "photos"')
    df = db.df
    if mode == 'species':
        df = df.unique(subset=["Species"], keep="first")
    
    
    df = df.filter(pl.col('Order')==order)
    
    fams = sorted(list(set(df['Family'].to_list())))
    fam_counts = []
    for fam in fams:
        fam_counts.append(df.filter(pl.col('Family') == fam).height)
        
    all_gen_counts = []
    all_gen_names = []
    for fam in fams:
        gen_counts = []
        fam_df = df.filter(pl.col('Family')==fam)
        gens = sorted(list(set(fam_df['Genus'].to_list())))
        all_gen_names.append(gens)
        for gen in gens:
            gen_counts.append(fam_df.filter(pl.col('Genus')==gen).height)
        all_gen_counts.append(gen_counts)
        
    # Create color scheme
    # Get maximum number of genera in any family for color mapping
    max_genera = max(len(genera) for genera in all_gen_names)
    
    # Create color palette for outer ring (families)
    tab20c = plt.colormaps['tab20c']
    outer_colors = [tab20c(i * 4 / 20) for i in range(len(fams))]
    
    # Create color palettes for inner ring (genera)
    inner_colors = []
    for i, genera_count in enumerate(all_gen_counts):
        # Create a color range for each family's genera
        base_color = outer_colors[i]
        if len(genera_count) == 1:
            # If only one genus, use slightly darker version of family color
            inner_colors.extend([mcolors.rgb_to_hsv(base_color[:3])])
        else:
            # Create gradient of similar colors for multiple genera
            for j in range(len(genera_count)):
                # Modify the brightness/saturation but keep similar hue
                hsv_color = list(mcolors.rgb_to_hsv(base_color[:3]))
                hsv_color[1] *= 0.5 + 0.5 * (j + 1) / len(genera_count)  # Vary saturation
                hsv_color[2] *= 0.8 + 0.2 * (j + 1) / len(genera_count)  # Vary brightness
                inner_colors.append(hsv_color)
    
    # Convert HSV colors back to RGB
    inner_colors = [mcolors.hsv_to_rgb(color) for color in inner_colors]
    
    # Create the plot
    fig, ax = plt.subplots(dpi=144)
    size = 0.3
    
    # Plot outer ring (families)
    ax.pie(fam_counts, radius=1, colors=outer_colors,
           wedgeprops=dict(width=size, edgecolor='w'),
           labels=fams)
    
    # Flatten genus counts for inner ring
    counts = [item for sublist in all_gen_counts for item in sublist]
    
    # Plot inner ring (genera)
    ax.pie(counts, radius=1-size, colors=inner_colors,
           wedgeprops=dict(width=size, edgecolor='w'),
           labels=[item for sublist in all_gen_names for item in sublist])
    
    #flat_list = [item for sublist in nested_list for item in sublist]
    
    ax.set(aspect="equal", title=f'Distribution of Families and Genera in {order}')
    
    return fig, ax
    
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
    
