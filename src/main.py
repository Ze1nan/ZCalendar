from kivy.app import App
import os

from calendar_store import CalendarStore
from app_config import Config

from widgets import ScreenWidget

import logging
logging.getLogger('matplotlib').setLevel(logging.CRITICAL)

os.environ['KIVY_NO_CONSOLELOG'] = '1'

config = Config()
checks_data_store = CalendarStore()
        
class CalendarApp(App):
    def build(self):
        sw = ScreenWidget()
        
        sw.change_screen('calendar', None)
        
        return sw
        
if __name__ == '__main__':
    CalendarApp().run()