from kivy.storage.dictstore import DictStore
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union, Any
import os

from config_data import languages, themes, easters

if not os.path.exists("../storage"):
    os.makedirs("../storage")

class Config:
    _instance: Optional["Config"] = None
        
    def __new__(cls, *args, **kwargs) -> "Config":
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        self.opened_date = list(map(int, f'{datetime.now():%Y-%m-%d}'.split('-')))
        self.config_store_path = "../storage/config_data.zein"
        self.checks_data_store_path = "../storage/checks_data.db"
        self.current_lang = None
        self.current_theme = None
        self.roman_numerals = None
        self.current_girl = None
        self.multiplier = None
        self.easters = None

        self.load_data()

    def load_data(self) -> None:
        store = DictStore(self.config_store_path)
        if 'config' not in store:
            store.put('config', current_lang='ru', current_theme='basic', roman_numerals=False, girl=False, multiplier=1)
        if 'easters' not in store:
            store.put('easters', **{easter: False for easter in easters})
        
        config = store.get('config')
        
        self.current_lang = languages[config['current_lang']]
        self.current_theme = themes[config['current_theme']]
        self.roman_numerals = config['roman_numerals']
        self.current_girl = config['girl']
        self.multiplier = config['multiplier']
        self.easters = store.get('easters')
    
    def update(self, space: str, key: str, value: Any) -> None:
        store = DictStore(self.config_store_path)
        if not store.get(space):
            return
        
        store = DictStore(self.config_store_path)
        store.get(space)[key] = value
        store.put(space, **store.get(space))

        self.load_data()

    def get_language(self, code: str) -> Dict[str, Union[int, str, Tuple[Union[int, str]]]]:
        return languages[code]
    
    def get_theme(self, name: str) -> Dict[str, Union[int, str, Tuple[Union[int, str]]]]:
        return themes[name]
    
    def get_languages_list(self) -> List[str]:
        return list(languages.keys())
    
    def get_themes_list(self) -> List[str]:
        return list(themes.keys())
    
    def get_easters(self) -> Dict[str, bool]:
        return easters