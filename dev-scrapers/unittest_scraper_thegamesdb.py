#!/usr/bin/python -B
# -*- coding: utf-8 -*-
import unittest, mock, os, sys

from mock import *
from mock import ANY
from tests.fakes import *
import xml.etree.ElementTree as ET

from resources.utils import *
from resources.net_IO import *
from resources.scrap import *
from resources.objects import *
from resources.constants import *

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def read_file_as_json(path):
    file_data = read_file(path)
    return json.loads(file_data, encoding = 'utf-8')

def mocked_gamesdb(url):

    mocked_json_file = ''

    if '/Developers' in url:
        mocked_json_file = Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\thegamesdb_developers.json"

    if '/Genres' in url:
        mocked_json_file = Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\thegamesdb_genres.json"


    if '/Publishers' in url:
        mocked_json_file = Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\thegamesdb_publishers.json"

    if '/Games/ByGameName' in url:
        mocked_json_file = Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\thegamesdb_castlevania_list.json"

    if '/Games/ByGameID' in url:
        mocked_json_file = Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\thegamesdb_castlevania.json"

    if '/Games/Images' in url:
        print('reading fake image file')
        mocked_json_file = Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\thegamesdb_images.json"

    if 'cdn.thegamesdb.net/' in url:
        return read_file(Test_gamesdb_scraper.TEST_ASSETS_DIR + "\\test.jpg")

    if mocked_json_file == '':
        return net_get_URL_as_json(url)

    print('reading mocked data from file: {}'.format(mocked_json_file))
    return read_file_as_json(mocked_json_file)

class Test_gamesdb_scraper(unittest.TestCase):

    ROOT_DIR = ''
    TEST_DIR = ''
    TEST_ASSETS_DIR = ''

    @classmethod
    def setUpClass(cls):
        set_log_level(LOG_DEBUG)

        cls.TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        cls.ROOT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR, os.pardir))
        cls.TEST_ASSETS_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'assets/'))

        print('ROOT DIR: {}'.format(cls.ROOT_DIR))
        print('TEST DIR: {}'.format(cls.TEST_DIR))
        print('TEST ASSETS DIR: {}'.format(cls.TEST_ASSETS_DIR))
        print('---------------------------------------------------------------------------')

    def get_test_settings(self):
        settings = {}
        settings['scan_metadata_policy'] = 3 # OnlineScraper only
        settings['scan_asset_policy'] = 0
        settings['metadata_scraper_mode'] = 1
        settings['asset_scraper_mode'] = 1
        settings['scan_clean_tags'] = True
        settings['scan_ignore_scrap_title'] = False
        settings['scraper_metadata'] = 0 # NullScraper
        settings['thegamesdb_apikey'] = 'abc123'
        settings['escape_romfile'] = False

        return settings

    @patch('resources.scrap.net_get_URL_as_json', side_effect = mocked_gamesdb)
    def test_scraping_metadata_for_game(self, mock_json_downloader):

        # arrange
        settings = self.get_test_settings()
        asset_factory = g_assetFactory

        launcher = StandardRomLauncher(None, settings, None, None, None, None, None)
        launcher.set_platform('Nintendo NES')

        rom = ROM({'id': 1234})
        fakeRomPath = FakeFile('/my/nice/roms/castlevania.zip')

        target = TheGamesDbScraper(settings, launcher)

        # act
        actual = target.scrape_metadata('castlevania', fakeRomPath, rom)

        # assert
        self.assertTrue(actual)
        self.assertEqual(u'Castlevania - The Lecarde Chronicles', rom.get_name())
        print(rom)

    # add actual gamesdb apikey above and comment out patch attributes to do live tests
    @patch('resources.scrap.net_get_URL_as_json', side_effect = mocked_gamesdb)
    @patch('resources.scrap.net_download_img')
    def test_scraping_assets_for_game(self, mock_img_downloader, mock_json_downloader):

        # arrange
        settings = self.get_test_settings()

        assets_to_scrape = [g_assetFactory.get_asset_info(ASSET_BANNER_ID), g_assetFactory.get_asset_info(ASSET_FANART_ID)]

        launcher = StandardRomLauncher(None, settings, None, None, None, None, None)
        launcher.set_platform('Nintendo NES')
        launcher.set_asset_path(g_assetFactory.get_asset_info(ASSET_BANNER_ID),'/my/nice/assets/banners/')
        launcher.set_asset_path(g_assetFactory.get_asset_info(ASSET_FANART_ID),'/my/nice/assets/fans/')

        rom = ROM({'id': 1234})
        fakeRomPath = FakeFile('/my/nice/roms/castlevania.zip')

        target = TheGamesDbScraper(settings, launcher)

        # act
        actuals = []
        for asset_to_scrape in assets_to_scrape:
            an_actual = target.scrape_asset('castlevania', asset_to_scrape, fakeRomPath, rom)
            actuals.append(an_actual)

        # assert
        for actual in actuals:
            self.assertTrue(actual)

        print(rom)
