# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 11:23:55 2025

@author: tlee
"""
import os
import pandas as pd
import polars as pl
from polars import DataFrame
from collections import defaultdict

import plotly.graph_objects as go
from birddb.sorting import get_photo_count

def plot_sankey_tree(db, mode: str='species',tree_style=1,_debug: bool=True):
    df = db.df
    unique_df = get_photo_count(df)
    unique_df = unique_df.drop('eBird_Checklist','Path','Wikipedia_URL','Scientific_Species','Capture_Date')

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

    fig = plotSankey(pddf,unique_df)
    if not os.path.isdir(f'{db.dataFolder}/Figures'):
        os.mkdir(f'{db.dataFolder}/Figures')

    fig.update_layout(dragmode='zoom')
    fig.write_html(f"{db.dataFolder}/Figures/bird_taxonomy_sankey.html",
               include_plotlyjs=True,
               full_html=True,
               config={
                   'responsive': True,
                   'scrollZoom': True,
                   'displayModeBar': True,
                   'modeBarButtonsToAdd': ['pan2d', 'zoom2d']
               })

    if _debug:
        if not os.path.isdir(f'{os.getcwd()}/Figures'):
            os.mkdir(f'{os.getcwd()}/Figures')
        fig.write_html(f"{os.getcwd()}/Figures/bird_taxonomy_sankey.html")

def _getSubCategoryCount(df,category,category_list):
    subcategoryCounts = []
    for cat in category_list:
        subcategoryCounts.append(df.filter(pl.col(category)==cat).height)

    return subcategoryCounts

def plotSankey(df, full_df, node_spacing: float=0.015):
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

    # Calculate node values (weight) based on incoming/outgoing links
    node_values = {}
    for label in labels:
        # Calculate node value as max of incoming or outgoing links
        incoming_sum = df[df['target'] == label]['value'].sum()
        outgoing_sum = df[df['source'] == label]['value'].sum()
        node_values[label] = max(incoming_sum, outgoing_sum)

    # Create y-coordinates based on level-specific spreading factor
    # Add a parameter for node spacing
    # Spacing between nodes (as a fraction of the total height)
    y_positions = {}
    buffer = 0.005  # Buffer to avoid exact 0 and 1 positions
    level_spread_factors = {}

    # Define spread factors for each level - higher levels have smaller spreads
    for level in range(max_level + 1):
        # Exponential spread - higher taxonomic levels are more compact
        level_spread_factors[level] = 0.7 ** (max_level - level)

    # Position nodes level by level
    for level in range(max_level + 1):
        nodes = ordered_nodes[level]
        if not nodes:
            continue

        # For root (level 0), just center it
        if level == 0:
            y_positions[nodes[0]] = 0.5
            continue

        # Get spread factor for this level
        spread = level_spread_factors[level]

        # Calculate total weight for this level
        total_weight = sum(node_values.get(node, 1) for node in nodes)

        # First pass: calculate relative heights based on node values
        node_heights = {}
        for node in nodes:
            relative_height = (node_values.get(node, 1) / total_weight) if total_weight > 0 else (1/len(nodes))
            # Scale by the spread factor
            node_heights[node] = relative_height * spread

        # Calculate the total spacing needed between nodes
        total_spacing = node_spacing * (len(nodes) - 1)

        # Calculate the total height needed (including spacing)
        total_height = sum(node_heights.values()) + total_spacing

        # If total exceeds available space, rescale the node heights (but keep spacing fixed)
        if total_height > (1.0 - 2*buffer):
            available_height = 1.0 - 2*buffer - total_spacing
            node_height_sum = sum(node_heights.values())
            scale_factor = available_height / node_height_sum
            node_heights = {node: height * scale_factor for node, height in node_heights.items()}
            total_height = available_height + total_spacing

        # Calculate starting position (centered)
        start_pos = 0.5 - (total_height / 2)

        # Second pass: position nodes with fixed spacing
        current_pos = start_pos
        for node in nodes:
            height = node_heights[node]
            # Center of node is current position + half the node's height
            center_pos = current_pos + (height / 2)
            # Ensure we're within bounds
            y_positions[node] = max(buffer, min(1.0 - buffer, center_pos))
            # Move to next position with spacing
            current_pos += height + node_spacing

    # Fix boundary condition of first node
    x_positions['Aves'] = 0.001

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

    # Update Layout
    fig.update_layout(title={'text': 'Taxonomy of Photograped Bird Species',
                             'font': {'size': 36,
                                      'shadow': 'auto'
                                      },
                             'x': 0.5},
                      width=2400,
                      height=1600)

    return fig
