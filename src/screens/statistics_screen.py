from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.dropdown import DropDown
from kivy.uix.widget import Widget
from kivy.uix.label import Label

from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.lang import Builder
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from datetime import datetime, timedelta
from matplotlib import font_manager
from collections import defaultdict
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from typing import Optional, Dict
from utils import toRoman

from app_config import Config
from calendar_store import CalendarStore
from widgets import ScreenWidget, GirlImage

config = Config()
checks_data_store = CalendarStore()

class StatisticsScreen(Screen):
    _instance: Optional["StatisticsScreen"] = None
    
    def __new__(cls, *args, **kwargs) -> "StatisticsScreen":
        if not cls._instance:
            cls._instance = super(StatisticsScreen, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, calendar_name: str, graph_period: Optional[str] = None, **kwargs) -> None:
        super(StatisticsScreen, self).__init__(**kwargs)
        
        self.calendar_name = calendar_name
        
        with checks_data_store as store:
            store.select_calendar(self.calendar_name)
        
        if not graph_period:
            graph_period = config.current_lang['periods'][1] 
        
        Window.clearcolor = config.current_theme['background_color']
                     
        notes = self.get_notes(graph_period=graph_period)
            
        today_date = datetime.today().strftime('%m-%Y').strip('0')
            
        months = config.current_lang['months']
            
        if graph_period == config.current_lang['periods'][3]:
            graph_labels = [f"{months[int(date.split('-')[1])-1]}, {int(date.split('-')[0])} - {months[(datetime.strptime(date, '%d-%m-%Y') + timedelta(days=6)).month - 1]}, {(datetime.strptime(date, '%d-%m-%Y') + timedelta(days=6)).day}" for date in sorted(notes.keys(), key=lambda x: datetime.strptime(x, '%d-%m-%Y'))]
            graph_checks = [notes[key] for key in sorted(notes.keys(), key=lambda x: datetime.strptime(x, '%d-%m-%Y'))]
        else:
            graph_checks = list(dict(sorted(notes.items(), key=lambda x: tuple(map(int, x[0].split('-')[::-1])))).values())
                
            month_now = int(today_date.split('-')[0])

            graph_labels = [months[(month_now + i-1) % 12] for i in range(-len(graph_checks) + 1, 1)]
            
        fig, ax = plt.subplots(facecolor=config.current_theme['stats_middleground_color'])
        
        ax.set_facecolor(config.current_theme['graph_color'])
        
        for i, check in enumerate(graph_checks):
            if check != 0:
                c = 0.05 + 0.02*(max(graph_checks)-1) if max(graph_checks) < 8 else 0.14 + 0.01*(max(graph_checks)-1) if max(graph_checks) < 20 else 0.24 + 0.02*(max(graph_checks)-20)
                
                if i == len(graph_checks)-1:
                    if graph_period == config.current_lang['periods'][3]:
                        c = c+0.02 if graph_checks[i-1] <= check else -(c)  - (0.2*(max(graph_checks)-1)) 
                    else:
                        c = c+0.02 if graph_checks[i-1] <= check else -(c)  - (0.03*(max(graph_checks)-1)) 
                elif i == 0:
                    if graph_period == config.current_lang['periods'][3]:
                        c = c+0.02 if graph_checks[i+1] <= check else -(c)  - (0.2*(max(graph_checks)-1)) 
                    else:
                        c = c+0.02 if graph_checks[i+1] <= check else -(c)  - (0.03*(max(graph_checks)-1)) 
                else:
                    c = c+0.02 if (graph_checks[i-1] < check) or (graph_checks[i-1] == check and graph_checks[i+1] <= check) or (graph_checks[i-1] > check and graph_checks[i+1] < check) else -(c) - (0.03*(max(graph_checks)-1)) 
                    
                ax.text(i, check + c , f'{toRoman(check) if config.roman_numerals else check}', ha='center', va='bottom', color=config.current_theme['graph_font_color'], fontsize=10)
        ax.plot(graph_checks, linewidth=4, color=config.current_theme['graph_line_color'])
        
        for i, check in enumerate(graph_checks):
            if check != 0:
                ax.scatter(i, check, color=config.current_theme['graph_line_color'], marker='o', edgecolors='black', facecolors='white', s=80, zorder=3, linewidths=2)

        ax.grid(True, color=config.current_theme['graph_grid_color']) 
        
        font_prop = font_manager.FontProperties(fname=config.current_lang['font'])
        
        # подписи с месяцами
        labels_step = (len(graph_checks) // 14) + 1
        ax.set_xticks(range(0, len(graph_checks), labels_step))
        ax.set_xticklabels(graph_labels[::labels_step], fontproperties=font_prop, fontsize=sp(4), color=config.current_theme['font_color'])
        
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
        
        ax.tick_params(axis='x', which='minor', length=4, color='gray')  
    
        if graph_period != config.current_lang['periods'][3]:
            graph_year = max([int(date.split('-')[-1]) for date in notes])
            for index in reversed([index for index, value in enumerate(graph_labels) if value == config.current_lang['months'][0]]):
                ax.text(index, -0.0504*max(notes.values())+0.0108, str(toRoman(graph_year) if config.roman_numerals else graph_year), color=(0.5,0,0,1), ha='center', va='bottom', fontsize=10, transform=ax.transData)
                graph_year -= 1

        # Установка делений по оси Y
        if graph_period == config.current_lang['periods'][3]:
            ax.set_yticks(range(0, 8))
            y_labels = [toRoman(i) for i in range(0, 8)] if config.roman_numerals else range(0, 8)
            ax.set_yticklabels(y_labels, fontproperties=font_prop, fontsize=sp(4), color=config.current_theme['font_color'])
        else:
            max_check = max(graph_checks)
            ax.set_yticks(range(0, max_check + 1, 1 if max_check < 20 else 2))
            y_labels = range(0, max_check + 1, 1 if max_check < 20 else 2)
            ax.set_yticklabels(y_labels, fontproperties=font_prop, fontsize=sp(4), color=config.current_theme['font_color'])
 
        
        if graph_period == config.current_lang['periods'][3]:
            ax.set_yticks(range(0,8))
            y_labels = [toRoman(i) for i in range(0, 8)] if config.roman_numerals else range(0, 8)
            ax.set_yticklabels(y_labels, fontproperties=font_prop, fontsize=sp(4), color=config.current_theme['font_color'])
        else:
            max_check = max(graph_checks)
            ax.set_yticks(range(0, max_check + 1, 1 if max_check < 20 else 2))
            y_labels = range(0, max_check + 1, 1 if max_check < 20 else 2)
            ax.set_yticklabels([toRoman(i) for i in y_labels] if config.roman_numerals else y_labels, fontproperties=font_prop, fontsize=sp(4), color=config.current_theme['font_color'])

        # поля с статистикой
        gl = CustomGridLayout(cols=1, padding=50, spacing=30, size_hint=(1, 0), height=Window.height*0.47)
        
        with checks_data_store as store:
            saved_checks = store.get_data(self.calendar_name)
        
        first_layout = BoxLayout(orientation='horizontal', spacing=30, size_hint_y=0.475)
        
        first_layout.add_widget(InfoField(title=config.current_lang['total'], value=sum([check.multiplier for check in saved_checks]), title_halign='center'))
        
        this_year_checks = sum([check.multiplier for check in saved_checks if check.date.split('-')[-1] == today_date.split('-')[-1]]) 
        first_layout.add_widget(InfoField(title=config.current_lang['this_year'], value=this_year_checks, title_halign='left'))
        
        this_month_checks = [check.multiplier for check in saved_checks if check.date.split('-')[1:] == today_date.split('-')]
        first_layout.add_widget(InfoField(title=config.current_lang['this_month'], value=sum(this_month_checks), title_halign='left'))
        
        second_layout = BoxLayout(orientation='horizontal', spacing=30)
        
        inner_layout = BoxLayout(orientation='vertical', spacing=30, size_hint_x=0.475)
        
        _month, year = map(int,today_date.split('-'))
        last_month_checks = sum([check.multiplier for check in saved_checks if check.date.split('-')[1:] == f"{12 if (_month - 1) == 0 else _month - 1}-{year - 1 if (_month - 1) == 0 else year}".split('-')])
        inner_layout.add_widget(InfoField(title=config.current_lang['last_month'], value=last_month_checks))
        
        monthly_sums = defaultdict(int)
        for check in saved_checks:
            if check.multiplier == 0:
                continue
            date_obj = datetime.strptime(check.date, '%d-%m-%Y')
            year_month = (date_obj.year, date_obj.month)
            monthly_sums[year_month] += check.multiplier
        
        monthly_sums = list(monthly_sums.values())
        
        average = round(sum(monthly_sums) / len(monthly_sums), 1) if monthly_sums else 0
        average = int(average) if int(average) == average else average
        inner_layout.add_widget(InfoField(title=config.current_lang['month_average'], value=average))
        
        second_layout.add_widget(inner_layout)
        
        def get_strike(n: int) -> float:
            sequence = []
            for i in range(1, n+1):
                value = 0.2 * i + 0.2 * (sequence[-1] if i != 1 else 0)
                sequence.clear()
                sequence.append(value)
            return sequence[0]
        
        def get_omission(n: int) -> float:
            sequence = []
            for i in range(1, n+1):
                value = 0.05 * n + 0.05*i + 0.2 * (sequence[-1] if i != 1 else 0)
                sequence.clear()
                sequence.append(value)
            return sequence[0]
        
        def calculate(sequence: list) -> float:
            result = 0
            for seq in sequence:
                if seq > 0:
                    result += get_strike(seq)
                elif seq < 0:
                    result -= get_omission(abs(seq))
            return result
        
        saved_checks_dates = sorted([check.date for check in saved_checks],key=lambda date: datetime.strptime(date, "%d-%m-%Y"))

        month_dates = [(datetime.now().replace(day=1) + timedelta(days=i)).strftime('%d-%m-%Y').strip('0').replace('-0','-') 
                       for i in range((datetime.now()+timedelta(days=1) - datetime.now().replace(day=1)).days + 1)]
        
        strikes = []
        strike_flag = None
        for date in month_dates:
            if date in saved_checks_dates:
                multiplier = [check.multiplier for check in saved_checks if check.date == date][0]
                if strike_flag is True:
                    strikes[-1] += int(multiplier)
                else:
                    strikes.append(int(multiplier))
                strike_flag = True
            else:
                if strike_flag is False:
                    strikes[-1] -= 1
                else:
                    strikes.append(-1)
                strike_flag = False
                    
        efficiency = round(calculate(strikes), 1)
        efficiency = int(efficiency) if int(efficiency) == efficiency else efficiency
        second_layout.add_widget(InfoField(title=config.current_lang['month_efficiency'], value=efficiency, title_halign='center', title_sp=27, value_sp=35))
        
        gl.add_widget(first_layout)
        gl.add_widget(second_layout)
        
        # лайаут кнопок внизу экрана
        self.menu_buttons = BoxLayout(orientation='horizontal', size_hint=(1, None), height=Window.height*0.06)
        self.menu_buttons.add_widget(
            Button(
                text=config.current_lang['menu_buttons'][0],
                color= config.current_theme['menu_buttons_font_color'],
                font_size = sp(13),
                background_color=
                config.current_theme['menu_buttons_color'], 
                background_normal='' ,
                background_down='',
                font_name=config.current_lang['font'],
                on_release=self.open_calendar
            )
        )
        
        self.menu_buttons .add_widget(
            Button(
                text=config.current_lang['menu_buttons'][1],
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
                text=config.current_lang['menu_buttons'][2],
                color= config.current_theme['menu_buttons_font_color'],
                font_size = sp(13),
                background_color= config.current_theme['menu_buttons_color'],
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
                font_size = sp(13),
                background_color= config.current_theme['menu_buttons_color'],
                background_normal='',
                background_down='',
                font_name=config.current_lang['font'],
                on_release=self.open_settings
            )
        )
        
        layout = BoxLayout(orientation='vertical', size=Window.size)
        layout.add_widget(Widget(size_hint=(1,0), height=Window.height*0.04))
        layout.add_widget(PeriodDropDown(graph_period=graph_period))
        layout.add_widget(FigureCanvasKivyAgg(fig, size_hint=(1, None), size=(0, dp(300))))
        layout.add_widget(gl)
        layout.add_widget(self.menu_buttons)

        self.add_widget(layout) 
        
        self.girl_png = GirlImage()

        if config.current_girl:
            self.add_widget(self.girl_png) 
    
    def get_notes(self, graph_period: str) -> Dict[str, int]:
        with checks_data_store as store:
            saved_checks = store.get_data()
        
        if graph_period == config.current_lang['periods'][0]:
            date_objects = [datetime.strptime(check.date, "%d-%m-%Y") for check in saved_checks]
                
            min_date = min(date_objects) 
            max_date = max(date_objects)
                
            graph_period = (max_date.year - min_date.year) * 12 + (max_date.month - min_date.month) + 1
            if graph_period < 6:
                graph_period = 6
        elif graph_period == config.current_lang['periods'][1]:
            graph_period = 12
        elif graph_period == config.current_lang['periods'][2]:
            graph_period = 6
            
        notes = {}
            
        today_date = datetime.today().strftime('%m-%Y').strip('0')
            
        if graph_period != config.current_lang['periods'][3]:
            for check in saved_checks:
                if datetime.strptime('-'.join(check.date.split('-')[1:]), '%m-%Y') > datetime.strptime(today_date,'%m-%Y'):
                    continue
                check_month = '-'.join(check.date.split('-')[1:])
                date1 = datetime.strptime(check_month, '%m-%Y')
                date2 = datetime.strptime(today_date, '%m-%Y')
                months_diff = (date1.year - date2.year) * 12 + date1.month - date2.month
                
                if abs(months_diff) < graph_period:
                    notes[check_month] = notes.get(check_month, 0) + check.multiplier
               
            check_month, check_year = map(int, today_date.split('-'))
                
            for i in range(1, graph_period+1):
                if f'{check_month}-{check_year}' not in notes:
                    notes[f'{check_month}-{check_year}'] = 0
            
                check_month = 12 if check_month == 1 else check_month - 1
                if check_month == 12:
                    check_year -= 1 
        else:
            saved_checks = sorted((date for date in saved_checks if datetime.now() - timedelta(days=28)<= datetime.strptime(date.date, "%d-%m-%Y") <= datetime.now()), key=lambda x: datetime.strptime(x.date, '%d-%m-%Y'))
            
            week_num = 1
            for check in saved_checks:
                start_week_date = datetime.now() - timedelta(days=7*(5-week_num)-1)
                
                end_week_date = start_week_date + timedelta(days=6)
                
                note_date  = start_week_date.strftime('%d-%m-%Y').strip('0')
                
                if start_week_date < datetime.strptime(check.date, '%d-%m-%Y') <= end_week_date:
                    notes[note_date] = notes.get(note_date, 0) + check.multiplier
                else:
                    week_num += 1
                    note_date = (datetime.now() - timedelta(days=7*(5-week_num)-1)).strftime('%d-%m-%Y').strip('0')
                    notes[note_date] = notes.get(note_date, 0) + check.multiplier
                
        return notes 
        
    def open_calendar(self, instance: Button) -> None:
        ScreenWidget().change_screen('calendar', calendar_name=self.calendar_name) 
    def open_settings(self, instance: Button) -> None:
        ScreenWidget().change_screen('settings', calendar_name=self.calendar_name)
    def open_usage(self, instance: Button) -> None:
        ScreenWidget().change_screen('usage', calendar_name=self.calendar_name)

class PeriodDropDown(BoxLayout):
    def __init__(self, graph_period: str, **kwargs) -> None:
        super(PeriodDropDown, self).__init__(**kwargs)
        dropdown = DropDown()
        periods =config.current_lang['periods']
                
        self.size_hint=(0.5,0)
                
        buttons = []
        for i, period in enumerate(periods):
            btn = PeriodButton(text=period, size_hint=(1,None), is_last=True if i+1 == len(periods) else False)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            buttons.append(btn)
        
        mainbutton = DropDownButton(text=graph_period, size_hint=(0.5, None), height=Window.height * 0.05)
                
        def on_select(mainbutton, period):
            setattr(mainbutton, 'text', period)
            ScreenWidget().update_statistics(calendar_name=checks_data_store.default_table, period=period)

                
        mainbutton.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: on_select(mainbutton, x))
                
        self.add_widget(mainbutton)
                
        def update_dropdown(*args):
            dropdown.clear_widgets()
            for button in buttons:
                if button.text != mainbutton.text:
                    dropdown.add_widget(button)
                else:
                    dropdown.remove_widget(button)

        mainbutton.bind(on_release=update_dropdown)


