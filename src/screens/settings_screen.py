from kivy.input.providers.mouse import MouseMotionEvent
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image as KivyImage
from kivy.properties import ObservableReferenceList
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label

from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.lang import Builder

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.selectioncontrol import MDCheckbox

from typing import List, Dict, Optional, Tuple, Union

from app_config import Config
from calendar_store import CalendarStore
from widgets import ScreenWidget, GirlImage
from utils import get_text_width

config = Config()

class SettingsScreen(Screen):
    _instance: Optional["SettingsScreen"] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> "SettingsScreen":
        if not cls._instance:
            cls._instance = super(SettingsScreen, cls).__new__(cls)
        else:
            SettingsScreen._initialized = True
        return cls._instance
    
    def __init__(self, calendar_name: str, **kwargs) -> None:
        super(SettingsScreen, self).__init__(**kwargs)

        if SettingsScreen._initialized:
            if self.number_format_al not in self.layout.children and config.easters['roman_numerals']: # pylint: disable=E0203
                self.layout.add_widget(self.number_format_al, index=4) # pylint: disable=E0203
            if self.girl_al not in self.layout.children and config.easters['girl']: # pylint: disable=E0203
                self.layout.add_widget(self.girl_al, index=4) # pylint: disable=E0203
            return
        
        self.calendar_name = calendar_name
        
        with self.canvas:
            self.bg_color = Color(*config.current_theme['background_color'])
            self.rect = Rectangle(size=self.size, pos=self.pos)
        def _update_rect(*args):
            self.rect.size = self.size
            self.rect.pos = self.pos
            
        self.bind(size=_update_rect, pos=_update_rect)

        # ATTRIBUTES FOR LAYOUTS
        self.lang_buttons = None
        self.theme_buttons = None
        self.multiplier_buttons = None
        self.delete_label = None
        self.trash_img = None

        # SELECT LANGUAGE LAYOUT
        self.lang_al = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None)
        
        lang_bl = SettingsBoxLayout(orientation='horizontal', width=Window.width-100, size_hint=(None,None), radius=[20,20,0,0])
        
        self.lang_label = Label(size_hint_x=None, width=get_text_width(config.current_lang['language'])+dp(18.2),color=config.current_theme['font_color'], text=config.current_lang['language'], font_size=sp(16), font_name=config.current_lang['font'])
        self.selected_lang_label = Label(size_hint_x=None,width=dp(12),color=(0.6,0.6,0.6,1), text=config.current_lang['code'].capitalize(), font_size=sp(16), font_name=config.current_lang['font'])
        
        lang_dropdown = LangDropDown(self)
        
        lang_bl.add_widget(self.lang_label)
        lang_bl.add_widget(Widget(size_hint_x=1))
        lang_bl.add_widget(self.selected_lang_label)
        lang_bl.add_widget(lang_dropdown) 
        
        self.lang_al.add_widget(lang_bl)
        
        # SELECT THEME LAYOUT
        self.theme_al = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None)
        
        theme_bl = SettingsBoxLayout(orientation='horizontal', width=Window.width-100, size_hint=(None,None), radius=[0,0,0,0])
        
        self.theme_label = Label(size_hint_x=None, width=get_text_width(config.current_lang['theme'])+dp(18.2), color=config.current_theme['font_color'], text=config.current_lang['theme'], font_size=sp(16), font_name=config.current_lang['font'])
        self.selected_theme_label = Label(size_hint_x=None, width=dp(25), color=(0.6,0.6,0.6,1), text=config.current_theme['name'].capitalize(), font_size=sp(16), font_name=config.current_lang['font'])
        
        theme_dropdown = ThemeDropDown(self)
        
        theme_bl.add_widget(self.theme_label)
        theme_bl.add_widget(Widget(size_hint_x=1))
        theme_bl.add_widget(self.selected_theme_label)
        theme_bl.add_widget(theme_dropdown)  
        
        self.theme_al.add_widget(theme_bl)
        
        # SELECT MULTIPLIER LAYOUT
        self.multiplier_al = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None)
        
        multiplier_bl = SettingsBoxLayout(orientation='horizontal', width=Window.width-100, size_hint=(None,None), radius=[0,0,0,0])
        
        self.multiplier_label = Label(size_hint_x=None, width=get_text_width(config.current_lang['check_count'])+dp(5), color=config.current_theme['font_color'], text=config.current_lang['check_count'], font_size=sp(16), font_name=config.current_lang['font'])
        self.selected_multiplier_label = Label(size_hint_x=None, width=dp(5), color=(0.6,0.6,0.6,1), text=str(config.multiplier), font_size=sp(16), font_name=config.current_lang['font'])
        
        multiplier_dropdown = MultiplierDropDown(self)
        
        multiplier_bl.add_widget(self.multiplier_label)
        multiplier_bl.add_widget(Widget(size_hint_x=1))
        multiplier_bl.add_widget(self.selected_multiplier_label)
        multiplier_bl.add_widget(multiplier_dropdown)  
        
        self.multiplier_al.add_widget(multiplier_bl)

        # SELECT NUMBER FORMAT LAYOUT
        self.number_format_al = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None)
        
        number_format_bl = SettingsBoxLayout(
            orientation='horizontal',
            width=Window.width-100,
            size_hint=(None,None),
            radius=[0,0,0,0]
        )
        
        self.number_format_label = Label(
            size_hint_x=None,
            width=get_text_width(config.current_lang['roman_numerals'])+dp(10),
            halign='left', color=config.current_theme['font_color'],
            text=config.current_lang['roman_numerals'],
            font_size=sp(16),
            font_name=config.current_lang['font']
        )
        
        self.switch_format = OptionSwitch(size_hint_x=None)
        
        number_format_bl.add_widget(self.number_format_label)
        number_format_bl.add_widget(Widget(size_hint_x=1))
        number_format_bl.add_widget(self.switch_format)
        
        self.number_format_al.add_widget(number_format_bl)

        # GIRL LAYOUT
        self.girl_png = GirlImage()
        
        self.girl_al = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None)
            
        girl_bl = SettingsBoxLayout(
            orientation='horizontal',
            width=Window.width-100,
            size_hint=(None,None),
            radius=[0,0,0,0]
        )
            
        self.girl_label = Label(
            size_hint_x=None,
            width=get_text_width(config.current_lang['girl'])+dp(20),
            color=config.current_theme['font_color'],
            text=config.current_lang['girl'],
            font_size=sp(16),
            font_name=config.current_lang['font']
        )
            
        self.switch_girl = OptionSwitch(size_hint_x=None)
        self.switch_girl.active = config.current_girl
            
        def turn_girl(instance, *args):
            instance.active = not instance.active
            config.update('config', 'girl', instance.active)
            
            if not config.easters['girl']:
                config.update('easters', 'girl', True)

            if instance.active and not self.girl_png in self.children:
                self.add_widget(self.girl_png)
            elif self.girl_png in self.children:
                self.remove_widget(self.girl_png)
                
            return 1
                
        self.switch_girl.on_click = turn_girl.__get__(self.switch_girl, None)
        girl_bl.add_widget(self.girl_label)
        girl_bl.add_widget(Widget(size_hint_x=1))
        girl_bl.add_widget(self.switch_girl)
            
        self.girl_al.add_widget(girl_bl)

        # MENU BUTTONS LAYOUT
        self.menu_buttons = BoxLayout(orientation='horizontal', size_hint=(1,None), height=Window.height*0.06)

        self.menu_buttons.add_widget(
            Button(
                text=config.current_lang['menu_buttons'][0],
                color= config.current_theme['menu_buttons_font_color'],
                font_size=sp(13),
                background_color=config.current_theme['menu_buttons_color'],
                background_normal='',
                background_down='',
                font_name=config.current_lang['font'],
                on_release=self.open_calendar
            )
        )
        self.menu_buttons.add_widget(
            Button(
                text=config.current_lang['menu_buttons'][1],
                color= config.current_theme['menu_buttons_font_color'],
                font_size = sp(13),
                background_color=config.current_theme['menu_buttons_color'],
                background_normal='',
                background_down='',
                font_name=config.current_lang['font'],
                on_release=self.open_statistics
            )
        )
        self.menu_buttons.add_widget(
            Button(
                text=config.current_lang['menu_buttons'][2],
                color= config.current_theme['menu_buttons_font_color'],
                font_size=sp(13),
                background_color=config.current_theme['menu_buttons_color'],
                background_normal='',
                background_down='',
                font_name=config.current_lang['font'],
                on_release=self.open_usage
            )
        )
        self.menu_buttons.add_widget(
            Button(
                text=config.current_lang['menu_buttons'][3],
                color= config.current_theme['menu_buttons_font_color'],
                font_size=sp(13),
                background_color=config.current_theme['menu_buttons_color'],
                background_normal='',
                background_down='',
                font_name=config.current_lang['font']
            )
        )

        # MAIN LAYOUT      
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(Widget(size_hint=(1,0.2)))
        self.layout.add_widget(self.lang_al) 
        self.layout.add_widget(self.theme_al)
        if config.easters['roman_numerals']:
            self.layout.add_widget(self.number_format_al)
        if config.easters['girl']:
            self.layout.add_widget(self.girl_al)
        self.layout.add_widget(self.multiplier_al)
        self.layout.add_widget(DeleteDataButton(self))
        self.layout.add_widget (Widget())
        self.layout.add_widget(self.menu_buttons)
        self.add_widget(self.layout)

        if self.girl_png in self.children:
            self.remove_widget(self.girl_png)
        if config.current_girl:
            self.add_widget(self.girl_png) 
            
    def open_calendar(self, instance: Button) -> None:
        ScreenWidget().change_screen('calendar', calendar_name=self.calendar_name)
    def open_statistics(self, instance: Button) -> None:
        ScreenWidget().change_screen('statistics', calendar_name=self.calendar_name)
    def open_usage(self, instance: Button) -> None:
        ScreenWidget().change_screen('usage', calendar_name=self.calendar_name)

