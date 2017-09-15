from abc import ABCMeta, abstractmethod

import os

# --- Kodi stuff ---
import xbmc

# --- Modules/packages in this plugin ---
from constants import *
from disk_IO import *
from utils import *
from utils_kodi import *

class RomSetFactory():
    
    def __init__(self, pluginDataDir):

        self.ROMS_DIR                 = pluginDataDir.join('db_ROMs')
        self.FAV_JSON_FILE_PATH       = pluginDataDir.join('favourites.json')
        self.RECENT_PLAYED_FILE_PATH  = pluginDataDir.join('history.json')
        self.MOST_PLAYED_FILE_PATH    = pluginDataDir.join('most_played.json')
        self.COLLECTIONS_FILE_PATH    = pluginDataDir.join('collections.xml')
        self.COLLECTIONS_DIR          = pluginDataDir.join('db_Collections')
        self.VIRTUAL_CAT_TITLE_DIR    = pluginDataDir.join('db_title')
        self.VIRTUAL_CAT_YEARS_DIR    = pluginDataDir.join('db_years')
        self.VIRTUAL_CAT_GENRE_DIR    = pluginDataDir.join('db_genre')
        self.VIRTUAL_CAT_STUDIO_DIR   = pluginDataDir.join('db_studio')
        self.VIRTUAL_CAT_CATEGORY_DIR = pluginDataDir.join('db_category')
        self.VIRTUAL_CAT_NPLAYERS_DIR = pluginDataDir.join('db_nplayers')
        self.VIRTUAL_CAT_ESRB_DIR     = pluginDataDir.join('db_esrb')
        self.VIRTUAL_CAT_RATING_DIR   = pluginDataDir.join('db_rating')

        if not self.ROMS_DIR.exists():                 self.ROMS_DIR.makedirs()
        if not self.VIRTUAL_CAT_TITLE_DIR.exists():    self.VIRTUAL_CAT_TITLE_DIR.makedirs()
        if not self.VIRTUAL_CAT_YEARS_DIR.exists():    self.VIRTUAL_CAT_YEARS_DIR.makedirs()
        if not self.VIRTUAL_CAT_GENRE_DIR.exists():    self.VIRTUAL_CAT_GENRE_DIR.makedirs()
        if not self.VIRTUAL_CAT_STUDIO_DIR.exists():   self.VIRTUAL_CAT_STUDIO_DIR.makedirs()
        if not self.VIRTUAL_CAT_CATEGORY_DIR.exists(): self.VIRTUAL_CAT_CATEGORY_DIR.makedirs()
        if not self.VIRTUAL_CAT_NPLAYERS_DIR.exists(): self.VIRTUAL_CAT_NPLAYERS_DIR.makedirs()
        if not self.VIRTUAL_CAT_ESRB_DIR.exists():     self.VIRTUAL_CAT_ESRB_DIR.makedirs()
        if not self.VIRTUAL_CAT_RATING_DIR.exists():   self.VIRTUAL_CAT_RATING_DIR.makedirs()
        if not self.COLLECTIONS_DIR.exists():          self.COLLECTIONS_DIR.makedirs()

    def create(self, launcherID, categoryID, launchers):
        
        launcher = None
        if launcherID in launchers:
            launcher = launchers[launcherID]
        else:
            log_warning('Launcher "{0}" not found in launchers'.format(launcherID))

        # --- ROM in Favourites ---
        if categoryID == VCATEGORY_FAVOURITES_ID and launcherID == VLAUNCHER_FAVOURITES_ID:
            return FavouritesRomSet(self.FAV_JSON_FILE_PATH, launcher)
        
        # --- ROM in Most played ROMs ---
        elif categoryID == VCATEGORY_MOST_PLAYED_ID and launcherID == VLAUNCHER_MOST_PLAYED_ID:
            return FavouritesRomSet(self.MOST_PLAYED_FILE_PATH, launcher)

        # --- ROM in Recently played ROMs list ---
        elif categoryID == VCATEGORY_RECENT_ID and launcherID == VLAUNCHER_RECENT_ID:
            return RecentlyPlayedRomSet(self.RECENT_PLAYED_FILE_PATH, launcher)

        # --- ROM in Collection ---
        elif categoryID == VCATEGORY_COLLECTIONS_ID:
            return CollectionRomSet(self.COLLECTIONS_FILE_PATH, launcher, self.COLLECTIONS_DIR, launcherID)

        # --- ROM in Virtual Launcher ---
        elif categoryID == VCATEGORY_TITLE_ID:
            log_info('RomSetFactory() loading ROM set Title Virtual Launcher ...')
            return VirtualLauncherRomSet(self.VIRTUAL_CAT_TITLE_DIR, launcher, launcherID)
        elif categoryID == VCATEGORY_YEARS_ID:
            log_info('RomSetFactory() loading ROM set Years Virtual Launcher ...')
            return VirtualLauncherRomSet(self.VIRTUAL_CAT_YEARS_DIR, launcher, launcherID)
        elif categoryID == VCATEGORY_GENRE_ID:
            log_info('RomSetFactory() loading ROM set Genre Virtual Launcher ...')
            return VirtualLauncherRomSet(self.VIRTUAL_CAT_GENRE_DIR, launcher, launcherID)
        elif categoryID == VCATEGORY_STUDIO_ID:
            log_info('RomSetFactory() loading ROM set Studio Virtual Launcher ...')
            return VirtualLauncherRomSet(self.VIRTUAL_CAT_STUDIO_DIR, launcher, launcherID)
        elif categoryID == VCATEGORY_NPLAYERS_ID:
            log_info('RomSetFactory() loading ROM set NPlayers Virtual Launcher ...')
            return VirtualLauncherRomSet(self.VIRTUAL_CAT_NPLAYERS_DIR, launcher, launcherID)
        elif categoryID == VCATEGORY_ESRB_ID:
            log_info('RomSetFactory() loading ROM set ESRB Virtual Launcher ...')
            return VirtualLauncherRomSet(self.VIRTUAL_CAT_ESRB_DIR, launcher, launcherID)
        elif categoryID == VCATEGORY_RATING_ID:
            log_info('RomSetFactory() loading ROM set Rating Virtual Launcher ...')
            return VirtualLauncherRomSet(self.VIRTUAL_CAT_RATING_DIR, launcher, launcherID)
        elif categoryID == VCATEGORY_CATEGORY_ID:
            return VirtualLauncherRomSet(self.VIRTUAL_CAT_CATEGORY_DIR, launcher, launcherID)
            
        
        log_info('RomSetFactory() loading standard romset...')
        return StandardRomSet(self.ROMS_DIR, launcher)

