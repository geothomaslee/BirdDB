# BirdDB: A Data Base Manager for Bird Photography

Are you someone who enjoys photography of birds? Are you looking for a system to organize the vast number of photos you've collected over your birding career? BirdDB may be for you!

### Installation
All required modules are available on `conda-forge`, so it is recommended you use Conda or Mamba for installation.

## BirdDataBase
The core module of BirdDB is `birddb.database` which contains the class `BirdDatabase`. BirdDataBase stores information about your photography in a Polars DataFrame and wraps it with user-friendly methods for accessing the data. 

BirdDataBase objects can be saved to the disk, and each entry new entry can take a second or two to add properly, so it is recommended to use `birddb.getBirdDataBase` when looking at your database. This will look for a saved database and load it in before initializing a new one. Name the files in the correct format (see File Structure section), placed in the home data directory for the database, then `db.sort_new()` can be called to add them to the database and place them into their correct taxonomic directory. Taxonomic information is gathered by parsing the species given in the file name, searching for their Wikipedia Page, and then scraping the taxonomic information from that page. If an ebird link is given `db.sort_new(ebird='ebird.com/my_checklist_link)` then all unsorted photos will be added to the Data Frame with that eBird link. Therefore, it is best practice to only sort photos from one birding checklist at a time.

#### File Structure
Photos must be pngs named with a few set of rules, otherwise Photographs must be named in the format `BirdName_MMMDD_YYYY.png`. Can also include multiple birds in the format `BirdName1_BirdName2_MMMDD__YYYY.png` and a copy of the photo will be put in the proper spot for each species named in the photo.
Example: `ForstersTern_Mar1_2025` or `


- [ ] Data Directory. Example: Windows `C:/Birds/Classification` Mac/Linux `/Users/myusername/Birds/Classification`
  - [ ] Charadriformes
    - [ ] Laridae
      - [ ] Sterna
        - [ ] {dataDirectory}/Charadriformes/Laridae/Sterna/ForsternsTern_Mar1_2025

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