class LangDropDown(BoxLayout):
    def __init__(self, screen: SettingsScreen, **kwargs) -> None:
        super(LangDropDown, self).__init__(**kwargs)
        
        dropdown = DropDown()
        drop_languages = [lang.capitalize() for lang in config.get_languages_list() if lang in config.easters and config.easters[lang] or lang not in config.easters]
             
        self.size_hint = (None,None)
        
        screen.lang_buttons = []
        for i, lang in enumerate(drop_languages):
            btn = DropButton(
                text=lang,
                size_hint=(None,None),
                is_last=True if i+1 == len(drop_languages) else False,
                font_name=config.current_lang['font'],
                color=config.current_theme['font_color'],
                font_size=sp(15)
            )
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            screen.lang_buttons.append(btn)
            
        mainbutton = Button(
            size_hint=(0.5, None),
            background_normal='textures/dropdown-arrow-gray.png',
            background_down='textures/dropdown-arrow-gray.png',
            background_color=(1,1,1,1)
        )
        
        def on_select(mainbutton: Button, lang: str) -> None:
            self.save_lang(lang)
            
            screen.lang_label.text = config.current_lang['language']
            screen.selected_lang_label.text = lang
            screen.theme_label.text = config.current_lang['theme']
            screen.multiplier_label.text = config.current_lang['check_count']
            
            if config.easters['girl']:
                screen.girl_label.text = config.current_lang['girl']
            screen.delete_label.text = config.current_lang['delete_data']
        
            labels = [screen.lang_label, screen.theme_label, screen.multiplier_label, screen.delete_label]
            padding = [18.2, 18.2, 5, 12]
            if config.easters['roman_numerals']:
                screen.number_format_label.text = config.current_lang['roman_numerals']
                labels.append(screen.number_format_label)
                padding.append(10)
            if config.easters['girl']:
                screen.girl_label.text = config.current_lang['girl']
                labels.append(screen.girl_label)
                padding.append(20)
            
            for label, pad in zip(labels, padding):
                label.width = get_text_width(label.text) + dp(pad)
                label.font_name = config.current_lang['font']
                
            screen.selected_lang_label.font_name = config.current_lang['font'] 
            screen.selected_theme_label.font_name = config.current_lang['font']
            screen.selected_multiplier_label.font_name = config.current_lang['font']
            
            for i, btn in enumerate(reversed(screen.menu_buttons.children)):
                btn.text = config.current_lang['menu_buttons'][i]
                btn.font_name = config.current_lang['font']
            for btn in screen.lang_buttons:
                btn.font_name = config.current_lang['font']
            for btn in screen.theme_buttons:
                btn.font_name = config.current_lang['font']
        
        mainbutton.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: on_select(mainbutton, x))
        
        self.add_widget(mainbutton)
        
        def update_dropdown(*args) -> None:
            dropdown.clear_widgets()
            for button in screen.lang_buttons:
                if button.text != mainbutton.text:
                    dropdown.add_widget(button)
                else:
                    dropdown.remove_widget(button)
        
        mainbutton.bind(on_release=update_dropdown)

    def save_lang(self, lang: str) -> None:
        config.update('config', 'current_lang', lang.lower())
        
