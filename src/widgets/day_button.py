from kivy.uix.anchorlayout import AnchorLayout 
from kivy.uix.image import Image as KivyImage
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.animation import Animation
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp, sp

from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Union
from datetime import datetime
from utils import toRoman
import time

from calendar_store import CalendarStore
from app_config import Config

from .note_popup import NotePopup

config = Config()
checks_data_store = CalendarStore()

class DayButtonsLayout(GridLayout):
    def __init__(self, screen: Screen, *args, **kwargs) -> None:
        super(DayButtonsLayout, self).__init__(*args, **kwargs)
        
        self.screen = screen

    def initialize(self) -> None:
        DayButton.initialize(self, self.screen)

        for _ in range(7*6):
            self.add_widget(
                DayButton(
                    screen=self.screen,
                    size_hint=(None, None),
                    size=((Window.width-24)/7,(Window.height*0.7-21)/6)
                )
            )

class DayButton(Button):
    def __init__(
            self,
            screen: Screen,
            date: Optional[str] = None,
            day_num: int = 0,
            this_month: bool = False,
            **kwargs 
        ) -> None:
        """
        date - дата кнопки
        day_num - номер дня
        this_month - определяет это кнопка дней сегодняшнего месяца или нет
        """
        super(DayButton, self).__init__(on_press=self.start_anim, on_release=self.release, **kwargs)
        
        day_padding = dp(19)
        multiplier_padding = dp(7)
        today_circle_padding = dp(4)
            
        self.screen = screen

        # родительские свойства
        self.background_normal = ''
        self.background_down = ''
        self.background_color = config.current_theme['buttons_color']
        self.font_size = 31
        self.font_name = config.current_lang['font'] 
        
        # кастомные свойства
        self.bg_state = ''
        self.date = date
        self.day_num = day_num
        self.this_month = this_month
        self.multiplier_padding = multiplier_padding
        self.today_circle_padding = today_circle_padding
        
        self.multiplier = 0
        self.short_note = ''
        self.long_note = ''

        # для текстур
        self.check_image = None
        self.text_image = None
        self.text_label = None
        self.today_circle_layout = None
        self.today_circle_png = None

        # для анимаций
        self.hold = False
        self.start = None
        self.anim_in = None
        self.is_today_button = None
        self.clicked_btn = None
        self.can_click = None
        self.anim_out = None
        self.anim_complete = True
        self.can_press = True
            
        day_num_color = config.current_theme['font_color'] if self.this_month else config.current_theme['menu_buttons_font_color']
        
        self.layout = AnchorLayout(anchor_x='center', anchor_y='top', size_hint=(None,None), padding=(0,day_padding,0,0))
        self.label = Label(text=toRoman(self.day_num) if config.roman_numerals else str(self.day_num), size_hint=(None, None), height=-10, color=day_num_color, font_name=config.current_lang['font'], font_size=sp(13))
        self.layout.add_widget(self.label)
        self.add_widget(self.layout)
        
        self.multiplier_layout = AnchorLayout(anchor_x='right', anchor_y='bottom', size_hint=(None,None), padding=(dp(30),0,0,self.multiplier_padding))
        self.multiplier_label = Label(text='', size_hint=(None, None), height=0, font_name=config.current_lang['font'], font_size=sp(13))
        self.multiplier_layout.add_widget(self.multiplier_label)
        self.add_widget(self.multiplier_layout)
            
        Clock.schedule_once(self.set_layout_size)
        
    def set_layout_size(self, *args) -> None:
        self.layout.size = self.size
        self.layout.pos = self.pos
        if self.today_circle_layout:
            self.today_circle_layout.size = self.size
            self.today_circle_layout.pos = self.pos
        self.multiplier_layout.size = (self.size[0]*1.2, self.size[1])
        self.multiplier_layout.pos = self.pos

    def truncate_text(self, text: str) -> str:
        image = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(config.current_lang['font'], 30)
            
        truncated_text = ''
        current_width = 0
            
        for char in text:
            char_width = draw.textlength(char, font=font)
            if (current_width + char_width + draw.textlength('..', font=font)) > (Window.width/7-24) *0.8:
                truncated_text += '..'
                break
            truncated_text += char
            current_width += char_width
                
        return truncated_text
    
    def change_bg(self, bg_state: str) -> None:
        def set_check(no_text: bool = True) -> None:
            if not self.check_image and self.bg_state != 'check':
                btn_size = ((Window.width-24)/7,(Window.height*0.7-21)/6)
                self.check_image = KivyImage(source=config.current_theme['check_texture'] if self.this_month else config.current_theme['check_texture_tp'], size=(btn_size[0]*0.7,btn_size[1]*0.3))
                def set_check_pos(*args):
                    self.check_image.center_x = self.center_x
                    self.check_image.y = self.center_y - self.height/2.2
                Clock.schedule_once(set_check_pos)
            if not self.check_image in self.children:
                self.check_image.source = config.current_theme['check_texture'] if self.this_month else config.current_theme['check_texture_tp']
                self.add_widget(self.check_image)
                
        def set_text(no_check: bool = True) -> None:
            if no_check and self.check_image:
                self.remove_widget(self.check_image)
            
            if not self.text_image and self.bg_state != 'text': 
                self.text_image = KivyImage(source=config.current_theme['text_texture'] if self.this_month else config.current_theme['text_texture_tp'], size_hint=(None,None))
                def set_image_pos(*args):
                    self.text_image.width = self.width*0.8
                    self.text_image.center_x = self.center_x
                    self.text_image.y = self.center_y-self.height*0.17
                Clock.schedule_once(set_image_pos) 
            else:
                self.text_image.source = config.current_theme['text_texture'] if self.this_month else config.current_theme['text_texture_tp']
                
            if not self.text_label and self.bg_state != 'text':
                self.text_label = Label(text=self.truncate_text(self.short_note), size_hint=(None,None), color=self.color, font_size=self.font_size,font_name=self.font_name)
                def set_text_pos(*args):
                    self.text_label.center_x = self.center_x
                    self.text_label.y = self.center_y-self.height*0.17
                    self.text_label.size = self.text_image.size
                    self.text_label.center_y = self.text_image.center_y
                    self.text_label.center_x = self.center_x
                Clock.schedule_once(set_text_pos)
            else:
                self.text_label.text = self.truncate_text(self.short_note)
            
            if not self.text_image in self.children:
                self.add_widget(self.text_image)
            if not self.text_label in self.children:
                self.add_widget(self.text_label) 
                
        if bg_state == 'check':
            set_check()
            
        elif bg_state == 'text':
            set_text()
                
        elif bg_state == 'check_with_text':
            set_check(no_text=False)
            set_text(no_check=False)
            
        elif bg_state == '':
            if self.check_image:
                self.remove_widget(self.check_image)
            if self.text_image:
                self.remove_widget(self.text_image)
                self.remove_widget(self.text_label)
        self.bg_state = bg_state
        
    def update_button(self, new_day_num: int, new_this_month: int, new_date: str) -> None:
        self.background_color = config.current_theme['buttons_color']
        self.font_name = config.current_lang['font']
        
        self.day_num = new_day_num
        self.label.text = toRoman(self.day_num) if config.roman_numerals else str(self.day_num)
        self.label.font_name = self.font_name

        if self.text_label:
            self.text_label.color = self.color
            self.text_label.font_size = self.font_size
            self.text_label.font_name = self.font_name

            
        self.this_month = new_this_month
        
        day_num_color = config.current_theme['font_color'] if self.this_month else config.current_theme['menu_buttons_font_color']
        self.multiplier_label.color = config.current_theme['font_color'] if self.this_month else config.current_theme['menu_buttons_font_color']
        self.multiplier_label.font_name = config.current_lang['font']
        
        if self.this_month and config.opened_date[0] == datetime.now().year and config.opened_date[1] == datetime.now().month and config.opened_date[2] == self.day_num:
            day_num_color = config.current_theme['note_font_color']
            if not self.today_circle_layout:
                self.today_circle_layout = AnchorLayout(anchor_x='center', anchor_y='top', size_hint=(None,None), padding=(0,self.today_circle_padding,0,0))    
                self.today_circle_png = KivyImage(source=config.current_theme['today_circle_texture'], size_hint=(None,None), size=(dp(25), dp(25)))
                self.today_circle_layout.add_widget(self.today_circle_png)
                self.add_widget(self.today_circle_layout)
            elif self.today_circle_png:
                self.today_circle_png.source = config.current_theme['today_circle_texture']
                if not self.today_circle_png in self.today_circle_layout.children:
                    self.today_circle_layout.add_widget(self.today_circle_png)
                    
            self.remove_widget(self.layout)
            self.add_widget(self.layout)
        else:
            if self.today_circle_layout:
                self.today_circle_layout.remove_widget(self.today_circle_png)
                
        self.label.color = day_num_color
            
        self.date = new_date
        
        self.change_bg('')
        self.multiplier_label.text = ''
        
        with checks_data_store as store:
            check_data = store.get(new_date)
            
        if check_data:
            self.multiplier = check_data.multiplier
            self.short_note = check_data.short_note
            self.long_note = check_data.long_note
            if self.multiplier > 0:
                self.change_bg('check')
                if self.multiplier > 1:
                    self.multiplier_label.text = 'x' + toRoman(self.multiplier) if config.roman_numerals else 'x' + str(self.multiplier)
            else:
                self.change_bg('')
            if self.short_note:
                if self.bg_state == '':
                    self.change_bg('text')
                elif self.bg_state =='check':
                    self.change_bg('check_with_text')
            else:
                if self.bg_state == 'text':
                    self.change_bg('')
                elif self.bg_state == 'check_with_text':
                    self.change_bg('check')
        else:
            self.multiplier = 0
            self.short_note = ''
            self.long_note = '' 
            self.change_bg('')
        
    def switch_today_circle(self) -> None:
        """
        Switch today circle for animation(between normal and half-transparent texture)
        """
        if self.today_circle_layout:
            source = self.today_circle_layout.children[0].source
            if source == config.current_theme['today_circle_texture']:
                self.today_circle_layout.children[0].source = config.current_theme['today_circle_texture_tp']
            else:
                self.today_circle_layout.children[0].source = config.current_theme['today_circle_texture']
    
    def click(self) -> None:
        if self.bg_state in ('', 'text'):
            self.change_multiplier(1)
            if self.bg_state == '':
                self.change_bg('check')
            else:
                self.change_bg('check_with_text')
            self.update_check()
        else:
            if self.multiplier < config.multiplier:
                self.change_multiplier(self.multiplier+1)
                self.update_check()
            else:
                self.change_multiplier(0)
                if self.bg_state == 'check':
                    self.change_bg('')
                elif self.bg_state == 'check_with_text':
                    self.change_bg('text')
                self.update_check()
        
    def change_multiplier(self, new_multiplier: Union[str, int]) -> None:
        self.multiplier = int(new_multiplier)
        self.multiplier_label.text = f'x{new_multiplier}' if new_multiplier >= 2 else ''
    
    def create_check(self, short_note: str = '', long_note: str = '') -> None:
        with checks_data_store as store:
            if store.date_exists(self.date):
                store.update(self.date, multiplier=self.multiplier, short_note=short_note, long_note=long_note)
            else:
                store.put(self.date, self.multiplier, short_note, long_note)

    def update_check(self, short_note: str = '', long_note: str = '') -> None:
        self.create_check(short_note=short_note, long_note=long_note)
        if short_note != '':
            self.short_note = short_note
        if long_note != '':
            self.long_note = long_note
    
    def delete_check(self) -> None:
        with checks_data_store as store:
            store.delete(self.date)
    
    @staticmethod
    def initialize(layout: DayButtonsLayout, screen: Screen) -> None:
        btn = DayButton(screen)
        layout.add_widget(btn)
        layout.remove_widget(btn)

    # анимации
    def start_anim(self, instance: Button) -> None:
        self.clicked_btn = instance
        self.hold = True
        
        self.is_today_button = self.clicked_btn.this_month and config.opened_date[1] == datetime.now().month and config.opened_date[2] == self.clicked_btn.day_num
        if self.start and time.time() - self.start < 0.3 and not self.is_today_button:
            self.anim_in.stop(self.clicked_btn.label)
            self.anim_out = Animation(color=config.current_theme['font_color'], duration=0.5)
            self.anim_out.start(self.clicked_btn.label)
            
        self.start = time.time()
        self.can_click = True
        if self.can_press:
            self.can_press = False
            Clock.schedule_once(self.enable_button, 0.1)
        else:
            self.can_click = False
            return
        
        self.anim_complete = False
        
        if self.is_today_button:
            self.clicked_btn.switch_today_circle()
            Clock.schedule_once(self.on_anim_complete, 0.2)
            return
        
        self.clicked_btn.label.color = config.current_theme['anim_transition_font_color'] if self.clicked_btn.this_month else config.current_theme['anim_transition_note_font_color']
    
        self.anim_in = Animation(color=config.current_theme['animation_font_color'], duration=0.2)
        self.anim_in.bind(on_complete=self.on_anim_complete)
        self.anim_in.start(self.clicked_btn.label)
    
    def on_anim_complete(self, *args) -> None:
        if not self.hold:
            return
        self.anim_complete = True
        try:
            if self.hold and self.is_finger_on_button(self.clicked_btn):
                NotePopup().display_popup(self.clicked_btn)
            if not self.is_today_button:
                self.anim_in.stop(self.clicked_btn.label)
                self.anim_out = Animation(
                    color=config.current_theme['font_color'] if self.clicked_btn.this_month 
                        else config.current_theme['menu_buttons_font_color'], 
                    duration=0.5
                )
                self.anim_out.start(self.clicked_btn.label)
        except KeyError as e:
            pass
            
    def release(self, instance: Button) -> None:
        self.hold = False
        if self.is_today_button:
            self.clicked_btn.switch_today_circle()
            instance.click()
            return
        if self.anim_complete:
            return
        if not self.can_click:
            return
            
        if self.anim_out:
            self.anim_out.stop(self.clicked_btn.label)
            
        if self.anim_in:
            self.anim_in.stop(self.clicked_btn.label)
            
            self.anim_out = Animation(
                color=config.current_theme['note_font_color'] if self.is_today_button 
                    else config.current_theme['menu_buttons_font_color'] if not self.clicked_btn.this_month
                    else config.current_theme['font_color'], 
                duration=0.5
            )
            self.anim_out.start(self.clicked_btn.label)
        
        instance.click()

    def enable_button(self, *args) -> None:
        self.can_press = True
        
    def is_finger_on_button(self, button) -> bool:
        if self.screen.current_touch:
            return button.collide_point(self.screen.current_touch.x, self.screen.current_touch.y)
        return False 