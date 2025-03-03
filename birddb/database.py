# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 21:00:51 2025

@author: tlee
"""

import os
import re
import shutil
from glob import glob
import pickle

from tqdm import tqdm
import polars as pl
from bs4 import BeautifulSoup

import wikipedia
from wikipedia import WikipediaPage, WikipediaException

class BirdDataBase:
    def __init__(self,datafolder: str=None):
        self.df = pl.DataFrame(schema={'Order': str,
                                   'Family': str,
                                   'Genus': str,
                                   'Species': str,
                                   'Scientific_Species': str,
                                   'Capture_Date': str,
                                   'Path': str,
                                   'Basename': str,
                                   'Wikipedia_URL': str,
                                   'eBird_Checklist': str})

        self.dataFolder =  datafolder
        if _has_existing_inventory(datafolder):
            print('Adding existing classification to directory...')
            self.load_data_base()

        self.unsortedList = []

        self.photoCount = len(self.df)-1
        self.DiskSpace=0
        self.save()

    def __repr__(self):
        return f'Bird Data Base containing {self.photoCount} photos at {self.dataFolder}'

    def load_data_base(self):
        """
        Loads an existing sorted file structure to the data base.
        """
        datafolder = self.dataFolder
        if not os.path.exists(datafolder):
            raise ValueError(f'Could not find data folder at {datafolder}')

        needs_sorting = glob(f'{datafolder}/*.png')
        self.unsortedCount = len(needs_sorting)
        pngs = glob(f'{datafolder}/**/*.png',recursive=True)
        pngs = [x for x in pngs if x not in needs_sorting]
        self.sortedCount = len(pngs)

        # Split up the main batch from the ones in the unidentified folder
        unidentified_pngs = [x for x in pngs if 'Unidentified' in x]
        pngs = [x for x in pngs if x not in unidentified_pngs]

        for png in tqdm(pngs):
            split = _path_to_list(png)
            order, fam, genus, path = split[-4:]
            species = _strip_species_name(path)
            cap = _pull_capture_date(png)

            for spec in species:
                page, common_name = _pull_species_wiki_page(spec)
                sci_species = _pull_species_box(page)[3]

                self.df = self._add_row_to_df(order, fam, genus, common_name,
                                         sci_species,cap,png,page.url,ebird=None)

    def add_unsorted_to_database(self, ebird: str=None):
        """
        Looks for pngs in the home directory that haven't been sorted and adds
        them to the database.

        NOTE: This does not sort them. For now BirdDataBase.sort() needs to be
        manually called.

        Parameters
        ----------
        ebird : str, optional
            Link to the eBird checklist corresponding to the photos. This assumes
            all unsorted pngs were taken in the same outing, so its best to add
            them in batches at a time if you're adding multiple sessions.
            The default is None.

        """
        pngs = glob(f'{self.dataFolder}/*.png')
        self.unsortedList = pngs
        for png in tqdm(pngs):
            self.add_new_png_to_database(png,ebird)
        self.save()

    def add_new_png_to_database(self, png: str, ebird: str=None):
        """
        Adds a new png photo to the database.

        Parameters
        ----------
        png : str
            Path to the png.
        ebird : str, optional
            An eBird checklist link corresponding to the photo being added.
            The default is None.

        Returns
        -------
        None.
        """
        species = _strip_species_name(os.path.basename(png))
        cap = _pull_capture_date(png)
        for spec in species:
            try:
                page, common_name = _pull_species_wiki_page(spec)
            except Exception as e:
                print(f'ERROR IN {png}')
                raise e
            order, fam, genus, sci_species = _pull_species_box(page)

            self.df = self._add_row_to_df(order, fam, genus, common_name,
                                     sci_species,cap,png,page.url, ebird)

    def rename_species(self, orig, new):
        """
        Will rename a species while keeping all other information the same. This
        may be useful if a bird has a name in your region that is different from
        the name on Wikipedia.
        Ex. Grey Plover is the correct name on Wikipedia and in the Old World,
        but they're called Black-bellied plovers in the New World.

        Parameters
        ----------
        orig : str
            Current name of the bird in the table.
        new : str
            New name of the bird in the table.

        Returns
        -------
        None.

        """
        self.df = self.df.with_columns(
            pl.when((pl.col("Species") == orig))
            .then(pl.lit(new))
            .otherwise(pl.col("Species"))
            .alias("Species")
        )

    def sort(self):
        """Sorts all unsorted pngs in the database into their proper directories
        and updates the data base paths accordingly"""
        for png in self.unsortedList:
            self._sort_png(png)
        self.unsortedList = []
        self.save()

    def _add_row_to_df(self, order, fam, genus, spec, sci_spec, cap, path, basename, url, ebird):
        """Adds a row to the internal DataFrame"""
        new_df = pl.DataFrame({'Order':order,
                               'Family':fam,
                               'Genus':genus,
                               'Species':spec,
                               'Scientific_Species':sci_spec,
                               'Capture_Date':cap,
                               'Path':path,
                               'Wikipedia_URL':url,
                               'eBird_Checklist': ebird})
        df = self.df
        return pl.concat([df,new_df])

    def _sort_png(self, png):
        """
        Sorts a png into its proper directory.

        If a photo contains multiple birds, a copy will be placed into the proper
        directory for EACH of the species present in the photo, then the original
        will be deleted. Otherwise the original is just moved directly into its
        proper directory.

        Parameters
        ----------
        png : str
            Path to the png.

        """
        row = self.df.filter(pl.col('Path') == png)
        if len(row) == 1:
            order = row['Order'].to_list()[0]
            family = row['Family'].to_list()[0]
            genus = row['Genus'].to_list()[0]

            os.makedirs(f'{self.dataFolder}/{order}/{family}/{genus}',exist_ok=True)
            new_path = f'{self.dataFolder}/{order}/{family}/{genus}/{os.path.basename(png)}'
            os.rename(png, new_path)

            self.df = self.df.with_columns(
                pl.col('Path').replace(png, new_path))
        else:
            for i in range(len(row)):
                order = row['Order'].to_list()[i]
                family = row['Family'].to_list()[i]
                genus = row['Genus'].to_list()[i]
                species = row['Species'].to_list()[i]

                os.makedirs(f'{self.dataFolder}/{order}/{family}/{genus}',exist_ok=True)
                new_path = f'{self.dataFolder}/{order}/{family}/{genus}/{os.path.basename(png)}'
                shutil.copyfile(png, new_path)

                self.df = self.df.with_columns(
                    pl.when((pl.col("Path") == png) & (pl.col("Species") == species))
                    .then(pl.lit(new_path))
                    .otherwise(pl.col("Path"))
                    .alias("Path")
                )
            
            """
            try:
                os.remove(png)
            except PermissionError:
                pass
            """


    def _add_unidentified(self,ebird: str):
        """
        Adds birds in the unidentified directory to the data base. For now this
        is an interal method and will have a wrapper function in the future to
        handle this better.

        Parameters
        ----------
        ebird : str
            Link to corresponding eBird checklist.

        """
        datafolder = self.dataFolder
        if not os.path.isdir(f'{datafolder}/Unidentified'):
            raise ValueError('Unidentified folder does not exist')

        for png in glob(f'{datafolder}/Unidentified/*.png'):
            path = os.path.basename(png)
            common_name = _strip_species_name(path)
            cap = _pull_capture_date(png)
            self.df = self._add_row_to_df(None, None, None, common_name,
                                     None,cap,png,None, ebird)

        self.save()

    def save(self):
        """Pickles the bird data base to the data home directory"""
        savepath = f'{self.dataFolder}/BirdDataBase.pkl'
        print(savepath)
        with open(savepath, 'wb') as f:
            pickle.dump(self,f)

def getBirdDataBase(directory: str=None,force_overwrite: bool=False):
    """
    Wrapper function for creating new bird databases. If a pickled BirdDataBase
    is found, it will load and return that. If none exists, it will create a new
    one for this directory. If force_overwrite is True, then any existing BirdDB
    file will be overwritten.

    Parameters
    ----------
    directory : str, optional
        Home directory for the bird data base. The default is None.
    force_overwrite : bool, optional
        If True, will overwrite any saved bird data base file (not the photos
        themselves, but just the pickled BirdDataBase object). The default is False.

    Returns
    -------
    birddb.BirdDataBase
        The Bird Data Base for all photos in the given directory.

    """
    if os.path.isdir(directory) is False:
        raise ValueError(f'Directory {directory} does not exist')

    if force_overwrite is False:
        try:
            with open(f'{directory}/BirdDataBase.pkl', 'rb') as f:
                print(f'Returning existing database at {directory}/BirdDataBase.pkl\n' +
                      'Set force_overwrite to True if you want to start over')
                db = pickle.load(f)
                return db
        except(FileNotFoundError,pickle.UnpicklingError):
            print('No existing file found, creating new BirdDataBase')

    return BirdDataBase(directory)

def _path_to_list(path: str) -> list:
    """Splits all subdirectories in a path into a list"""
    all_parts = []
    while True:
        head, tail = os.path.split(path)
        if tail:
            all_parts.insert(0, tail)
            path = head
        elif head:
            all_parts.insert(0, head)
            break
        else:
            break
    return all_parts


def _strip_species_name(spec: str) -> str:
    """Strips a list of species names as strings from the png"""
    if '_Downscale' in spec:
        spec = spec.replace('_Downscale', '')

    spec = spec.removesuffix('.png')
    pattern = r'_[A-Z][a-z]{2}\d{1,2}_\d{4}$'
    spec = re.sub(pattern, '', spec)
    _species = spec.split('_')

    species = []
    for spec in _species:
        try:
            int(spec[-1])
            species.append(spec[0:-1])
        except ValueError:
            species.append(spec)
        
    return species

def _pull_species_wiki_page(spec) -> WikipediaPage:
    """Pulls the wiki page for the species"""
    split = re.findall('[A-Z][^A-Z]*', spec)
    spec = ' '.join(split)

    results = wikipedia.search(spec,results=1)
    if len(results) == 0:
        raise ValueError(f'Wikipedia could not find page for "{spec}". Rename file and try again.\n' +
                         'Note: Most effective when all individual words are capitalized, even if hyphenated\n' +
                         'e.g. black-necked stilt should be BlackNeckedStilt')

    try:
        page = wikipedia.page(title=results[0],auto_suggest=False)
    except WikipediaException:
        print(f'ERROR OCCURING WITH SEARCHING FOR {spec}')
    except Exception as e:
        raise e

    return page, results[0]

def _pull_species_box(page: WikipediaPage):
    """Parses the order, fam, genus, and species from the Wikipedia Page's InfoBox"""
    # parse the html using beautiful soup and store in variable 'soup'
    soup = BeautifulSoup(page.html(), 'html.parser')
    # find results within table
    table = soup.find('table', attrs={'class': 'infobox biota'})
    try:
        tds = table.find_all('td')
        trs = table.find_all('tr')
    except AttributeError:
        print(f'ERROR OCCURING WITH {page}')
        return [None, None, None, None]

    order = _pull_table_value(tds,'Order')
    fam = _pull_table_value(tds,'Family')
    genus = _pull_table_value(tds,'Genus')
    species = _pull_table_value_tr(trs,'Species')

    return [order, fam, genus, species]