class ThemeDropDown(BoxLayout):
    def __init__(self, screen: SettingsScreen, **kwargs) -> None:
        super(ThemeDropDown, self).__init__(**kwargs)
        dropdown = DropDown()
        drop_themes = [theme.capitalize() for theme in config.get_themes_list()]
        
        self.size_hint = (None,None)

        screen.theme_buttons = []
        for i, theme in enumerate(drop_themes):
            btn = DropButton(
                text=theme,
                size_hint=(None,None),
                is_last=True if i+1 == len(drop_themes) else False,
                font_name=config.current_lang['font'],
                color=config.current_theme['font_color'],
                font_size=sp(13)
            )
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            screen.theme_buttons.append(btn)
            
        mainbutton = Button(
            size_hint=(0.5, None),
            background_normal='textures/dropdown-arrow-gray.png',
            background_down='textures/dropdown-arrow-gray.png',
            background_color=(1,1,1,1)
        )
        
        def on_select(mainbutton: Button, theme: str) -> None:
            self.save_theme(theme)

            if screen.girl_png:
                screen.girl_png.update()
            
            SettingsBoxLayout.update_rect_color(config.current_theme)
            
            if config.easters['roman_numerals']:
                screen.switch_format.switch_bg_color = config.current_theme['switch_bg_color']
                screen.switch_format.switch_outline_color = config.current_theme['switch_outline_color']
            
            if config.easters['girl']:
                screen.switch_girl.switch_bg_color = config.current_theme['switch_bg_color']
                screen.switch_girl.switch_outline_color = config.current_theme['switch_outline_color']
                screen.girl_label.color = config.current_theme['font_color']
                
            screen.delete_label.color = config.current_theme['font_color']
            
            screen.bg_color.r = config.current_theme['background_color'][0]
            screen.bg_color.g = config.current_theme['background_color'][1]
            screen.bg_color.b = config.current_theme['background_color'][2]
            
            screen.selected_theme_label.text = theme
            
            screen.theme_label.color = config.current_theme['font_color']
            screen.lang_label.color = config.current_theme['font_color']
            screen.multiplier_label.color = config.current_theme['font_color']
            if config.easters['roman_numerals']:
                screen.number_format_label.color = config.current_theme['font_color']
            
            screen.trash_img.source = config.current_theme['trash_can']

            for btn in screen.menu_buttons.children:
                btn.color = config.current_theme['menu_buttons_font_color']
                btn.background_color = config.current_theme['menu_buttons_color']
            for btn in screen.theme_buttons:
                btn.color = config.current_theme['font_color']
                btn.bg_color = config.current_theme['period_button_color']
            for btn in screen.lang_buttons:
                btn.color = config.current_theme['font_color']
                btn.bg_color = config.current_theme['period_button_color']
            for btn in screen.multiplier_buttons:
                btn.color = config.current_theme['font_color']
                btn.bg_color = config.current_theme['period_button_color']
            
        mainbutton.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: on_select(mainbutton, x))
        
        self.add_widget(mainbutton)
        
        def update_dropdown(*args) -> None:
            dropdown.clear_widgets()
            for button in screen.theme_buttons:
                if button.text != mainbutton.text:
                    dropdown.add_widget(button)
                else:
                    dropdown.remove_widget(button)
        
        mainbutton.bind(on_release=update_dropdown)

    def save_theme(self, theme: str):
        config.update('config', 'current_theme', theme.lower())
        
