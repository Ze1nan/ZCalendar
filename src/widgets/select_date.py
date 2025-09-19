from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from kivy.uix.screenmanager import Screen
from typing import Optional
from datetime import date

from calendar_store import CalendarStore
from app_config import Config

config = Config()
checks_data_store = CalendarStore()

class SelectDateApp(MDApp):
    _instance: Optional["SelectDateApp"] = None

    def __new__(cls, *args, **kwargs) -> "SelectDateApp":
        if not cls._instance:
            cls._instance = super(SelectDateApp, cls).__new__(cls)
            cls._instance.date_picker = None 
        return cls._instance

    def __init__(self, app: Screen, **kwargs):
        super(SelectDateApp, self).__init__(**kwargs)
        self.app = app
        self.date_picker = None

    def opened_date_picker(self) -> None:
        if self.date_picker is None:
            self.date_picker = MDDatePicker(
                overlay_color=config.current_theme['popup_overlay_color'],
                font_name=config.current_lang['font'],
                primary_color= config.current_theme['date_select_primary_color'],
                selector_color = config.current_theme['date_select_selector_color'],
                shadow_color=config.current_theme['popup_overlay_color'],
                text_button_color=config.current_theme['font_color'],
                title='',
                input_field_text_color_focus=
config.current_theme['font_color'],
                line_color= config.current_theme['popup_line_color_normal'],
                year=config.opened_date[0],
                month=config.opened_date[1]
            )
            self.date_picker.bind(on_save=self.on_date_select)
        
        self.date_picker.overlay_color = config.current_theme['popup_overlay_color']
        self.date_picker.primary_color = config.current_theme['date_select_primary_color']
        self.date_picker.selector_color = config.current_theme['date_select_selector_color']
        self.date_picker.shadow_color = config.current_theme['popup_overlay_color']
        self.date_picker.text_button_color = config.current_theme['font_color']
        self.date_picker.input_field_text_color_focus = config.current_theme['font_color']
        self.date_picker.line_color= config.current_theme['popup_line_color_normal']
        self.date_picker.year = config.opened_date[0]
        self.date_picker.month = config.opened_date[1] 
        
        self.date_picker.open()

    def on_date_select(self, instance: MDDatePicker, value: date, date_range: Optional[list] = None):
        self.app.open_calendar_date(value.year, value.month)