def _pull_table_value(tds, value: str) -> str:
    """Pulls a specific value from an HTML table"""
    correct_i = None
    for i, td in enumerate(tds):
        td_str = str(td)
        if value in td_str:
            correct_i = i+1

        if correct_i is not None:
            # We only get to this code once we know wh
            if i == correct_i:
                match = _extract_bird_name(td_str)

                if '(genus)' in match.group(1):
                    return match.group(1).removesuffix(' (genus)')
                if '(order)' in match.group(1):
                    return match.group(1).removesuffix(' (order)')
                if '(family)' in match.group(1):
                    return match.group(1).removesuffix(' (family)')
                return match.group(1)
    return None

def _extract_bird_name(html_str):
    """Extracts the bird name from the HTML table entry for the bird name"""
    pattern1 = r'<i>(.*?)</i></a>'
    pattern2 = r'title="[^"]*">([^<]+)</a>'

    match = re.search(pattern1, html_str)
    if match:
        return match
    match = re.search(pattern2,html_str)
    if match:
        return match
    return None

def _pull_table_value_tr(trs, value: str) -> str:
    """Pulls a specific value from a <tr> class in HTML"""
    for tr in trs:
        tr_str = str(tr)
        if value in tr_str:
            match = re.findall('<b>(.*?)</b>', tr_str)[0]
            match = match.replace('\xa0', ' ')
            return match

    return None