class MultiplierDropDown(BoxLayout):
    def __init__(self, screen: SettingsScreen, **kwargs):
        super(MultiplierDropDown, self).__init__(**kwargs)
        
        dropdown = DropDown()
        drop_multipliers = [1, 2, 3, 4, 5]
        
        self.size_hint = (None,None)

        screen.multiplier_buttons = []
        for i, multiplier in enumerate(drop_multipliers):
            btn = DropButton(
                text=str(multiplier),
                size_hint=(None,None),
                is_last=True if i+1 == len(drop_multipliers) else False,
                font_name=config.current_lang['font'],
                color=config.current_theme['font_color'], 
                font_size=sp(13)
            )
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            screen.multiplier_buttons.append(btn)
            
        mainbutton = Button(
            size_hint=(0.5, None),
            background_normal='textures/dropdown-arrow-gray.png',
            background_down='textures/dropdown-arrow-gray.png',
            background_color=(1,1,1,1)
        )
        
        def on_select(mainbutton: Button, multiplier: str) -> None:
            self.save_multiplier(int(multiplier))
            
            screen.selected_multiplier_label.text = multiplier
            
        mainbutton.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: on_select(mainbutton, x))
        
        self.add_widget(mainbutton)
        
        def update_dropdown(*args) -> None:
            dropdown.clear_widgets()
            for button in screen.multiplier_buttons:
                if button.text != mainbutton.text:
                    dropdown.add_widget(button)
                else:
                    dropdown.remove_widget(button)
        
        mainbutton.bind(on_release=update_dropdown)

    def save_multiplier(self, multiplier: int) -> None:
        config.update('config', 'multiplier', multiplier)

