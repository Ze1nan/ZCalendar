from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from typing import Optional

class ScreenWidget(Screen):
    _instance: Optional["ScreenWidget"] = None

    def __new__(cls) -> "ScreenWidget":
        if cls._instance is None:
            cls._instance = super(ScreenWidget, cls).__new__(cls)
        return cls._instance
    
    def change_screen(self, screen_name: str, calendar_name: Optional[str] = None) -> None:
        self.size_hint = (1,1)
        self.size = Window.size
        
        new_screen = None
        if screen_name == 'calendar':
            from screens import CalendarScreen # pylint: disable=all
            new_screen = CalendarScreen(calendar_name=calendar_name)
        elif screen_name == 'statistics':
            from screens import StatisticsScreen # pylint: disable=all
            new_screen = StatisticsScreen(calendar_name=calendar_name)
        elif screen_name == 'usage':
            from screens import UsageScreen # pylint: disable=all
            new_screen = UsageScreen(calendar_name=calendar_name)
        elif screen_name == 'settings':
            from screens import SettingsScreen # pylint: disable=all
            new_screen = SettingsScreen(calendar_name=calendar_name)
    
        new_screen.pos = self.pos
        new_screen.size = self.size 
        
        self.clear_widgets()
        
        self.add_widget(new_screen)
        
    def update_statistics(self, calendar_name: str, period: str) -> None:
        from screens import StatisticsScreen # pylint: disable=all
        self.clear_widgets()
        self.add_widget(StatisticsScreen(calendar_name=calendar_name, graph_period=period, size=self.size))
        