class DropDownButton(Button):
    bg_color = ObjectProperty((1,1,1,1))
    def __init__(self, **kwargs) -> None:
        super(DropDownButton, self).__init__(**kwargs)
        self.font_name = config.current_lang['font']
        
        self.bg_color = config.current_theme['stats_middleground_color']
        
        self.color = config.current_theme['font_color']

class PeriodButton(Button):
    is_last = ObjectProperty(False)
    bg_color = ObjectProperty((1,1,1,1))
    def __init__(self, is_last: bool, **kwargs) -> None:
        super(PeriodButton, self).__init__(**kwargs) 
        self.is_last = is_last
        self.font_name = config.current_lang['font']
        self.bg_color = config.current_theme['period_button_color']
        self.color = config.current_theme['period_button_font_color']
    

class InfoField(ButtonBehavior, BoxLayout):
    stats_info_background_color = ObjectProperty((0.973,0.973,0.973,1))
    stats_info_outline_color = ObjectProperty((0.9,0.9,0.9,1))
    value_sp = ObjectProperty(0)
    title_sp = ObjectProperty(0)
    title_halign = ObjectProperty('center')
    def __init__(
        self,
        title: str,
        value: int,
        title_sp: int = 19, 
        value_sp: int = 25, 
        title_halign: str = 'center',
        **kwargs,
    ) -> None:
        super(InfoField, self).__init__(**kwargs)
        value = str(toRoman(int(value)) if config.roman_numerals else value) + ('\n' if title==config.current_lang['month_efficiency'] else '')
        title = title + ':'
        
        self.ids.title_label.text = '   ' + title
        self.ids.value_label.text = str(value) + '\n'
        
        self.stats_info_background_color = config.current_theme['stats_info_background_color']
        self.stats_info_outline_color = config.current_theme['stats_info_outline_color']
        self.value_sp = sp(value_sp)
        self.title_halign = title_halign
        self.title_sp = sp(title_sp)