class DropDownButton(Button):
    pass

class SettingsBoxLayout(BoxLayout):
    instances = []
    def __init__(self, radius: List[int], **kwargs) -> None:
        super(SettingsBoxLayout, self).__init__(**kwargs)
        
        SettingsBoxLayout.instances.append(self)
        
        self.radius = radius
        
        with self.canvas.before:
            Color(*config.current_theme['stats_middleground_color'])
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=self.radius)
        
        self.bind(size=self._update_rect, pos=self._update_rect)
        
    def _update_rect(self, instance: "SettingsBoxLayout", value: ObservableReferenceList) -> None:
        self.rect.pos = self.pos
        self.rect.size = self.size
        
    @classmethod
    def update_rect_color(cls, theme: Dict[str, Union[str, int, Tuple[int]]]) -> None:
        for instance in cls.instances:
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*theme['stats_middleground_color'])
                instance.rect = RoundedRectangle(size=instance.size, pos=instance.pos, radius=instance.radius)
                
class DropButton(Button):
    is_last = ObjectProperty(False)
    bg_color = ObjectProperty((1,1,1,1))
    def __init__(self, is_last: bool, lang_font: bool = True, **kwargs) -> None:
        super(DropButton, self).__init__(**kwargs)
        self.is_last = is_last
        self.bg_color = config.current_theme['period_button_color']

class OptionSwitch(Button):
    active = ObjectProperty(False)
    switch_bg_color = ObjectProperty((0.8,0.8,0.8,1))
    switch_outline_color = ObjectProperty((0.9,0.9,0.9,1))
    def __init__(self, **kwargs) -> None:
        super(OptionSwitch, self).__init__(**kwargs)
        self.active = config.roman_numerals
        self.switch_bg_color = config.current_theme['switch_bg_color']
        self.switch_outline_color = config.current_theme['switch_outline_color']
        
    def on_click(self, instance: "OptionSwitch") -> None:
        self.active = not self.active
        config.update('config', 'roman_numerals', self.active)
class DeleteDataButton(AnchorLayout):
    def __init__(self, screen: SettingsScreen, **kwargs) -> None:
        super(DeleteDataButton, self).__init__(**kwargs)
        
        self.anchor_x='center'
        self.anchor_y='center'
        self.size_hint_y=None
        
        
        
        bl = SettingsBoxLayout(orientation='horizontal', width=Window.width-100, size_hint=(None,None), radius=[0,0,20,20])
        
        screen.delete_label = Button(
            text=config.current_lang['delete_data'],
            size_hint_x=None,
            width=get_text_width(config.current_lang['delete_data'])+dp(12),
            color=config.current_theme['font_color'],
            font_size=sp(16),
            font_name=config.current_lang['font'],
            background_normal='',
            background_down='',
            background_color=(0,0,0,0)
        )
        
        bl.add_widget(screen.delete_label)
        bl.add_widget(Widget(size_hint_x=1))
        
        screen.trash_img = KivyImage(source=config.current_theme['trash_can'], allow_stretch=False, keep_ratio=True, size_hint=(None,None), size=(dp(44),dp(44))) 
        
        screen.trash_img.bind(on_touch_down=self.on_image_touch)
        
        bl.add_widget(screen.trash_img)
        self.add_widget(bl)
    
    def on_image_touch(self, instance: KivyImage, touch: MouseMotionEvent) -> bool:
        if instance.collide_point(touch.x, touch.y):        
            DelPopup().show_confirmation_dialog()
        return False
        
