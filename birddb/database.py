# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 21:00:51 2025

@author: tlee
"""

import os
import re
from glob import glob
from typing import List
import urllib.request
#from tqdm import tqdm

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
                                   'Wikipedia_URL': str})
        if datafolder is not None:
            self.load_data_base(datafolder)
            
    def load_data_base(self, datafolder: str):
        if not os.path.exists(datafolder):
            raise ValueError(f'Could not find data folder at {datafolder}')
            
        needs_sorting = glob(f'{datafolder}/*.png')
        pngs = glob(f'{datafolder}/**/*.png',recursive=True)
        pngs = [x for x in pngs if x not in needs_sorting]
    
        # Split up the main batch from the ones in the unidentified folder
        unidentified_pngs = [x for x in pngs if 'Unidentified' in x]
        pngs = [x for x in pngs if x not in unidentified_pngs]
        
        for i, png in enumerate(pngs):
            split = _path_to_list(png)
            order, fam, genus, path = split[-4:]
            species = _strip_species_name(path)
            
            for spec in species:
                page, common_name = _pull_species_wiki_page(spec)
                sci_species = _pull_species_box(page)[3]
                
                self.df = self._add_row_to_df(order, fam, genus, common_name,
                                         sci_species,None,png,page.url)
                
    def add_bulk_to_database(self, path: str):
        pngs = glob(f'{path}/*.png')
        for png in pngs:
            self.add_new_png_to_database(png)
                
    def add_new_png_to_database(self, path: str):
        png = path
        path = os.path.basename(path)
        species = _strip_species_name(path)
        for spec in species:
            try:
                page, common_name = _pull_species_wiki_page(spec)
            except Exception as e:
                print(f'ERROR IN {png}')
                raise e
            order, fam, genus, sci_species = _pull_species_box(page)
            
            self.df = self._add_row_to_df(order, fam, genus, common_name,
                                     sci_species,None,png,page.url)
                
                
    def _add_row_to_df(self, order, fam, genus, spec, sci_spec, cap, path, url):
        new_df = pl.DataFrame({'Order':order,
                               'Family':fam,
                               'Genus':genus,
                               'Species':spec,
                               'Scientific_Species':sci_spec,
                               'Capture_Date':cap,
                               'Path':path,
                               'Wikipedia_URL':url})
        df = self.df
        return pl.concat([df,new_df])
        
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
        except:
            species.append(spec)
    
    return species

def _pull_species_wiki_page(spec) -> WikipediaPage:
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
    urlpage = urllib.request.urlopen(page.url)
    # parse the html using beautiful soup and store in variable 'soup'
    soup = BeautifulSoup(urlpage, 'html.parser')
    # find results within table
    table = soup.find('table', attrs={'class': 'infobox biota'})
    try:
        tds = table.find_all('td')
        trs = table.find_all('tr')
    except AttributeError as e:
        print(f'ERROR OCCURING WITH {page}')
        return [None, None, None, None]
    
    order = _pull_table_value(tds,'Order')
    fam = _pull_table_value(tds,'Family')
    genus = _pull_table_value(tds,'Genus')
    species = _pull_table_value_tr(trs,'Species')
    
    return [order, fam, genus, species]
                   
def _pull_table_value(tds, value: str) -> str:
    correct_i = None
    for i, td in enumerate(tds):
        td_str = str(td)
        if value in td_str:
            correct_i = i+1
        if correct_i is not None:
            if i == correct_i:
                match = re.search(r'title="([^"]*)"', str(td))
                if match:
                    if '(genus)' in match.group(1):
                        return match.group(1).removesuffix(' (genus)')
                    if '(order)' in match.group(1):
                        return match.group(1).removesuffix(' (order)')
                    if '(family)' in match.group(1):
                        return match.group(1).removesuffix(' (family)')
                    return match.group(1)
                else:
                    raise ValueError(f'Could not pull {value} from Wikipedia Infobox')
                    
def _pull_table_value_tr(trs, value: str) -> str:
    correct_i = None
    for i, tr in enumerate(trs):
        tr_str = str(tr)
        if value in tr_str:
            match = re.findall(r'<b>(.*?)</b>', tr_str)[0]
            match = match.replace(u'\xa0', u' ')
            return match
            

        
     
            
        
        
       
                                
            
