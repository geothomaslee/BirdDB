# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 17:20:27 2025

@author: tlee
"""
import polars as pl
from polars import DataFrame
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from birddb.plot_sankey import plot_sankey_tree
import birddb.sorting as srt

def plot_orders(db,mode: str='species',return_axes: bool=False):
    """
    Displays a matplotlib pie chart showing the breakdown of orders seen

    Parameters
    ----------
    db : birddb.database.BirdDataBase
        DESCRIPTION.
    mode : str, optional
        species: keeps only the first instance of every species, equivalent to life list.
        photos: counts every photo for every species
        dates: counts the first photo of a species on a given data. I.E. if you photographed a species
            twice on the same day, would only count as 1.
        trips: counts the first photo of a species for a given eBird list. I.E. if you photographed
            a species multiple times within the same eBird list, would only count as 1. In many cases
            will not be that different from dates, but will differ in the case of a species seen multiple
            times on the same date, but on different eBird checklists
        The default is 'species'.
    return_axes : bool, optional
        If True, will return figure and axes . The default is False.

    Returns
    -------
    fig, ax: matplotlib.pyplot.figure, matplotlib.pyplot.axes.Axes
        Matplotlib axes, if return_axes is True

    """
    df = returnModeDF(db.df,mode)

    orders = set(df['Order'].to_list())
    if None in orders:
        orders.remove(None)
    orders = sorted(list(orders))
    counts = []
    for order in orders:
        counts.append(df.filter(pl.col('Order') == order).height)

    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    fig, ax = plt.subplots()
    ax.pie(counts, labels=orders,colors=colors, autopct='%1.1f%%')
    ax.set_title(f'Orders Photographed\n{returnModeSubtitle(mode)}')
    plt.show()

    if return_axes:
        return fig, ax

def plot_families(db, order, mode: str='species',return_axes: bool=False):
    """
    Displays a matplotlib pie chart showing the breakdown of families seen
    within a specific order.

    Parameters
    ----------
    db : birddb.database.BirdDataBase
        DESCRIPTION.
    order : str
        Order to show family composition.
    mode : str, optional
        species: keeps only the first instance of every species, equivalent to life list.
        photos: counts every photo for every species
        dates: counts the first photo of a species on a given data. I.E. if you photographed a species
            twice on the same day, would only count as 1.
        trips: counts the first photo of a species for a given eBird list. I.E. if you photographed
            a species multiple times within the same eBird list, would only count as 1. In many cases
            will not be that different from dates, but will differ in the case of a species seen multiple
            times on the same date, but on different eBird checklists
        The default is 'species'.
    return_axes : bool, optional
        If True, will return figure and axes . The default is False.

    Returns
    -------
    fig, ax: matplotlib.pyplot.figure, matplotlib.pyplot.axes.Axes
        Matplotlib axes, if return_axes is True

    """
    df = returnModeDF(db.df,mode)

    df = df.filter(pl.col('Order')==order)

    fams = set(df['Family'].to_list())
    fams = sorted(list(fams))
    counts = []
    for fam in fams:
        counts.append(df.filter(pl.col('Family') == fam).height)

    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    fig, ax = plt.subplots()
    ax.pie(counts, labels=fams,colors=colors, autopct='%1.1f%%',
           wedgeprops={'linewidth': 2.0, 'edgecolor': 'white'},)

    ax.set_title(f'Families Photographed in Order {order}\n{returnModeSubtitle(mode)}')
    plt.show()

    if return_axes:
        return fig, ax

def plot_genera(db, family, mode: str='species',return_axes: bool=False):
    """
    Displays a matplotlib pie chart showing the breakdown of genera seen
    within a family.

    Parameters
    ----------
    db : birddb.database.BirdDataBase
        DESCRIPTION.
    family : str
        Family to show genera composition for.
    mode : str, optional
        species: keeps only the first instance of every species, equivalent to life list.
        photos: counts every photo for every species
        dates: counts the first photo of a species on a given data. I.E. if you photographed a species
            twice on the same day, would only count as 1.
        trips: counts the first photo of a species for a given eBird list. I.E. if you photographed
            a species multiple times within the same eBird list, would only count as 1. In many cases
            will not be that different from dates, but will differ in the case of a species seen multiple
            times on the same date, but on different eBird checklists
        The default is 'species'.
    return_axes : bool, optional
        If True, will return figure and axes . The default is False.

    Returns
    -------
    fig, ax: matplotlib.pyplot.figure, matplotlib.pyplot.axes.Axes
        Matplotlib axes, if return_axes is True

    """
    df = returnModeDF(db.df,mode)

    df = df.filter(pl.col('Family')==family)

    gens = set(df['Genus'].to_list())
    gens = sorted(list(gens))
    counts = []
    for gen in gens:
        counts.append(df.filter(pl.col('Genus') == gen).height)

    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    fig, ax = plt.subplots()
    ax.pie(counts, labels=gens,colors=colors, autopct='%1.1f%%',
           wedgeprops={'linewidth': 2.0, 'edgecolor': 'white'},)

    ax.set_title(f'Genuses Photographed in Family {family}\n{returnModeSubtitle(mode)}')
    plt.show()

    if return_axes:
        return fig, ax

def plot_phylo_tree(db,mode:str = 'Species'):
    plot_sankey_tree(db,mode=mode)

def plot_order_comp(db,order,mode: str='species',return_axes: bool=False):
    """
    Displays a nested matplotlib pie chart showing the family and genera
    composition of a specific order.

    Parameters
    ----------
    db : birddb.database.BirdDataBase
        BirdDataBase.
    order : str
        Order to show composition of.
    mode : str, optional
        species: keeps only the first instance of every species, equivalent to life list.
        photos: counts every photo for every species
        dates: counts the first photo of a species on a given data. I.E. if you photographed a species
            twice on the same day, would only count as 1.
        trips: counts the first photo of a species for a given eBird list. I.E. if you photographed
            a species multiple times within the same eBird list, would only count as 1. In many cases
            will not be that different from dates, but will differ in the case of a species seen multiple
            times on the same date, but on different eBird checklists
        The default is 'species'.
    return_axes : bool, optional
        If True, will return figure and axes . The default is False.

    Returns
    -------
    fig, ax: matplotlib.pyplot.figure, matplotlib.pyplot.axes.Axes
        Matplotlib axes, if return_axes is True

    """
    df = returnModeDF(db.df,mode)

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
    #max_genera = max(len(genera) for genera in all_gen_names)

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

    plt.show()
    if return_axes:
        return fig, ax

def plot_most_photographed(db,mode:str = 'photos',n: int=10,rotation: int=55,
                           return_axes: bool=False):
    """
    Displays a bar chart of the most photographed species.
    Parameters
    ----------
    db : birddb.database.BirdDataBase
        BirdDataBase.
    mode : str, optional
        photos: counts every photo for every species
        dates: counts the first photo of a species on a given data. I.E. if you photographed a species
            twice on the same day, would only count as 1.
        trips: counts the first photo of a species for a given eBird list. I.E. if you photographed
            a species multiple times within the same eBird list, would only count as 1. In many cases
            will not be that different from dates, but will differ in the case of a species seen multiple
            times on the same date, but on different eBird checklists
        The default is 'species'.
    n : int, optional
        The maximum number of species to plot. If n=10, and the first 8 are all ranked properly, but the 9-12th birds
        all have the same count, then only the first 8 will be plotted. This is useful for smaller databses where
        ties are much more likely. The default is 10.
    rotation: int, optional
        Rotation angle (from horizontal) of the species labels. The default is 55.
    return_axes : bool, optional
        If True, will return figure and axes. The default is False.

    Returns
    -------
    fig, ax: matplotlib.pyplot.figure, matplotlib.pyplot.axes.Axes
        Matplotlib axes, if return_axes is True

    """
    df = db.df
    if mode == 'species':
        raise ValueError('Mode set to species, but this sets the count of every bird to 1')

    df = returnModeDF(df,mode)

    species = df.unique(subset=["Species"], keep="first")['Species'].to_list()

    spec_dict = {}
    for specie in species:
        spec_dict[specie] = df.filter(pl.col('Species') == specie).height

    spec_dict = dict(sorted(spec_dict.items(), key=lambda x: x[1], reverse=True))
    spec_dict = dict(list(spec_dict.items())[:n])

    new_dict = None
    for spec in spec_dict:
        if list(spec_dict.values())[-1] == list(spec_dict.values())[-2]:
            new_dict = {key: val for key, val in spec_dict.items() if val != list(spec_dict.values())[-1]}

    if new_dict:
        species = list(new_dict.keys())
        counts = list(new_dict.values())
    else:
        species = list(spec_dict.keys())
        counts = list(spec_dict.values())

    rotation = rotation

    fig, ax = plt.subplots()
    ax.bar(species,counts)
    ax.set_title(f'Most Photographed Species\n{returnModeSubtitle(mode)}')
    plt.xticks(rotation=rotation,
               ha='right' if rotation < 90 else 'center')
    plt.show()
    if return_axes:
        return fig, ax

def returnModeDF(df: DataFrame,mode: str):
    """Returns a dataframe depending on the counting mode"""
    if mode == 'species':
        return srt.get_unique_species_df(df)
    elif mode == 'photos':
        return df
    elif mode == 'dates':
        return srt.get_unique_dates_df(df)
    elif mode == 'trips':
        return srt.get_unique_lists_df(df)
    else:
        raise ValueError('Mode must be "species","photos", "dates", or "trips"')

def returnModeSubtitle(mode: str):
    """Returns the proper subtitle to show the counting mode"""
    if mode == 'species':
        return 'Species Photographed'
    elif mode == 'photos':
        return 'Total Photos Taken'
    elif mode == 'dates':
        return 'Photos Taken, Unique Dates'
    elif mode == 'trips':
        return 'Photos Taken, Unique Trips'
    else:
        raise ValueError('Mode must be "species","photos", "dates", or "trips"')

def plot_photos_over_time(db,mode: str='photos'):
    """
    Plots the number of photos taken over time.

    Parameters
    ----------
    db : birddb.database.BirdDataBase
        BirdDataBase.
    mode : str, optional
        photos: counts every photo for every species
        dates: counts the first photo of a species on a given data. I.E. if you photographed a species
            twice on the same day, would only count as 1.
        trips: counts the first photo of a species for a given eBird list. I.E. if you photographed
            a species multiple times within the same eBird list, would only count as 1. In many cases
            will not be that different from dates, but will differ in the case of a species seen multiple
            times on the same date, but on different eBird checklists
        The default is 'photos'.

    """
    df = returnModeDF(db.df,mode)
    df = df.with_columns(pl.col("Capture_Date").str.strptime(pl.Datetime, format="%B %e %Y"))
    dates = sorted(list(set(df['Capture_Date'].to_list())))
    counts = []
    for i, date in enumerate(dates):
        if i == 0:
            counts.append(df.filter(pl.col('Capture_Date')==date).height)
            continue
        counts.append(df.filter(pl.col('Capture_Date')==date).height + counts[i-1])
    fig, ax = plt.subplots()
    ax.plot(dates,counts,'b-')
    ax.set_title(f'Sightings Over Time\n{returnModeSubtitle(mode)}')
    plt.xticks(rotation=55,
               ha='right' if 55 < 90 else 'center')
    plt.show()

def plot_orders_over_time(db,mode: str='photos'):
    """
    Plots the number of photos taken over time.

    Parameters
    ----------
    db : birddb.database.BirdDataBase
        BirdDataBase.
    mode : str, optional
        photos: counts every photo for every species
        dates: counts the first photo of a species on a given data. I.E. if you photographed a species
            twice on the same day, would only count as 1.
        trips: counts the first photo of a species for a given eBird list. I.E. if you photographed
            a species multiple times within the same eBird list, would only count as 1. In many cases
            will not be that different from dates, but will differ in the case of a species seen multiple
            times on the same date, but on different eBird checklists
        The default is 'species'.

    """
    df = returnModeDF(db.df,mode)
    df = df.with_columns(pl.col("Capture_Date").str.strptime(pl.Datetime, format="%B %e %Y"))
    dates = sorted(list(set(df['Capture_Date'].to_list())))
    orders = list(set(db.df['Order'].to_list()))

    order_count_dict = {}
    for order in orders:
        order_count_dict[order] = []
        for i, date in enumerate(dates):
            if i == 0:
                order_count_dict[order].append(df.filter(pl.col('Capture_Date')==date,
                                                         pl.col('Order')==order).height)
                continue
            order_count_dict[order].append(df.filter(pl.col('Capture_Date')==date,
                                                     pl.col('Order')==order).height + order_count_dict[order][i-1])

    order_count_dict = dict(sorted(order_count_dict.items(), key=lambda x: x[1][-1], reverse=True))

    fig, ax = plt.subplots()

    all_counts = []
    labels = []
    for k, v in order_count_dict.items():
        all_counts.append(v)
        labels.append(k)

    for i, count in enumerate(all_counts):
        if i == 0:
            ax.bar(dates,count,label=labels[i])
        else:
            new_count = [0 for x in count]
            for j in range(i):
                new_count = [sum(x) for x in zip(new_count, all_counts[j])]
            ax.bar(dates,count,bottom=new_count,label=labels[i])
    ax.legend(fontsize='x-small')
    ax.set_title(f'Orders Seen Over Time\n{returnModeSubtitle(mode)}')
    plt.xticks(rotation=55,
               ha='right' if 55 < 90 else 'center')

    plt.show()