class DelPopup(MDApp):
    _instance: Optional["DelPopup"] = None

    def __new__(cls, *args, **kwargs) -> "DelPopup":
        if not cls._instance:
            cls._instance = super(DelPopup, cls).__new__(cls)
        return cls._instance
        
    def __init__(self, **kwargs) -> None:
        super(DelPopup, self).__init__(**kwargs)
        
        self.data_store = None
        self.checkboxes_list = None
        self.dialog = None
        self.opened = False

    def show_confirmation_dialog(self) -> None:
        if self.opened:
            return
        self.opened = True
        
        self.data_store = CalendarStore()
        
        with self.data_store as store:
            calendars_list = store.get_calendars() 
    
        checkboxes_bl = BoxLayout(orientation='vertical', size_hint = (None,None), size = (Window.width*0.7,Window.height/30*len(calendars_list)+dp(50)+50))
        
        lbl = Label(
            text='Данные из выбранных календарей будут полностью удалены. \nОтменить это действие нельзя.' if config.current_lang['code'] == 'ru' 
                else 'Data from selected calendars will be permanently deleted.\nThis action cannot be undone.',
            size_hint=(None,None),
            size=(Window.width*0.7, dp(50)),
            color=(0,0,0,1),
            text_size=(Window.width*0.7, None)
        )
        checkboxes_bl.add_widget(lbl)
        
        checkboxes_bl.add_widget(Widget(size_hint_y=None, height=50))
        
        self.checkboxes_list = []

        for name in calendars_list:
            calendar_bl = BoxLayout(orientation='horizontal',size_hint=(1, None), height=Window.height/30)
            checkbox = MDCheckbox(size_hint_x=None, width=Window.width*0.127) 
            self.checkboxes_list.append((checkbox, name))
            calendar_bl.add_widget(checkbox)
            
            name_label = Label(text=name, color=(0,0,0,1), size_hint_x=None, width=Window.width*0.573, valign='center')
            name_label.bind(size=name_label.setter('text_size'))
            calendar_bl.add_widget(name_label)
                
            calendar_bl.add_widget(Widget())
            checkboxes_bl.add_widget(calendar_bl)
    
        self.dialog = MDDialog(
            title='Сбросить данные?' if config.current_lang['code'] == 'ru' else 'Delete Data?',
            buttons=[
                MDFlatButton(
                    text="Отмена" if config.current_lang['code'] == 'ru' else 'Cancel',
                    on_release=self.close_dialog
                ),
                MDFlatButton(
                    text="Удалить" if config.current_lang['code'] == 'ru' else "Delete",
                    on_release=self.confirm_delete
                ),
            ],
            type='custom',
            content_cls=checkboxes_bl,
            auto_dismiss = False,
            pos_hint={'y':0.596},
            md_bg_color=config.current_theme['popup_color'],
            overlay_color=config.current_theme['popup_overlay_color'],
        )
        
        
        self.dialog.open(animation=False)

    def close_dialog(self, *args) -> None:
        self.dialog.dismiss(force=True)
        self.opened = False

    def confirm_delete(self, *args) -> None:
        with self.data_store as store:
            calendars = len(store.get_calendars())
            for checkbox, calendar_name in self.checkboxes_list:
                if checkbox.active and calendars > 1:
                    store.delete_calendar(calendar_name)
                    calendars -= 1
                elif calendars == 1:
                    store.delete_calendar(calendar_name)
                    new_calendar_name = config.current_lang['new_calendar'] + ' 1'
                    
                    store.create_calendar(new_calendar_name)
            self.data_store.default_table = self.data_store.get_calendars()[0]
                
        self.dialog.dismiss()
         
Builder.load_string('''
<DropButton>:
    background_color: 0,0,0,0
    color: 0,0,0,1
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            size: self.size
            pos: (self.pos[0], self.pos[1]+10)
            radius: [0, 0, 20, 20] if self.is_last else [0, 0, 0, 0]
            
<OptionSwitch>
    size_hint: None, None
    size: 90, 50
    background_normal: ''
    background_down: ''
    background_color: 0,0,0,0
    on_release: self.on_click(self)
    canvas.before:
        Color:
            rgba: self.switch_bg_color
        RoundedRectangle:
            pos: (self.pos[0]-5, self.pos[1]+25)
            size: self.size
            radius: [25]
        Color:
            rgba: self.switch_outline_color
        Line:
            rounded_rectangle: self.x-6, self.y + 24, self.width+1, self.height+1, 25
            width: 2
        Color:
            rgba: 1,1,1,1
        Ellipse:
            pos: (self.pos[0]+(40 if self.active else 0), self.pos[1]+30)
            size: 40, 40
''')