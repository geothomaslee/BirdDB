# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 11:23:55 2025

@author: tlee
"""
import os
import pandas as pd
import polars as pl
from collections import defaultdict

import plotly.graph_objects as go

def plot_sankey_tree(db, mode: str='species',tree_style=1,_debug: bool=True):
    df = db.df
    unique_df = df.unique(subset=["Species"], keep="first")
    unique_df = unique_df.drop('eBird_Checklist','Path','Wikipedia_URL','Scientific_Species','Capture_Date')
    
    unique_df = unique_df.with_columns(
        pl.lit("1").alias("Count"))
    
    if mode == 'photos':
        species = unique_df['Species'].to_list()
        for spec in species:
            count = df.filter(pl.col('Species') == spec).height
            unique_df = unique_df.with_columns(
                pl.when((pl.col("Species") == spec))
                .then(pl.lit(str(count)))
                .otherwise(pl.col("Count"))
                .alias("Count"))
            
    pl.Config.set_tbl_rows(120)
    
    unique_df = unique_df.sort(by=['Order','Family','Genus','Species'])

    orders = sorted(unique_df.unique(subset=["Order"], keep="first")['Order'].to_list())
    families = sorted(unique_df.unique(subset=["Family"], keep="first")['Family'].to_list())
    genera = sorted(unique_df.unique(subset=["Genus"], keep="first")['Genus'].to_list())
    species = sorted(unique_df.unique(subset=["Species"], keep="first")['Species'].to_list())

    # Values corresponding to the number of species within that order that are within each family
    class_order_values = _getSubCategoryCount(df,'Order',orders)
    order_fam_values = _getSubCategoryCount(df,'Family',families)
    fam_genus_values = _getSubCategoryCount(df,'Genus',genera)
    genus_species_values = _getSubCategoryCount(df,'Species',species)
    
    class_sources = []
    for order in orders:
        class_sources.append('Aves')
    
    order_sources = []
    for fam in families:
        order = unique_df.filter(pl.col('Family')==fam)['Order'].to_list()[0]
        order_sources.append(order)
    
 
    fam_sources = []
    for gen in genera:
        fam = unique_df.filter(pl.col('Genus')==gen)['Family'].to_list()[0]
        fam_sources.append(fam)
        
    gen_sources = []
    for spec in species:
        gen = unique_df.filter(pl.col('Species')==spec)['Genus'].to_list()[0]
        gen_sources.append(gen)
    
    
    pddf = pd.DataFrame({'source': class_sources + order_sources + fam_sources + gen_sources,
                         'target': orders + families + genera + species,
                         'value': class_order_values + order_fam_values + fam_genus_values + genus_species_values})
    
    
    pddf.to_csv('C:/Users/Blumenwitz/Downloads/example_taxo_df.csv')
    pd.set_option('display.max_rows', None)
    
    fig = _plotSankey(pddf,mode=tree_style)
    if not os.path.isdir(f'{db.dataFolder}/Figures'):
        os.mkdir(f'{db.dataFolder}/Figures')
    fig.write_html(f"{db.dataFolder}/Figures/bird_taxonomy_sankey.html")
        
    if _debug:
        if not os.path.isdir(f'{os.getcwd()}/Figures'):
            os.mkdir(f'{os.getcwd()}/Figures')
        fig.write_html(f"{os.getcwd()}/Figures/bird_taxonomy_sankey.html")
        
def _getSubCategoryCount(df,category,category_list):
    subcategoryCounts = []
    for cat in category_list:
        subcategoryCounts.append(df.filter(pl.col(category)==cat).height)
        
    return subcategoryCounts 

def _plotSankey(df,mode: int=1):
    if mode==1:
        return _plotSankeySimple(df)
    elif mode==2:
        return _plotSankeyComplex(df)
    else:
        raise ValueError('Mode must be either 1 for simple or 2 for complex')
    
def _plotSankeySimple(df):
    # Get unique labels from both source and target columns
    labels = list(pd.unique(df[['source', 'target']].values.ravel('K')))
    
    # Separate labels by taxonomic level
    source_unique = df['source'].unique()
    target_unique = df['target'].unique()
    
    # Create a dictionary to record taxonomic level for each node
    taxonomic_levels = {}
    
    # Identify the different levels (Aves, Order, Family, Genus, Species)
    taxonomic_levels['Aves'] = 0  # Root level
    
    # Identify Orders (direct children of Aves)
    orders = df[df['source'] == 'Aves']['target'].unique()
    for order in orders:
        taxonomic_levels[order] = 1
    
    # Identify Families (children of Orders)
    for order in orders:
        families = df[df['source'] == order]['target'].unique()
        for family in families:
            taxonomic_levels[family] = 2
    
    # Identify Genera (children of Families)
    families = df[df['source'].isin(taxonomic_levels.keys()) & (df['source'] != 'Aves') & ~df['source'].isin(orders)]['source'].unique()
    for family in families:
        genera = df[df['source'] == family]['target'].unique()
        for genus in genera:
            taxonomic_levels[genus] = 3
    
    # Identify Species (children of Genera) - these are at the end
    for label in labels:
        if label not in taxonomic_levels:
            taxonomic_levels[label] = 4  # Assume any remaining labels are species
    
    # Create x-coordinates based on taxonomic level
    x_positions = {}
    for label, level in taxonomic_levels.items():
        x_positions[label] = level * 0.2  # Scale factor for spacing
    
    # Map source and target names to their indices in the labels list
    source_indices = [labels.index(src) for src in df['source']]
    target_indices = [labels.index(tgt) for tgt in df['target']]
    
    # Create color scheme
    color_scale = {
        0: "rgba(31, 119, 180, 0.8)",    # Aves (blue)
        1: "rgba(255, 127, 14, 0.8)",    # Orders (orange)
        2: "rgba(44, 160, 44, 0.8)",     # Families (green)
        3: "rgba(214, 39, 40, 0.8)",     # Genera (red)
        4: "rgba(148, 103, 189, 0.8)"    # Species (purple)
    }
    
    # Create node colors based on taxonomic level
    node_colors = [color_scale[taxonomic_levels[label]] for label in labels]
    
    # Create link colors based on source taxonomic level
    link_colors = [color_scale[taxonomic_levels[df.loc[i, 'source']]] for i in df.index]
    
    # Create Sankey diagram with node positions
    fig = go.Figure(data=[go.Sankey(
        arrangement = "fixed",  # Use fixed arrangement with custom positions
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = labels,
            color = node_colors,
            x = [x_positions[label] for label in labels],  # Set x position based on taxonomic level
            y = None  # Let Plotly calculate y positions to avoid crossing
        ),
        link = dict(
            source = source_indices,
            target = target_indices,
            value = df['value'],
            color = link_colors
        )
    )])
    
    # Update layout
    fig.update_layout(
        title_text="Bird Taxonomy: From Orders to Species",
        font=dict(size=10),
        autosize=True,
        height=900,
        width=1200,
        margin=dict(t=60, l=25, r=25, b=25)
    )
    
    return fig    

"""
def _plotSankeyComplex(df):
    # Get unique labels from both source and target columns
    labels = list(pd.unique(df[['source', 'target']].values.ravel('K')))
    
    # Create a graph representation and identify levels
    graph = {}
    parents = {}
    children = defaultdict(list)
    
    for i, row in df.iterrows():
        source, target = row['source'], row['target']
        if source not in graph:
            graph[source] = []
        if target not in graph:
            graph[target] = []
        graph[source].append(target)
        parents[target] = source
        children[source].append(target)
    
    # Identify root (Aves) and build taxonomic levels
    root = 'Aves'  # Assuming 'Aves' is always the root
    
    # Traverse the tree to determine levels
    taxonomic_levels = {root: 0}
    level_nodes = defaultdict(list)
    level_nodes[0].append(root)
    
    queue = [root]
    while queue:
        node = queue.pop(0)
        current_level = taxonomic_levels[node]
        
        for child in graph.get(node, []):
            if child not in taxonomic_levels:
                taxonomic_levels[child] = current_level + 1
                level_nodes[current_level + 1].append(child)
                queue.append(child)
    
    # Get the maximum level
    max_level = max(taxonomic_levels.values())
    
    # Create optimized node ordering to minimize crossings
    def optimize_level(level, parent_order):
        nodes = level_nodes[level]
        if not nodes or level == 0:  # Skip for root level
            return nodes
        
        # Create a mapping of nodes to their parent's position
        node_parent_pos = {}
        for node in nodes:
            if node in parents:
                parent = parents[node]
                # Fix: ensure parent is in parent_order before trying to get its index
                if parent in parent_order:
                    parent_idx = parent_order.index(parent)
                    node_parent_pos[node] = parent_idx
                else:
                    # If parent not found in parent_order, assign a default position
                    node_parent_pos[node] = len(parent_order)  # Place at the end
            else:
                node_parent_pos[node] = 0
        
        # Sort nodes by their parent's position
        return sorted(nodes, key=lambda x: node_parent_pos.get(x, 0))
    
    # Optimize ordering level by level
    ordered_nodes = {}
    ordered_nodes[0] = [root]
    
    for level in range(1, max_level + 1):
        parent_level = level - 1
        ordered_nodes[level] = optimize_level(level, ordered_nodes[parent_level])
    
    # Create a flat list of optimized node order
    optimized_labels = []
    for level in range(0, max_level + 1):
        optimized_labels.extend(ordered_nodes[level])
    
    # Ensure all labels are included (there might be disconnected nodes)
    for label in labels:
        if label not in optimized_labels:
            optimized_labels.append(label)
    
    # Remap labels to their optimized positions
    label_map = {label: idx for idx, label in enumerate(optimized_labels)}
    
    # Map source and target indices based on the optimized order
    source_indices = [label_map[src] for src in df['source']]
    target_indices = [label_map[tgt] for tgt in df['target']]
    
    # Create x-coordinates based on taxonomic level
    x_positions = {}
    for label in optimized_labels:
        level = taxonomic_levels.get(label, 0)
        x_positions[label] = level * 0.2  # Scale factor for spacing
    
    # Create y-coordinates based on optimized positions within each level
    y_positions = {}
    for level in range(0, max_level + 1):
        nodes = ordered_nodes[level]
        total_nodes = len(nodes)
        if total_nodes > 0:
            for i, node in enumerate(nodes):
                # Distribute nodes evenly within each level
                # Add small offset to avoid potential division by zero
                y_positions[node] = i / max(1, total_nodes - 1 + 0.001) if total_nodes > 1 else 0.5
                
    print(x_positions['Accipitriformes'])
    print(x_positions['Pelecaniformes'])
    
    print(y_positions['Accipitriformes'])
    print(y_positions["Cooper's hawk"])
    print(y_positions['Suliformes'])
    
    # Create color scheme by level
    color_scale = {
        0: "rgba(31, 119, 180, 0.8)",    # Aves (blue)
        1: "rgba(255, 127, 14, 0.8)",    # Orders (orange)
        2: "rgba(44, 160, 44, 0.8)",     # Families (green)
        3: "rgba(214, 39, 40, 0.8)",     # Genera (red)
        4: "rgba(148, 103, 189, 0.8)"    # Species (purple)
    }
    
    # Apply colors based on taxonomy level
    node_colors = [color_scale[taxonomic_levels.get(label, 0)] for label in optimized_labels]
    
    # Create Sankey diagram with optimized positions
    fig = go.Figure(data=[go.Sankey(
        arrangement = "fixed",
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = optimized_labels,
            color = node_colors,
            x = [x_positions.get(label, 0) for label in optimized_labels],
            y = [y_positions.get(label, 0.5) for label in optimized_labels]
        ),
        link = dict(
            source = source_indices,
            target = target_indices,
            value = df['value'],
            color = [color_scale[taxonomic_levels.get(df.loc[i, 'source'], 0)] for i in df.index]
        )
    )])
    
    # Update layout
    fig.update_layout(
        title_text="Bird Taxonomy: From Orders to Species",
        font=dict(size=10),
        autosize=True,
        height=1000,
        width=1400,
        margin=dict(t=60, l=25, r=25, b=25)
    )
    
    return fig