class RomSet():
    __metaclass__ = ABCMeta
    
    def __init__(self, romsDir, launcher):
        self.romsDir = romsDir
        self.launcher = launcher
    
    @abstractmethod
    def romSetFileExists():
        return False

    @abstractmethod
    def loadRoms(self):
        return None
    
    @abstractmethod
    def loadRom(self, romId):
        return None

    @abstractmethod
    def saveRoms(self, roms):
        pass

class StandardRomSet(RomSet):
    
    def __init__(self, romsDir, launcher):
        
        self.roms_base_noext = launcher['roms_base_noext'] if launcher is not None and 'roms_base_noext' in launcher else None
        super(StandardRomSet, self).__init__(romsDir, launcher)

    def romSetFileExists():
        rom_file_path = self.romsDir.join(self.roms_base_noext + '.json')
        return rom_file_path.exists()

    def loadRoms(self):

        if not self.romSetFileExists():
            log_warning('Launcher "{0}" JSON not found.'.format(self.roms_base_noext))
            return None

        log_info('StandardRomSet() Loading ROMs in Launcher ...')
        roms = fs_load_ROMs_JSON(self.romsDir, self.roms_base_noext)
        return roms

    def loadRom(self, romId):
        
        roms = self.loadRoms()

        if roms is None:
            log_error("StandardRomSet(): Could not load roms")
            return None

        romData = roms[romId]
        
        if romData is None:
            log_warning("StandardRomSet(): Rom with ID '{0}' not found".format(romId))
            return None

        return romData

    def saveRoms(self, roms):
        fs_write_ROMs_JSON(self.romsDir, self.roms_base_noext, roms, self.launcher)
        pass


class FavouritesRomSet(StandardRomSet):

    def loadRoms(self):
        log_info('FavouritesRomSet() Loading ROMs in Favourites ...')
        roms = fs_load_Favourites_JSON(self.romsDir)
        return roms


