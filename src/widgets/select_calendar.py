from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import sp

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField 

from PIL import Image, ImageDraw, ImageFont
from typing import Optional
import re

from calendar_store import CalendarStore
from app_config import Config

config = Config()
checks_data_store = CalendarStore()

class SelectCalendarLayout(ScrollView):
    _instance: Optional["SelectCalendarLayout"] = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs) -> "SelectCalendarLayout":
        if not cls._instance:
            cls._instance = super(SelectCalendarLayout, cls).__new__(cls)
        else:
            SelectCalendarLayout._initialized = True
        return cls._instance
        
    def __init__(self, select_calendar: str, calendar_screen: Screen, **kwargs) -> None:
        super(SelectCalendarLayout, self).__init__(**kwargs)
        
        self.select_calendar = select_calendar
        self.calendar_screen = calendar_screen
        
        self.bar_width = 0
        self.do_scroll_y = False
        self.do_scroll_x = True
        
        if not self._initialized:
            self.layout = BoxLayout(orientation='horizontal', size_hint_x=None)
            CalendarButton.initialize(self.layout) 
            self.layout.bind(minimum_width=self.layout.setter('width'))
            self.add_widget(self.layout)    
            
            self.add_button = None
            def create_add_button(*args) -> None:
                nonlocal button
                self.add_button = Button(text='+', size_hint=(None,None), width=button.height, height=button.height, background_color=(0,0,0,0), color=config.current_theme['font_color'])
                
                self.add_button.bind(on_release=self.create_calendar)
    
                self.layout.add_widget(self.add_button)
            Clock.schedule_once(create_add_button) 
        
        with checks_data_store as store:
            self.calendars = store.get_calendars()
        
        for calendar in self.calendars:
            button = CalendarButton(calendar)
            if calendar == select_calendar:
                button.on_focus = True 
                button.update_color()
                
            button.bind(on_press=self.change_focus)
            self.layout.add_widget(button)
        
    def change_focus(self, instance: Button) -> None:
        if instance.on_focus:
            RenameCalendarPopup().open_dialog(instance) 
            return
        for child in self.layout.children:
            if isinstance(child, CalendarButton):
                child.on_focus = False
                child.update_color()
        
        if isinstance(instance, CalendarButton):
            instance.on_focus = True
            instance.update_color()
        
            self.calendar_screen.change_calendar(instance.name)
            
    def create_calendar(self, instance: Button) -> None:
        max_number = 0
        with checks_data_store as store:
            for calendar in store.get_calendars():
                match = re.fullmatch(r"Новый календарь (\d+)", calendar)
                if match:
                    number = int(match.group(1))
                    if number > max_number:
                        max_number = number
        
            new_calendar_name = config.current_lang['new_calendar'] + ' ' + str(max_number+1)
            
            if store.create_calendar(new_calendar_name):
                new_button = CalendarButton(new_calendar_name)
                self.change_focus(new_button)
                new_button.bind(on_release=self.change_focus)
                
                self.layout.remove_widget(self.add_button)
                self.layout.add_widget(new_button)
                self.layout.add_widget(self.add_button)
            
    def update(self) -> None:
        self.layout.remove_widget(self.add_button)
        button = CalendarButton('None')
        def create_add_button(*args) -> None:
            nonlocal button
            self.add_button = Button(text='+', size_hint=(None,None), width=button.height, height=button.height, background_color=(0,0,0,0), color=config.current_theme['font_color'])
                
            self.add_button.bind(on_release=self.create_calendar)
    
            self.layout.add_widget(self.add_button)
        Clock.schedule_once(create_add_button) 

        with checks_data_store as store:
            calendars = store.get_calendars()
        
        for i, calendar in enumerate(calendars):    
            if calendar not in [calendar_btn.name for calendar_btn in self.layout.children]:
                button = CalendarButton(calendar)
                button.bind(on_press=self.change_focus)
                self.layout.add_widget(button) 
                
        for i, calendar in enumerate(self.layout.children):
            if calendar.name not in calendars:
                self.layout.remove_widget(calendar)
                continue
            if (calendar.name == self.select_calendar) if self.select_calendar in calendars else (i == 0):
                if calendar.on_focus is not True:
                    calendar.on_focus = True
                    calendar.update_color()
                    checks_data_store.select_calendar(calendar.name)
            elif calendar.on_focus is True:
                calendar.on_focus = False
                calendar.update_color()
                checks_data_store.select_calendar(calendar.name)
        