def _pull_capture_date(png):
    """Strips the date from the end of the file"""
    png = png.removesuffix('.png')
    pattern = r'[A-Z][a-z]{2}\d{1,2}_\d{4}$'
    try:
        match = re.search(pattern,os.path.basename(png))[0]
    except TypeError as e:
        if str(e) == ("'NoneType' object is not subscriptable"):
            raise ValueError(f'Could not pull capture date for {png}. Make sure date is properly formatted')
        else:
            raise e
        
    if match:
        date = f'{match[0:3]} {match[3:]}'
        date = date.replace('_',' ')
        date = _get_full_month_name(date)
        return str(date)
    return None

def _get_full_month_name(date):
    """Replaces the 3 letter month abbreviation with the months full name"""
    ddict = {'Jan': 'January',
             'Feb': 'February',
             'Mar': 'March',
             'Apr': 'April',
             'May': 'May',
             'Jun': 'June',
             'Jul': 'July',
             'Aug': 'August',
             'Sep': 'September',
             'Oct': 'October',
             'Nov': 'November',
             'Dec': 'December'}

    for key in ddict.keys():
        if key in date:
            date = date.replace(key,ddict[key])
            return date
    return None

def _has_existing_inventory(directory):
    """Checks if there's an existing file structure containing bird photos"""
    for _result in glob(f'{directory}/*'):
        if os.path.isdir(_result):
            return True
    return False

def _has_unsorted_pngs(directory):
    """Checks if there are unsorted pngs"""
    count = len(glob(f'{directory}/*.png'))
    if count == 0:
        return False
    return True
