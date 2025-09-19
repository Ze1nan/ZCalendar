from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField 

from datetime import datetime
from typing import Optional

from calendar_store import CalendarStore
from app_config import Config

config = Config()
checks_data_store = CalendarStore()

class NotePopup(MDApp):
    _instance: Optional["NotePopup"] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> "NotePopup":
        if not cls._instance:
            cls._instance = super(NotePopup, cls).__new__(cls)
        else:
            NotePopup._initialized = True
        return cls._instance
    
    def __init__(self, **kwargs) -> None:
        super(NotePopup, self).__init__(**kwargs)

        if NotePopup._initialized:
            return
        self.instance = None
        self.open_day = None
        self.short_textfield = None
        self.long_textfield = None
        self.add_note = None
        self.opened = False
        
    def display_popup(self, instance: Button) -> None:
        if self.opened:
            return
        self.opened = True

        self.instance = instance
        self.open_day = instance.day_num

        with checks_data_store as store:
            if not store.date_exists(instance.date):
                store.put(instance.date)
        
        self.theme_cls.font_styles['Custom'] = [config.current_lang['font'],24, True, 0.5]
        
        lang = config.get_language('en' if config.current_lang != 'ru' else 'ru')
        week_days = lang['full_weekdays']
        months = lang['months']
        
        short_field_bl = BoxLayout(orientation='horizontal', size_hint=(None,None), size=(Window.size[0]*0.75, 100))
        self.short_textfield = MDTextField(mode='line', hint_text='Short Note' if config.current_lang['code'] != 'ru' else 'Короткая заметка', max_text_length=25, text_color_focus=config.current_theme['font_color'], text_color_normal=config.current_theme['font_color'], line_color_normal=config.current_theme['popup_line_color_normal'], hint_text_color_normal=config.current_theme['popup_hint_text_color_normal'], line_color_focus=config.current_theme['popup_line_color_focus'], hint_text_color_focus=config.current_theme['popup_hint_text_color_focus'], font_name=config.current_lang['font'], size_hint_x=1) 
        short_field_bl.add_widget(self.short_textfield)
        icon = MDIconButton(icon="close-circle-outline", on_release=self.clear_text, size_hint_x=None) 
        short_field_bl.add_widget(icon)
        
        if instance.short_note:
            self.short_textfield.text = instance.short_note
            
        self.long_textfield = MDTextField(text = '', mode='rectangle', hint_text="     " + 'Note' if config.current_lang['code'] != 'ru' else 'Заметка', multiline=True, size_hint = (None,None), size = (Window.size[0]*0.7, 600), max_text_length=250, line_color_normal=config.current_theme['popup_line_color_normal'], hint_text_color_normal=config.current_theme['popup_hint_text_color_normal'], text_color_focus=config.current_theme['font_color'], text_color_normal=config.current_theme['font_color'], line_color_focus=config.current_theme['popup_line_color_focus'], hint_text_color_focus=config.current_theme['popup_hint_text_color_focus'], max_height=550, font_name=config.current_lang['font'], height=550)
        
        if instance.long_note:
            self.long_textfield.text = instance.long_note
                
        bl_field = BoxLayout(orientation = 'vertical', size_hint = (None,None), size = (Window.width*0.7,Window.height/3))

        bl_field.add_widget(short_field_bl)
        bl_field.add_widget(Widget())
        bl_field.add_widget(self.long_textfield)
        
        self.add_note = MDDialog(
            title=f'{week_days[datetime.weekday(datetime(config.opened_date[0], config.opened_date[1], self.open_day))]}, {self.open_day} {months[config.opened_date[1]-1]}',
            type="custom",
            buttons=[MDFlatButton(text='Закрыть' if config.current_lang == 'ru' else 'Close', on_release=self.close_popup)],
            content_cls=bl_field,
            auto_dismiss = False,
            pos_hint={'y':0.596},
            size_hint=(None, None),
            size = (Window.size[0]/1.2, Window.size[1]/25),
            md_bg_color=config.current_theme['popup_color'],
            overlay_color=config.current_theme['popup_overlay_color']
        )
        
        self.add_note.open(animation=False)
    
    def clear_text(self, instance: Button) -> None:
        self.short_textfield.text = ''
    
    def close_popup(self, instance: Button) -> None:
        self.instance.short_note = self.short_textfield.text.strip()
        self.instance.color = config.current_theme['note_font_color']
        
        if len(self.instance.short_note) > 0:
            if self.instance.bg_state == '':
                self.instance.change_bg('text')
            elif self.instance.bg_state == 'check':
                self.instance.change_bg('check_with_text')
            elif self.instance.bg_state == 'text':
                self.instance.change_bg('text')
            elif self.instance.bg_state == 'check_with_text':
                self.instance.change_bg('check_with_text')
        else:
            if self.instance.bg_state == 'text':
                self.instance.change_bg('')
            elif self.instance.bg_state == 'check_with_text':
                self.instance.change_bg('check')
        
        if self.short_textfield.text and not self.instance.short_note.isspace():
            self.instance.update_check(short_note=self.short_textfield.text.strip())
        else:
            self.instance.update_check(short_note=self.short_textfield.text.strip())
            
        if self.long_textfield.text and not self.long_textfield.text.isspace():
            self.instance.update_check(long_note=self.long_textfield.text.strip())
        else:
            self.instance.update_check(long_note='')
        
        for easter, keywords in config.get_easters().items():
            if self.short_textfield.text.strip().lower() in keywords:
                config.update('easters', easter, True)
                
        self.instance.update_check(short_note=self.short_textfield.text.strip())
        
        self.add_note.dismiss()

        self.opened = False