"""
def _plotSankeyComplex(df):
    # Get unique labels from both source and target columns
    labels = list(pd.unique(df[['source', 'target']].values.ravel('K')))
    
    # Create a graph representation and identify levels
    graph = {}
    parents = {}
    children = defaultdict(list)
    
    for i, row in df.iterrows():
        source, target = row['source'], row['target']
        if source not in graph:
            graph[source] = []
        if target not in graph:
            graph[target] = []
        graph[source].append(target)
        parents[target] = source
        children[source].append(target)
    
    # Identify root (Aves) and build taxonomic levels
    root = 'Aves'  # Assuming 'Aves' is always the root
    
    # Traverse the tree to determine levels
    taxonomic_levels = {root: 0}
    level_nodes = defaultdict(list)
    level_nodes[0].append(root)
    
    queue = [root]
    while queue:
        node = queue.pop(0)
        current_level = taxonomic_levels[node]
        
        for child in graph.get(node, []):
            if child not in taxonomic_levels:
                taxonomic_levels[child] = current_level + 1
                level_nodes[current_level + 1].append(child)
                queue.append(child)
    
    # Get the maximum level
    max_level = max(taxonomic_levels.values())
    
    # Create optimized node ordering to minimize crossings
    def optimize_level(level, parent_order):
        nodes = level_nodes[level]
        if not nodes or level == 0:  # Skip for root level
            return nodes
        
        # Create a mapping of nodes to their parent's position
        node_parent_pos = {}
        for node in nodes:
            if node in parents:
                parent = parents[node]
                if parent in parent_order:
                    parent_idx = parent_order.index(parent)
                    node_parent_pos[node] = parent_idx
                else:
                    node_parent_pos[node] = 0
            else:
                node_parent_pos[node] = 0
        
        # Sort nodes by their parent's position
        return sorted(nodes, key=lambda x: node_parent_pos.get(x, 0))
    
    # Optimize ordering level by level
    ordered_nodes = {}
    ordered_nodes[0] = [root]
    
    for level in range(1, max_level + 1):
        parent_level = level - 1
        ordered_nodes[level] = optimize_level(level, ordered_nodes[parent_level])
    
    # Create a flat list of optimized node order
    optimized_labels = []
    for level in range(0, max_level + 1):
        optimized_labels.extend(ordered_nodes[level])
    
    # Ensure all labels are included (there might be disconnected nodes)
    for label in labels:
        if label not in optimized_labels:
            optimized_labels.append(label)
    
    # Remap labels to their optimized positions
    label_map = {label: idx for idx, label in enumerate(optimized_labels)}
    
    # Map source and target indices based on the optimized order
    source_indices = [label_map[src] for src in df['source']]
    target_indices = [label_map[tgt] for tgt in df['target']]
    
    # Create x-coordinates based on taxonomic level
    x_positions = {}
    for label, level in taxonomic_levels.items():
        x_positions[label] = level * 0.2  # Scale factor for spacing
    
    # Create y-coordinates based on optimized positions within each level
    y_positions = {}
    for level in range(0, max_level + 1):
        nodes = ordered_nodes[level]
        total_nodes = len(nodes)
        
        if total_nodes > 1:
            # Define buffer to avoid exact 0 and 1 positions
            buffer = 0.05  # 5% buffer on top and bottom
            usable_range = 1.0 - (2 * buffer)  # Usable range for positioning
            
            for i, node in enumerate(nodes):
                # Distribute nodes evenly with buffer on top and bottom
                normalized_position = i / (total_nodes - 1) if total_nodes > 1 else 0.5
                y_positions[node] = buffer + (normalized_position * usable_range)
        else:
            # If only one node at this level, place it in the middle
            for node in nodes:
                y_positions[node] = 0.5
    
    # Make sure all labels have y positions (fallback for any missing)
    for label in optimized_labels:
        if label not in y_positions:
            y_positions[label] = 0.5  # Default to middle
    
    # Create color scheme by level
    color_scale = {
        0: "rgba(31, 119, 180, 0.8)",    # Aves (blue)
        1: "rgba(255, 127, 14, 0.8)",    # Orders (orange)
        2: "rgba(44, 160, 44, 0.8)",     # Families (green)
        3: "rgba(214, 39, 40, 0.8)",     # Genera (red)
        4: "rgba(148, 103, 189, 0.8)"    # Species (purple)
    }
    
    # Apply colors based on taxonomy level
    node_colors = [color_scale[taxonomic_levels.get(label, 0)] for label in optimized_labels]
    
    # Create Sankey diagram with optimized positions
    fig = go.Figure(data=[go.Sankey(
        arrangement = "fixed",
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = optimized_labels,
            color = node_colors,
            x = [x_positions.get(label, 0) for label in optimized_labels],
            y = [y_positions.get(label, 0.5) for label in optimized_labels]
        ),
        link = dict(
            source = source_indices,
            target = target_indices,
            value = df['value'],
            color = [color_scale[taxonomic_levels.get(df.loc[i, 'source'], 0)] for i in df.index]
        )
    )])
    
    # Update layout
    fig.update_layout(
        title_text="Bird Taxonomy: From Orders to Species",
        font=dict(size=10),
        autosize=True,
        height=1000,
        width=1400,
        margin=dict(t=60, l=25, r=25, b=25)
    )
    
    return fig