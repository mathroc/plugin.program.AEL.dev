#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Test AEL Arcade DB asset scraper.
#

# --- Python standard library ---
from __future__ import unicode_literals
import os
import pprint
import sys

# --- AEL modules ---
if __name__ == "__main__" and __package__ is None:
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print('Adding to sys.path {0}'.format(path))
    sys.path.append(path)
from resources.scrap import *
from resources.utils import *
import common

# --- main ---------------------------------------------------------------------------------------
print('*** Fetching candidate game list ********************************************************')
set_log_level(LOG_DEBUG)

# --- Create scraper object ---
scraper_obj = ArcadeDB(common.settings)
scraper_obj.set_verbose_mode(False)
scraper_obj.set_debug_file_dump(True, os.path.join(os.path.dirname(__file__), 'assets'))
status_dic = kodi_new_status_dic('Scraper test was OK')

# --- Get candidates ---
# candidate_list = scraper_obj.get_candidates(*common.games['tetris'], status_dic = status_dic)
# candidate_list = scraper_obj.get_candidates(*common.games['mslug'], status_dic = status_dic)
candidate_list = scraper_obj.get_candidates(*common.games['dino'], status_dic = status_dic)
# candidate_list = scraper_obj.get_candidates(*common.games['MAME_invalid'], status_dic = status_dic)

# --- Print search results ---
common.handle_get_candidates(candidate_list)
# pprint.pprint(candidate_list)
print_candidate_list(candidate_list)
candidate = candidate_list[0]

# --- Print list of assets found -----------------------------------------------------------------
print('*** Fetching game assets ****************************************************************')
# --- Get specific assets ---
print_game_assets(scraper_obj.get_assets(candidate, ASSET_TITLE_ID, status_dic))
print_game_assets(scraper_obj.get_assets(candidate, ASSET_SNAP_ID, status_dic))
print_game_assets(scraper_obj.get_assets(candidate, ASSET_BOXFRONT_ID, status_dic))
print_game_assets(scraper_obj.get_assets(candidate, ASSET_FLYER_ID, status_dic))