class CalendarButton(Button):
    on_focus = ObjectProperty(False)
    bg_color = ObjectProperty((1,1,1,1))
    name = ObjectProperty('')
    def __init__(self, name: str, **kwargs) -> None:
        super(CalendarButton, self).__init__(**kwargs)
        
        self.name = name
        self.size_hint = (None,1)
        self.font_name = config.current_lang['font']        
        self.bg_color = config.current_theme['buttons_color']
        self.color = config.current_theme['font_color']
        self.background_color = (0, 0, 0, 0)
        self.font_size = sp(15)
        self.text = '' 
        
        shorted_text, text_width, is_long = self.truncate_text(self.name)
        
        if is_long:
            self.name = shorted_text
            self.width = Window.width*0.5
        else:
            self.width = Window.width*0.15 + text_width
            
        self.name_label = Label(text=self.name, size_hint=(None,None), size=self.size, pos=(self.x, self.y), font_name=self.font_name, color=self.color, halign='center', valign='middle')
    
        self.name_label.bind(size=self.update_color, pos=self.update_color)
        
        self.add_widget(self.name_label)
        
        Clock.schedule_once(self.update_color)

    def update_name(self, new_name: str) -> None:
        new_name, text_width, is_long = self.truncate_text(new_name)
        self.name = new_name
        self.name_label.text = new_name
        
        if is_long:
            self.width = Window.width*0.5
        else:
            self.width = Window.width*0.15 + text_width
        
        self.update_color()
        
        for child in self.parent.children:
            if isinstance(child, CalendarButton):
                Clock.schedule_once(child.update_color)
            
    def update_color(self, *args) -> None:
        self.canvas.before.clear()
        if self.on_focus:
            self.bg_color = config.current_theme['buttons_color'] 
            
            with self.canvas.before:
                Color(*self.bg_color)
                RoundedRectangle(size=self.size, pos=self.pos, color=self.bg_color, radius=(20,20,0,0))
        self.name_label.size = (self.width, self.height)
        self.name_label.pos = (self.x, self.y)
                    
    def truncate_text(self, text: str) -> str:
        image = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(config.current_lang['font'], int(sp(15)))
            
        truncated_text = ''
        current_width = 0
        is_long = False
            
        for char in text:
            char_width = draw.textlength(char, font=font)
            if (current_width + char_width + draw.textlength('..', font=font)) > Window.width*0.5:
                truncated_text += '..'
                is_long = True
                break
            truncated_text += char
            current_width += char_width
                
        return truncated_text, current_width, is_long
        
    @staticmethod
    def initialize(layout: BoxLayout) -> None:
        btn = CalendarButton('')
        layout.add_widget(btn)
        layout.remove_widget(btn)
 
class RenameCalendarPopup(MDApp):
    _instance: Optional["RenameCalendarPopup"] = None
        
    def __new__(cls, *args, **kwargs) -> "RenameCalendarPopup":
        if not cls._instance:
            cls._instance = super(RenameCalendarPopup, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, **kwargs) -> None:
        super(RenameCalendarPopup, self).__init__(**kwargs)
        
        self.instance = None
        self.textfield = None
        self.dialog = None
        
    def open_dialog(self, instance: Button) -> None:
        if self.dialog:
            self.dialog = None
        
        self.instance = instance
        
        self.textfield = MDTextField(mode='line', hint_text='Новое имя' if config.current_lang['code'] == 'ru' else 'New Name', max_text_length=25, text_color_focus=config.current_theme['font_color'], text_color_normal=config.current_theme['font_color'], line_color_normal=config.current_theme['popup_line_color_normal'], hint_text_color_normal=config.current_theme['popup_hint_text_color_normal'], line_color_focus=config.current_theme['popup_line_color_focus'], hint_text_color_focus=config.current_theme['popup_hint_text_color_focus'],size_hint=(None,None), size=(Window.size[0]*0.7, 100), font_name=config.current_lang['font'])
            
        bl_field = BoxLayout(orientation = 'vertical', size_hint = (None,None), width=Window.size[0]*0.7)

        bl_field.add_widget(self.textfield)
            
        self.dialog = MDDialog(
            title='Переименовать календарь' if config.current_lang['code'] == 'ru' else 'Rename calendar',
            buttons=[
                MDFlatButton(
                    text="Отмена" if config.current_lang['code'] == 'ru' else 'Cancel',
                    on_release=self.close_dialog
                ),
                MDFlatButton(
                    text="Ок" if config.current_lang['code'] == 'ru' else "Ok",
                    on_release=self.confirm_create
                ),
            ],
            content_cls=bl_field,
            type='custom',
            auto_dismiss = False,
            pos_hint={'y':0.596},
            size_hint=(None, None),
            size = (Window.size[0]/1.2, Window.size[1]/50),
            md_bg_color=config.current_theme['popup_color'],
            overlay_color=config.current_theme['popup_overlay_color'] 
        )
            
        self.dialog.open(animation=False)

    def close_dialog(self, *args) -> None:
        self.dialog.dismiss()

    def confirm_create(self, *args):
        new_name = self.textfield.text.strip()
        with checks_data_store as store:
            if new_name.lower() != store.default_table.lower() and new_name.lower() not in map(str.lower, store.get_calendars()):
                store.rename_calendar(new_name)
                self.instance.update_name(new_name)
        self.dialog.dismiss()