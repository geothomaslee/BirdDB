# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 10:42:36 2025

@author: tlee
"""

import polars as pl
from polars import DataFrame

def get_unique_species_df(df: DataFrame) -> DataFrame:
    """Returns only first instance of every species"""
    return df.unique(subset=["Species"], keep="first")

def get_unique_dates_df(df: DataFrame) -> DataFrame:
    """Returns only first instance of a species on a specific date"""
    return df.unique(subset=['Species','Capture_Date'],keep='first')

def get_unique_lists_df(df: DataFrame) -> DataFrame:
    """Returns only first instance of a species from a specific eBird link"""
    return df.unique(subset=['Species','eBird_Checklist'],keep='first')

def get_photo_count(df: DataFrame) -> DataFrame:
    """Returns a DataFrame with only unique species, but adds a count column
    for the number of times that species was seen in the input DataFrame"""
    # Creates new dataframe with only first instance of bird sighting
    unique_df = get_unique_species_df(df)

    # Add column for count
    unique_df = unique_df.with_columns(pl.lit("1").alias("Count"))

    species = unique_df['Species'].to_list()
    for spec in species:
        count = df.filter(pl.col('Species') == spec).height
        unique_df = unique_df.with_columns(
            pl.when((pl.col("Species") == spec))
            .then(pl.lit(str(count)))
            .otherwise(pl.col("Count"))
            .alias("Count"))

    return unique_df
