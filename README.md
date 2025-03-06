# BirdDB: A Data Base Manager for Bird Photography

Are you someone who enjoys photography of birds? Are you looking for a system to organize the vast number of photos you've collected over your birding career? BirdDB may be for you!

### Installation
All required modules are available on `conda-forge`, so it is recommended you use Conda or Mamba for installation.

## BirdDataBase
The core module of BirdDB is `birddb.database` which contains the class `BirdDatabase`. BirdDataBase stores information about your photography in a Polars (because I don't like Pandas) DataFrame and wraps it with user-friendly methods for managing the data within that DataFrame. 

BirdDataBase objects can be saved to the disk, and each entry new entry can take a second or two to add properly, so it is recommended to use `birddb.getBirdDataBase` when looking at your database. This will look for a saved database and load it in before initializing a new one.


### Planned Features
- [x] Add user-friendly querying function that can pull photos
- [x] Add ability to show them in IDE with matplotlib
- [x] Add ability to make copies of all queried photos and put them in an easy to access directory
- [x] Add ability to easily clear query directories
- [ ] Add plotting tools for showing evolution of photography over time
  - [ ] Species seen per month
  - [ ] Species photographed per month
  - [ ] Long-term evolution of photographed taxa
