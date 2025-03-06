# BirdDB: A Data Base Manager for Bird Photography

![Ring-necked duck][./Figures/RingNeckedDuck2_Feb23_2025.png]

Are you someone who enjoys photography of birds? Are you looking for a system to organize the vast number of photos you've collected over your birding career? BirdDB may be for you!

### Installation
All required modules are available on `conda-forge`, so it is recommended you use Conda or Mamba for installation.

## BirdDataBase
The core module of BirdDB is `birddb.database` which contains the class `BirdDatabase`. BirdDataBase stores information about your photography in a Polars DataFrame and wraps it with user-friendly methods for accessing the data. 

BirdDataBase objects can be saved to the disk, and each entry new entry can take a second or two to add properly, so it is recommended to use `birddb.getBirdDataBase` when looking at your database. This will look for a saved database and load it in before initializing a new one. Name the files in the correct format (see File Structure section), placed in the home data directory for the database, then `db.sort_new()` can be called to add them to the database and place them into their correct taxonomic directory. Taxonomic information is gathered by parsing the species given in the file name, searching for their Wikipedia Page, and then scraping the taxonomic information from that page. If an ebird link is given `db.sort_new(ebird='ebird.com/my_checklist_link)` then all unsorted photos will be added to the Data Frame with that eBird link. Therefore, it is best practice to only sort photos from one birding checklist at a time.

#### File Structure
Photos must be pngs named with a few set of rules, otherwise searching for their Wikipedia page may return the wrong page.
- Photographs must be named in the format `BirdName_MMMDD_YYYY.png`.
  - Can also include multiple birds in the format `BirdName1_BirdName2_MMMDD__YYYY.png` and a copy of the photo will be put in the proper spot for each species named in the photo.
- Each separate word in the name must be capitalized.
  - Correct: `BrownPelican` Incorrect: `Brownpelican`
- Hypens must be excluded, and the word after the hyphen must also be capitalized
  - Correct: `BlackNeckedStilt` Incorrect: `Black-neckedStilt` `BlackneckedStilt`
- A limited number of species have different names on Wikipedia than on eBird/Merlin.
  - Ex. on Wikipedia, their is a distinction drawn between the American White Ibis and the Australian White Ibis
  - On eBird, these are called the White Ibis and Austrlian Ibis
  - Go with the Wikipedia name for naming the png and adding it in to your database, but you can change its display name within the BirdDataBase using `BirdDataBase.rename_species()`
    - This function may also be useful for species whose name differs regionally, and Wikipedia will get the correct page regardless of which name you use, but will add in the default name on Wikipedia.
      - Example: in North America we call it the Black-bellied plover, but in the rest of the world it is the Grey plover. If you name your file the Black-bellied plover it will pull the page for the correct bird, but it will be entered in to your database as the Grey plover.
    
Example: `ForstersTern_Mar1_2025` or `AmericanWhiteIbis_SnowyEgret_NeotropicCormorant_Jan15_2025.png`


- [ ] Data Directory. Example: Windows `C:/Birds/Classification` Mac/Linux `/Users/myusername/Birds/Classification`
  - [ ] Charadriformes
    - [ ] Laridae
      - [ ] Sterna
        - [ ] {dataDirectory}/Charadriformes/Laridae/Sterna/ForstersTern_Mar1_2025

#### The DataFrame
| Order | Family | Genus | Species | Scientific_Species | Capture_Date | Path | Wikipedia_URL | eBird_Checklist |
|--|--|--|--|--|--|--|--|--|
| Charadriformes | Laridae | Sterna | Forster's tern | S. forsteri | March 1 2025 | /path/to/saved/.png | https://en.wikipedia.org/wiki/Forster's_tern | https://ebird.org/checklist/S216014746 |



### Planned Features
- [x] Add user-friendly querying function that can pull photos
- [x] Add ability to show them in IDE with matplotlib
- [x] Add ability to make copies of all queried photos and put them in an easy to access directory
- [x] Add ability to easily clear query directories
- [ ] Add plotting tools for showing evolution of photography over time
  - [ ] Species seen per month
  - [ ] Species photographed per month
  - [ ] Long-term evolution of photographed taxa