class CustomGridLayout(GridLayout):
    background_color = ObjectProperty((1,1,1,1))
    bg_line_color = ObjectProperty((0.8,0.8,0.8,1))
    def __init__(self, **kwargs) -> None:
        super(CustomGridLayout, self).__init__(**kwargs)
        
        self.background_color = config.current_theme['stats_middleground_color']
        self.bg_line_color = config.current_theme['background_color']
        
class InfoLabel(Label):
    color = ObjectProperty((1,1,1,1))
    def __init__(self, **kwargs) -> None:
        super(InfoLabel, self).__init__(**kwargs)
        self.font_name = config.current_lang['font'] 
        
        self.color = config.current_theme['font_color']
        
Builder.load_string('''
<DropDownButton>:
    background_color: 0,0,0,0
    color: self.color
    pos_hint: {'y':-0.01}
    font_size: sp(15)
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [20, 20, 0, 0]
            
<PeriodButton>:
    background_color: 0,0,0,0
    color: 0,0,0,1
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            size: self.size
            pos: (self.pos[0], self.pos[1]+10)
            radius: [0, 0, 20, 20] if self.is_last else [0, 0, 0, 0]
        
<InfoLabel>:
    text_size: root.width, None
    size: self.texture_size
    valign: 'top'
    halign: 'left'
    padding: 10

<InfoField>:
    color: 0, 0, 0, 1    # black color text
    orientation: 'vertical'
    size_hint: 1, 1
    padding: 5
    canvas.before:
        Color:
            rgba: self.stats_info_background_color 
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [30]
        Color:
            rgba: self.stats_info_outline_color
        Line:
            rounded_rectangle: (self.x+3, self.y+3, self.width-6, self.height-6, 30)

    AnchorLayout:
        anchor_x: 'left'
        anchor_y: 'top'
        InfoLabel:
            id: title_label
            color: self.color
            halign: root.title_halign
            font_size: root.title_sp

    AnchorLayout:
        anchor_x: 'center'
        anchor_y: 'top'
        InfoLabel:
            id: value_label
            color: self.color
            halign: 'center'
            font_size: root.value_sp

<CustomGridLayout>
    canvas:
        Color: 
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: (self.size[0], self.size[1])
        Color:
            rgba: self.bg_line_color
        Line:
            points: [self.x, self.y, self.x + self.width, self.y]
            width: 3
            cap: 'square'
            joint: 'miter'
            close: True
''')