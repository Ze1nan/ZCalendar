from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

from app_config import Config

config = Config()

class GirlImage(Image):
    def __init__(self, **kwargs):
        kwargs.update({
            'source': config.current_theme['girl'], 
            'size_hint': (None, None), 
            'size': (dp(config.current_theme['girl_size']), dp(config.current_theme['girl_size'])),
            'pos_hint': {'right': 1, 'y': config.current_theme['girl_y']/Window.height}
        })
        super(GirlImage, self).__init__(**kwargs)

    def update(self):
        self.source = config.current_theme['girl']
        self.size = (dp(config.current_theme['girl_size']), dp(config.current_theme['girl_size']))