class VirtualLauncherRomSet(StandardRomSet):
    
    def __init__(self, romsDir, launcher, launcherID):

        self.launcherID = launcherID
        super(VirtualLauncherRomSet, self).__init__(romsDir, launcher)

    def romSetFileExists():
        hashed_db_filename = self.romsDir.join(self.launcherID + '.json')
        return hashed_db_filename.exists()

    def loadRoms(self):

        if not self.romSetFileExists():
            log_warning('VirtualCategory "{0}" JSON not found.'.format(self.launcherID))
            return None

        log_info('VirtualCategoryRomSet() Loading ROMs in Virtual Launcher ...')
        roms = fs_load_VCategory_ROMs_JSON(self.romsDir, self.launcherID)
        return roms

    def saveRoms(self, roms):
        fs_write_Favourites_JSON(self.romsDir, roms)
        pass

class RecentlyPlayedRomSet(RomSet):
    
    def romSetFileExists():
        return self.romsDir.exists()

    def __loadRomsAsList(self):
        romsList = fs_load_Collection_ROMs_JSON(self.romsDir)
        return romsList

    def loadRoms(self):
        log_info('RecentlyPlayedRomSet() Loading ROMs in Recently Played ROMs ...')
        romsList = self.__loadRomsAsList()
        
        roms = OrderedDict()
        for rom in romsList:
            roms[rom['id']] = rom
            
        return roms
    
    def loadRom(self, romId):
        
        roms = self.__loadRomsAsList()

        if roms is None:
            log_error("RecentlyPlayedRomSet(): Could not load roms")
            return None
        
        current_ROM_position = fs_collection_ROM_index_by_romID(romId, roms)
        if current_ROM_position < 0:
            kodi_dialog_OK('Collection ROM not found in list. This is a bug!')
            return None
            
        romData = roms[current_ROM_position]
        
        if romData is None:
            log_warning("RecentlyPlayedRomSet(): Rom with ID '{0}' not found".format(romId))
            return None

        return romData

    
    def saveRoms(self, roms):
        fs_write_Collection_ROMs_JSON(self.romsDir, roms)
        pass

class CollectionRomSet(RomSet):
    
    def __init__(self, romsDir, launcher, collection_dir, launcherID):

        self.collection_dir = collection_dir
        self.launcherID = launcherID
        super(CollectionRomSet, self).__init__(romsDir, launcher)

    def romSetFileExists():
        (collections, update_timestamp) = fs_load_Collection_index_XML(self.romsDir)
        collection = collections[self.launcherID]

        roms_json_file = self.romsDir.join(collection['roms_base_noext'] + '.json')
        return roms_json_file.exists()
    
    def __loadRomsAsList(self):
        (collections, update_timestamp) = fs_load_Collection_index_XML(self.romsDir)
        collection = collections[self.launcherID]
        roms_json_file = self.collection_dir.join(collection['roms_base_noext'] + '.json')
        romsList = fs_load_Collection_ROMs_JSON(roms_json_file)
        return romsList

    # NOTE ROMs in a collection are stored as a list and ROMs in Favourites are stored as
    #      a dictionary. Convert the Collection list into an ordered dictionary and then
    #      converted back the ordered dictionary into a list before saving the collection.
    def loadRoms(self):
        log_info('CollectionRomSet() Loading ROMs in Collection ...')

        romsList = self.__loadRomsAsList()
        
        roms = OrderedDict()
        for rom in romsList:
            roms[rom['id']] = rom
            
        return roms
    
    def loadRom(self, romId):
        
        roms = self.__loadRomsAsList()

        if roms is None:
            log_error("CollectionRomSet(): Could not load roms")
            return None

        current_ROM_position = fs_collection_ROM_index_by_romID(romId, roms)
        if current_ROM_position < 0:
            kodi_dialog_OK('Collection ROM not found in list. This is a bug!')
            return
            
        romData = roms[current_ROM_position]
        
        if romData is None:
            log_warning("CollectionRomSet(): Rom with ID '{0}' not found".format(romId))
            return None

        return romData

    def saveRoms(self, roms):
        
        # >> Convert back the OrderedDict into a list and save Collection
        collection_rom_list = []
        for key in roms:
            collection_rom_list.append(roms[key])

        json_file_path = self.romsDir.join(collection['roms_base_noext'] + '.json')
        fs_write_Collection_ROMs_JSON(json_file_path, collection_rom_list)