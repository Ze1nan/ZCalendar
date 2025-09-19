from kivy.input.providers.mouse import MouseMotionEvent
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
    
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.metrics import sp

from typing import Optional, Tuple
from calendar import monthrange
from datetime import datetime
from utils import toRoman

from calendar_store import CalendarStore
from app_config import Config

from widgets import (
    DayButtonsLayout,
    SelectCalendarLayout,
    CalendarButton,
    SelectDateApp,
    ScreenWidget,
    GirlImage,
)

is_clamped = True
stop_hold = False

config = Config()
checks_data_store = CalendarStore()

class CalendarScreen(Screen):
    _instance: Optional["CalendarScreen"] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> "CalendarScreen":
        if not cls._instance:
            cls._instance = super(CalendarScreen, cls).__new__(cls)
        else:
            CalendarScreen._initialized = True
        return cls._instance
    
    def __init__(self, calendar_name: Optional[str] = None, **kwargs) -> None:
        super(CalendarScreen, self).__init__(**kwargs)

        update_theme = self.__getattribute__('current_theme')['name'] != config.current_theme['name'] if hasattr(self, 'current_theme') else False
        update_lang = self.__getattribute__('current_lang')['code'] != config.current_lang['code'] if hasattr(self, 'current_lang') else False
        
        self.current_lang = config.current_lang
        self.current_theme = config.current_theme
        self.roman_numerals = config.roman_numerals

        with checks_data_store as store:
            if not store.get_calendars():
                checks_data_store.create_calendar('Calendar')
                self.calendar_name = 'Calendar'
            else:
                self.calendar_name = calendar_name if calendar_name else checks_data_store.get_calendars()[0]
            checks_data_store.select_calendar(self.calendar_name)
        
        if not CalendarScreen._initialized:
            self.bg_rect_color = None
            self.head_bl = None
            self.month_label = None
            self.weekdays_labels = None
            self.menu_buttons = None
            self.menu_buttons_btns = None
            self.calendar_layout_bl = None
            self.girl_png = None
            self.days = None

        if CalendarScreen._initialized:
            if update_theme:
                self.bg_rect_color.r, self.bg_rect_color.g, self.bg_rect_color.b, self.bg_rect_color.a = config.current_theme['background_color']
                self.head_bl.rect_color.r, self.head_bl.rect_color.g, self.head_bl.rect_color.b, self.head_bl.rect_color.a = config.current_theme['buttons_color']
                
                self.month_label.color = config.current_theme['font_color']
                
                for label in self.weekdays_labels:
                    label.color = config.current_theme['font_color']
                
                for button in self.menu_buttons.children:
                    button.color = config.current_theme['menu_buttons_font_color']
                    button.background_color = config.current_theme['menu_buttons_color']
                    button.font_name = config.current_lang['font']
                
                for button in self.calendar_layout_bl.layout.children:
                    if isinstance(button, CalendarButton):
                        button.name_label.color = config.current_theme['font_color']
                        if button.on_focus:
                            button.update_color()
                
                self.girl_png.update()
                
            if update_lang:
                for label, text in zip(self.weekdays_labels, config.current_lang['short_weekdays']):
                    label.text = text
                    label.font_name = config.current_lang['font']
                for label, text in zip(self.menu_buttons_btns, config.current_lang['menu_buttons']):
                    label.font_name = config.current_lang['font'] 

                for button in self.calendar_layout_bl.layout.children:
                    if isinstance(button, CalendarButton):
                        button.name_label.font_name = config.current_lang['font']
            
            self.calendar_layout_bl.select_calendar = self.calendar_name
            self.calendar_layout_bl.update()
            self.open_calendar_date(*config.opened_date[:2], today=True)
            return
        
        self.size = Window.size
        
        self.current_touch = None
        self.touch_start = (0, 0)
        
        with self.canvas:
            self.bg_rect_color = Color(*config.current_theme['background_color'])
            Rectangle(size=self.size, pos=self.pos)
        
        self.calendar_layout_bl = SelectCalendarLayout(self.calendar_name, self, size_hint=(1, None), height=Window.height * 0.05) 
        
        # основной лайаут
        self.layout = BoxLayout(orientation='vertical', size_hint=(1, 1))
        self.add_widget(self.layout)  
            
        self.months = config.current_lang['months'] 
        
        self.month_label = Label(
            text='',
            halign='left',
            valign='bottom',
            color=config.current_theme['font_color'],
            size_hint=(1.0, None),
            height=Window.height * 0.03,
            font_name=config.current_lang['font'],
            font_size=sp(18)
        )  
        self.month_label.bind(on_touch_down=self.open_change_date)
        self.month_label.bind(size=self.month_label.setter('text_size'))
        
        # лайаут с подписью дней недели
        weekdays = config.current_lang['short_weekdays']
        self.weekdays_bl = BoxLayout(orientation='horizontal', size_hint=(1, None), height=Window.height * 0.05)
        self.weekdays_labels = []
        # генерация подписей(лейблов) дней недели
        for day in weekdays:
            weekday_label = Label(text=day, color=config.current_theme['font_color'], font_name=config.current_lang['font'], font_size=sp(17))
            self.weekdays_labels.append(weekday_label)
            self.weekdays_bl.add_widget(weekday_label) 
            
        self.head_bl = HeadBoxLayout(orientation='vertical', size_hint=(1, None), height=Window.height * 0.15)
        self.head_bl.add_widget(Widget(size_hint=(None, None), height=Window.height * 0.07))
        self.head_bl.add_widget(self.month_label)
        self.head_bl.add_widget(self.weekdays_bl)
        
        # лайаут кнопок дней
        self.days = DayButtonsLayout(self, rows=6, cols=7, size_hint=(1, 0.93), spacing=3, padding=(0, 3, 0, 3), size=(Window.width - 24, Window.height * 0.7))
        self.days.initialize()
        
        # лайаут кнопок внизу экрана
        self.menu_buttons = BoxLayout(orientation='horizontal', size_hint=(1,None), height=Window.height*0.06)
        self.menu_buttons_btns = []

        calendar_button = Button(
            text=config.current_lang['menu_buttons'][0],
            color=config.current_theme['menu_buttons_font_color'],
            font_size = sp(13),
            background_color= config.current_theme['menu_buttons_color'],
            background_normal='',
            background_down='',
            font_name=config.current_lang['font']
        )
        self.menu_buttons.add_widget(calendar_button)
        self.menu_buttons_btns.append(calendar_button)
        
        statistics_button = Button(
            text=config.current_lang['menu_buttons'][1],
            color= config.current_theme['menu_buttons_font_color'],
            font_size = sp(13),
            background_color= config.current_theme['menu_buttons_color'], 
            background_normal='',
            background_down='',
            font_name=config.current_lang['font'],
            on_release=self.open_statistics
        )
        self.menu_buttons.add_widget(statistics_button)
        self.menu_buttons_btns.append(statistics_button)
        
        usage_button = Button(
            text=config.current_lang['menu_buttons'][2],
            color= config.current_theme['menu_buttons_font_color'],
            font_size = sp(13),
            background_color= config.current_theme['menu_buttons_color'], 
            background_normal='',
            background_down='',
            font_name=config.current_lang['font'],
            on_release=self.open_usage
        )
        self.menu_buttons.add_widget(usage_button)
        self.menu_buttons_btns.append(usage_button)
        
        settings_button = Button(
            text=config.current_lang['menu_buttons'][3],
            color= config.current_theme['menu_buttons_font_color'],
            font_size = sp(13),
            background_color= config.current_theme['menu_buttons_color'], 
            background_normal='',
            background_down='',
            font_name=config.current_lang['font'],
            on_release=self.open_settings
        )
        self.menu_buttons.add_widget(settings_button)
        self.menu_buttons_btns.append(settings_button)
        
        self.girl_png = GirlImage()
        
        # сборка лайаута
        self.layout.add_widget(Widget(size_hint=(None, None), height=Window.height * 0.04))
                
        self.layout.add_widget(self.calendar_layout_bl)
                
        self.layout.add_widget(self.head_bl)
                
        self.layout.add_widget(self.days)
                
        self.layout.add_widget(self.menu_buttons) 
        
        self.open_calendar_date(*config.opened_date[:2], today=True)

    def open_statistics(self, instance: Button) -> None:
        ScreenWidget().change_screen('statistics', calendar_name=checks_data_store.default_table)
    def open_settings(self, instance: Button) -> None:
        ScreenWidget().change_screen('settings', calendar_name=checks_data_store.default_table)
    def open_usage(self, instance: Button) -> None:
        ScreenWidget().change_screen('usage', calendar_name=self.calendar_name)
        
    def get_month_data(self, year: int, month: int) -> Tuple[int]:
        first_weekday, month_days = monthrange(int(year), int(month))
        return (first_weekday+1, month_days)
        
    def on_touch_down(self, touch: MouseMotionEvent) -> bool:
        self.current_touch = touch
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch: MouseMotionEvent) -> bool:
        global is_clamped
        if is_clamped is True:
            self.touch_start = (touch.x, touch.y)
            is_clamped = False 
        self.current_touch = touch 
        return super().on_touch_move(touch)
        
    # обработка свайпа после отпуска пальца
    def on_touch_up(self, touch: MouseMotionEvent) -> None:
        global is_clamped
        
        # если свайп вправо больше 200 пикселей, то:
        if (
            self.touch_start[0] != 0 and
            touch.y > Window.height*0.06 and
            touch.y < Window.height*0.76 and
            self.touch_start[1] > Window.height*0.06 and
            self.touch_start[1] < Window.height*0.76
        ):
            is_clamped = True
            year, month, day = config.opened_date
            # свайп вправо
            if self.touch_start[0] - touch.x > 200:
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1
                self.open_calendar_date(year, month)
                
            # свайп влево
            if touch.x - self.touch_start[0] > 200:
                if month == 1:
                    month = 12
                    year -= 1
                else:
                    month -= 1
                        
            self.open_calendar_date(year, month)
            self.touch_start = (0,0)

        else:
            self.touch_start = (0,0)
            is_clamped = True
    
    def _setup_month_label(self, year: int, month: int) -> None:
        self.months = config.current_lang['months']
        month_label_text = f'{self.months[int(month) - 1]} {toRoman(year) if config.roman_numerals else year}' + (' г.' if config.current_lang['code'] == 'ru' else '')
                
        self.month_label.text = month_label_text
        self.month_label.font_name = config.current_lang['font']

    def open_calendar_date(self, year: int, month: int, today: bool = False) -> None:
        if today or (config.opened_date[0], config.opened_date[1]) != (year, month):
            config.opened_date[0], config.opened_date[1] = (year, month)
            
            self._setup_month_label(year, month)
            
            days_layout = list(reversed(self.days.children))
            
            # Создание и добавление кнопок дней
            _, previous_month_days = self.get_month_data(year-1 if month == 1 else year, month-1 if month != 1 else 12)
            
            first_weekday, month_days = self.get_month_data(year, month) 
            
            if first_weekday == 7:
                first_weekday = 0
            
            for i, btn in enumerate(days_layout[:first_weekday]):
                btn.update_button(
                    new_day_num=previous_month_days-first_weekday+i+1,
                    new_this_month=False,
                    new_date=f'{previous_month_days-first_weekday+i+1}-{"12" if int(month) - 1 == 0 else int(month) - 1}-{int(year)-1 if int(month)-1 == 0 else year}'
                )
            
            for i, btn in enumerate(days_layout[first_weekday:month_days+first_weekday], start=1):
                btn.update_button(new_day_num=i, new_this_month=True, new_date=f'{i}-{month}-{year}')
                
            for i, btn in enumerate(days_layout[month_days+first_weekday:len(days_layout)+1]):
                btn.update_button(new_day_num=i+1, new_this_month=False, new_date=f'{i+1}-{month+1 if month != 12 else 1}-{year if month != 12 else year+1}')
        
            if self.girl_png in self.children:
                self.remove_widget(self.girl_png)
            if config.current_girl:
                self.add_widget(self.girl_png)
            
    def open_change_date(self, label: Label, touch: MouseMotionEvent):
        if label.collide_point(touch.x, touch.y):
            popup = SelectDateApp(app=self)
            popup.opened_date_picker()
        
    @classmethod
    def change_calendar(cls, name: str):
        config.opened_date = list(map(int, f'{datetime.now():%Y-%m-%d}'.split('-')))
        checks_data_store.select_calendar(name)
        cls._instance.calendar_name = name
        cls._instance.open_calendar_date(*config.opened_date[:2], today=True)
    
class HeadBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(HeadBoxLayout, self).__init__(**kwargs)
        with self.canvas.before:
            self.rect_color = Color(*config.current_theme['buttons_color'])
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size 