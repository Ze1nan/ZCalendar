from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.metrics import dp, sp
from typing import Optional

from app_config import Config
from widgets import ScreenWidget, GirlImage

config = Config()

class UsageScreen(Screen):
    _instance: Optional["UsageScreen"] = None
    
    def __new__(cls, *args, **kwargs) -> "UsageScreen":
        if not cls._instance:
            cls._instance = super(UsageScreen, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, calendar_name: str, **kwargs) -> None:
        super(UsageScreen, self).__init__(**kwargs)
        
        self.calendar_name = calendar_name
        
        Window.clearcolor = config.current_theme['background_color']
        
        with self.canvas:
            self.bg_rect_color = Color(*config.current_theme['background_color'])
            Rectangle(size=self.size, pos=self.pos)
            
        parent = BoxLayout(orientation='vertical', size_hint=(None,None), size=Window.size)
        self.add_widget(parent)
        
        # лайаут кнопок внизу экрана
        self.menu_buttons = BoxLayout(orientation='horizontal', size_hint=(1,None), height=Window.height*0.06)
        self.menu_buttons.add_widget(
            Button(
                text=config.current_lang['menu_buttons'][0],
                color= config.current_theme['menu_buttons_font_color'],
                font_size = sp(13),
                background_color= config.current_theme['menu_buttons_color'],
                background_normal='',
                background_down='',
                font_name=config.current_lang['font'],
                on_press=self.open_calendar
            )
        )
        
        self.menu_buttons.add_widget(
            Button(
                text=config.current_lang['menu_buttons'][1],
                color= config.current_theme['menu_buttons_font_color'],
                font_size = sp(13),
                background_color= config.current_theme['menu_buttons_color'], 
                background_normal='',
                background_down='',
                font_name=config.current_lang['font'],
                on_press=self.open_statistics
            )
        )
        
        self.menu_buttons.add_widget(
            Button(
                text=config.current_lang['menu_buttons'][2],
                color= config.current_theme['menu_buttons_font_color'],
                font_size = sp(13),
                background_color= config.current_theme['menu_buttons_color'], 
                background_normal='',
                background_down='',
                font_name=config.current_lang['font']
            )
        )
        
        self.menu_buttons.add_widget(
            Button(
                text=config.current_lang['menu_buttons'][3],
                color= config.current_theme['menu_buttons_font_color'],
                font_size = sp(13),
                background_color= config.current_theme['menu_buttons_color'], 
                background_normal='',
                background_down='',
                font_name=config.current_lang['font'],
                on_press=self.open_settings
            )
        )
        
        self.girl_png = GirlImage()
                                       
        parent.add_widget(self.menu_buttons)
        
        if config.current_girl:
            self.add_widget(self.girl_png)
            
    def open_calendar(self, instance: Button) -> None:
        ScreenWidget().change_screen('calendar', calendar_name=self.calendar_name) 
    def open_statistics(self, instance: Button) -> None:
        ScreenWidget().change_screen('statistics', calendar_name=self.calendar_name)
    def open_settings(self, instance: Button) -> None:
        ScreenWidget().change_screen('settings', calendar_name=self.calendar_name)