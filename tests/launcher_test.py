import unittest, mock, os, sys
from mock import *
from fakes import *

from resources.launchers import *

from resources.utils import *
from resources.disk_IO import *
from resources.utils_kodi import *

from resources.constants import *

class Test_Launcher(unittest.TestCase):
    
    ROOT_DIR = ''
    TEST_DIR = ''
    TEST_ASSETS_DIR = ''

    @classmethod
    def setUpClass(cls):
        set_use_print(True)
        set_log_level(LOG_DEBUG)
        
        cls.TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        cls.ROOT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR, os.pardir))
        cls.TEST_ASSETS_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'assets/'))
                
        print 'ROOT DIR: {}'.format(cls.ROOT_DIR)
        print 'TEST DIR: {}'.format(cls.TEST_DIR)
        print 'TEST ASSETS DIR: {}'.format(cls.TEST_ASSETS_DIR)
        print '---------------------------------------------------------------------------'

    def test_when_creating_a_launcher_with_not_exisiting_id_it_will_fail(self):
        # arrange
        launcher_data = {}

        # act
        factory = LauncherFactory(None, None, None)
        actual = factory.create(launcher_data)
        
        # assert
        self.assertIsNone(actual)
                
    @patch('resources.executors.ExecutorFactory')    
    def test_when_its_an_app_factory_loads_with_correct_launcher(self, mock_exeFactory):

        # arrange
        mock_exeFactory.create.return_value = FakeExecutor(None)
        
        launcher_data = {}
        launcher_data['id'] = 'ABC'
        launcher_data['type'] = LAUNCHER_STANDALONE
        launcher_data['application'] = 'path'
        launcher_data['toggle_window'] = True
        launcher_data['romext'] = ''
        launcher_data['application'] = ''
        launcher_data['args'] = ''
        launcher_data['args_extra'] = ''

        settings = {}
        settings['lirc_state'] = True

        # act
        factory = LauncherFactory(settings, None, mock_exeFactory)
        launcher = factory.create(launcher_data)
        
        # assert        
        actual = launcher.__class__.__name__
        expected = 'ApplicationLauncher'
        self.assertEqual(actual, expected)
        
    @patch('resources.executors.ExecutorFactory')
    def test_if_app_launcher_will_correctly_passthrough_parameters_when_launching(self, mock_exeFactory):

        # arrange
        expectedApp = 'AbcDefGhiJlkMnoPqrStuVw'
        expectedArgs = 'doop dap dib'

        launcher_data = {}
        launcher_data['id'] = 'ABC'
        launcher_data['type'] = LAUNCHER_STANDALONE
        launcher_data['application'] = expectedApp
        launcher_data['toggle_window'] = True
        launcher_data['args'] = expectedArgs
        launcher_data['m_name'] = 'MyApp'

        settings = {}
        settings['windows_cd_apppath'] = ''
        settings['windows_close_fds'] = ''
        settings['display_launcher_notify'] = False
        settings['media_state_action'] = 0
        settings['suspend_audio_engine'] = False
        settings['delay_tempo'] = 1
        
        mock = FakeExecutor(None)
        mock_exeFactory.create.return_value = mock

        factory = LauncherFactory(settings, None, mock_exeFactory)
        launcher = factory.create(launcher_data)

        # act
        launcher.launch()

        # assert
        self.assertEqual(expectedApp, mock.actualApplication.getOriginalPath())
        self.assertEqual(expectedArgs, mock.actualArgs)
        
    @patch('resources.executors.ExecutorFactory')
    def test_if_app_launcher_will_correctly_alter_arguments_when_launching(self, mock_exeFactory):

        # arrange
        set_log_level(LOG_VERB)
        set_use_print(True)

        expectedApp = 'C:\Sparta\Action.exe'
        expectedArgs = 'this is C:\Sparta'

        launcher_data = {}
        launcher_data['id'] = 'ABC'
        launcher_data['type'] = 'STANDALONE'
        launcher_data['application'] = expectedApp
        launcher_data['toggle_window'] = True
        launcher_data['args'] = 'this is $apppath%'
        launcher_data['m_name'] = 'MyApp'
        
        mock = FakeExecutor(None)
        mock_exeFactory.create.return_value = mock

        settings = {}
        settings['windows_cd_apppath'] = ''
        settings['windows_close_fds'] = ''
        settings['display_launcher_notify'] = False
        settings['media_state_action'] = 0
        settings['suspend_audio_engine'] = False
        settings['delay_tempo'] = 1
        
        factory = LauncherFactory(settings, None, mock_exeFactory)
        launcher = factory.create(launcher_data)

        # act
        launcher.launch()

        # assert
        self.assertEqual(expectedApp, mock.actualApplication.getOriginalPath())
        self.assertEqual(expectedArgs, mock.actualArgs)
            
    @patch('resources.romsets.RomSetFactory')
    @patch('resources.executors.ExecutorFactory')
    def test_when_using_rom_the_factory_will_get_the_correct_launcher(self, mock_exeFactory, mock_romsFactory):
        
        # arrange
        set_log_level(LOG_VERB)
        set_use_print(True)

        launcher_data = {}
        launcher_data['id'] = 'ABC'
        launcher_data['application'] = 'path'
        launcher_data['type'] = LAUNCHER_ROM
        launcher_data['toggle_window'] = True
        launcher_data['romext'] = ''
        launcher_data['application'] = ''
        launcher_data['args'] = ''
        launcher_data['args_extra'] = ''
        launcher_data['roms_base_noext'] = 'snes'

        rom = {}
        rom['m_name'] = 'TestCase'        

        settings = {}
        settings['lirc_state'] = True
        settings['escape_romfile'] = True

        # act
        factory = LauncherFactory(settings, mock_romsFactory, mock_exeFactory)
        launcher = factory.create(launcher_data)
        launcher.load_rom(rom)
        
        # assert
        actual = launcher.__class__.__name__
        expected = 'StandardRomLauncher'
        self.assertEqual(actual, expected)
                
    @patch('resources.romsets.RomSetFactory')
    @patch('resources.executors.ExecutorFactory')
    def test_if_rom_launcher_will_correctly_passthrough_the_application_when_launching(self, mock_exeFactory, mock_romsFactory):
        
        # arrange
        set_log_level(LOG_VERB)
        set_use_print(True)

        launcher_data= {}
        launcher_data['id'] = 'ABC'
        launcher_data['type'] = LAUNCHER_ROM
        launcher_data['application'] = 'path'
        launcher_data['toggle_window'] = True
        launcher_data['romext'] = ''
        launcher_data['application'] = ''
        launcher_data['args'] = '-a -b -c -d -e $rom$ -yes'
        launcher_data['args_extra'] = ''
        launcher_data['roms_base_noext'] = 'snes'

        rom = {}
        rom['id'] = 'qqqq'
        rom['m_name'] = 'TestCase'
        rom['filename'] = 'testing.zip'
        rom['altapp'] = ''
        rom['altarg'] = ''
        
        settings = {}
        settings['lirc_state'] = True
        settings['escape_romfile'] = True
        settings['display_launcher_notify'] = False
        settings['media_state_action'] = 0
        settings['suspend_audio_engine'] = False
        settings['delay_tempo'] = 1

        mock_romsFactory.create.return_value = FakeRomSet(rom)
        mock = FakeExecutor(None)
        mock_exeFactory.create.return_value = mock

        expected = launcher_data['application']
        expectedArgs = '-a -b -c -d -e testing.zip -yes'

        factory = LauncherFactory(settings, mock_romsFactory, mock_exeFactory)
        launcher = factory.create(launcher_data)
        launcher.load_rom(rom)

        # act
        launcher.launch()

        # assert
        self.assertEqual(expected, mock.actualApplication.getOriginalPath())
        self.assertEqual(expectedArgs, mock.actualArgs)
                
    @patch('resources.romsets.RomSetFactory')
    @patch('resources.executors.ExecutorFactory')
    def test_if_rom_launcher_will_use_the_multidisk_launcher_when_romdata_has_disks_field_filled_in(self, mock_exeFactory, mock_romsFactory):
        
        # arrange
        set_log_level(LOG_VERB)
        set_use_print(True)

        launcher_data = {}
        launcher_data['id'] = 'ABC'
        launcher_data['type'] = LAUNCHER_ROM
        launcher_data['application'] = 'path'
        launcher_data['toggle_window'] = True
        launcher_data['romext'] = ''
        launcher_data['application'] = ''
        launcher_data['args'] = ''
        launcher_data['args_extra'] = ''
        launcher_data['roms_base_noext'] = 'snes'

        rom= {}
        rom['m_name'] = 'TestCase'
        rom['disks'] = ['disc01.zip', 'disc02.zip']
        
        settings = {}
        settings['lirc_state'] = True
        settings['escape_romfile'] = True
        
        mock_romsFactory.create.return_value = FakeRomSet(rom)
        mock = FakeExecutor(None)
        mock_exeFactory.create.return_value = mock

        # act
        factory = LauncherFactory(settings, mock_romsFactory, mock_exeFactory)
        launcher = factory.create(launcher_data)
        launcher.load_rom(rom)
        
        # assert        
        actual = launcher.__class__.__name__
        expected = 'StandardRomLauncher'
        self.assertEqual(actual, expected)
                
    @patch('resources.romsets.RomSetFactory')
    @patch('resources.launchers.xbmcgui.Dialog.select')
    @patch('resources.executors.ExecutorFactory')
    def test_if_rom_launcher_will_apply_the_correct_disc_in_a_multidisc_situation(self, mock_exeFactory, mock_dialog, mock_romsFactory):

        # arrange
        set_log_level(LOG_VERB)
        set_use_print(True)

        launcher_data = {}
        launcher_data['id'] = 'ABC'
        launcher_data['type'] = LAUNCHER_ROM
        launcher_data['application'] = 'c:\\temp\\'
        launcher_data['toggle_window'] = True
        launcher_data['romext'] = ''
        launcher_data['application'] = ''
        launcher_data['args'] = '-a -b -c -d -e $rom$ -yes'
        launcher_data['args_extra'] = ''
        launcher_data['roms_base_noext'] = 'snes'

        rom = {}
        rom['id'] = 'qqqq'
        rom['m_name'] = 'TestCase'
        rom['filename'] = 'd:\\games\\discXX.zip'
        rom['altapp'] = ''
        rom['altarg'] = ''
        rom['disks'] = ['disc01.zip', 'disc02.zip']

        mock_dialog.return_value = 1
        mock_romsFactory.create.return_value = FakeRomSet(rom)
        mock = FakeExecutor(None)
        mock_exeFactory.create.return_value = mock

        settings = {}
        settings['lirc_state'] = True
        settings['escape_romfile'] = True
        settings['display_launcher_notify'] = False
        settings['media_state_action'] = 0
        settings['suspend_audio_engine'] = False
        settings['delay_tempo'] = 1

        expected = launcher_data['application']
        expectedArgs = '-a -b -c -d -e d:\\games\\disc02.zip -yes'

        factory = LauncherFactory(settings, mock_romsFactory, mock_exeFactory)
        launcher = factory.create(launcher_data)
        launcher.load_rom(rom)

        # act
        launcher.launch()

        # assert
        self.assertEqual(expectedArgs, mock.actualArgs)
    
    @patch('resources.launchers.is_windows')
    @patch('resources.launchers.is_android')
    @patch('resources.launchers.is_linux')    
    @patch('resources.romsets.RomSetFactory')
    @patch('resources.executors.ExecutorFactory')
    def test_if_retroarch_launcher_will_apply_the_correct_arguments_when_running_on_android(self, mock_exeFactory, mock_romsFactory, is_linux_mock,is_android_mock, is_win_mock):
        
        # arrange
        is_linux_mock.return_value = False
        is_win_mock.return_value = False
        is_android_mock.return_value = True

        launcher_data = {}
        launcher_data['type'] = LAUNCHER_RETROARCH
        launcher_data['id'] = 'ABC'
        launcher_data['toggle_window'] = True
        launcher_data['romext'] = None
        launcher_data['args_extra'] = None
        launcher_data['roms_base_noext'] = 'snes'
        launcher_data['core'] = 'mame_libretro_android.so'
        launcher_data['application'] = None

        rom = {}
        rom['id'] = 'qqqq'
        rom['m_name'] = 'TestCase'
        rom['filename'] = 'superrom.zip'
        rom['altapp'] = None

        mock_romsFactory.create.return_value = FakeRomSet(rom)
        mock = FakeExecutor(None)
        mock_exeFactory.create.return_value = mock

        settings = {}
        settings['lirc_state'] = True
        settings['escape_romfile'] = True
        settings['display_launcher_notify'] = False
        settings['media_state_action'] = 0
        settings['suspend_audio_engine'] = False
        settings['delay_tempo'] = 1

        expected = '/system/bin/am'
        expectedArgs = "start --user 0 -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -e ROM 'superrom.zip' -e LIBRETRO /data/data/com.retroarch/cores/mame_libretro_android.so -e CONFIGFILE /storage/emulated/0/Android/data/com.retroarch/files/retroarch.cfg -e IME com.android.inputmethod.latin/.LatinIME -e REFRESH 60 -n com.retroarch/.browser.retroactivity.RetroActivityFuture"

        factory = LauncherFactory(settings, mock_romsFactory, mock_exeFactory)
        launcher = factory.create(launcher_data)
        launcher.load_rom(rom)

        # act
        launcher.launch()

        # assert
        self.assertEqual(expected, mock.getActualApplication().getPath())
        self.assertEqual(expectedArgs, mock.actualArgs)

if __name__ == '__main__':
   unittest.main()
