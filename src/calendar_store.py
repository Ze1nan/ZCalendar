from typing import List, Optional, Union
from types import TracebackType
from datetime import datetime
import sqlite3

from app_config import Config

class Check:
    def __init__(self, date: str, multiplier: int, short_note: str, long_note: str) -> None:
        self.date: str = date
        self.multiplier: int = multiplier
        self.short_note: str = short_note
        self.long_note: str = long_note
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(date=\"{self.date}\", multiplier={self.multiplier}, short_note=\"{self.short_note}\", long_note=\"{self.long_note}\")"

class CalendarStore:
    _instance: Optional["CalendarStore"] = None
    
    def __new__(cls, *args, **kwargs) -> "CalendarStore":
        if not cls._instance:
            cls._instance = super(CalendarStore, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        self.db_name: str = Config().checks_data_store_path
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.default_table: Optional[str] = None

    def __enter__(self) -> "CalendarStore":
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> None:
        self.connection.close()

    def select_calendar(self, table: str) -> None:
        self.default_table = table

    def date_exists(self, date: str, table: Optional[str] = None) -> bool:
        table = table or self.default_table
        if table is None:
            raise ValueError("Default table is not set. Use select_calendar() to set it.")
        self.cursor.execute(f'SELECT 1 FROM "{table}" WHERE date = ?', (date,))
        return self.cursor.fetchone() is not None

    def get(self, date: str, table: Optional[str] = None) -> Optional[Check]:
        table = table or self.default_table
        if table is None:
            raise ValueError("Default table is not set. Use select_calendar() to set it.")
        self.cursor.execute(f'SELECT * FROM "{table}" WHERE date = ?', (date,))
        row = self.cursor.fetchone()
        if row:
            return Check(*row)
        return None
        
    def get_data(self, table: Optional[str] = None) -> List[Check]:
        table = table or self.default_table
        if table is None:
            raise ValueError("Default table is not set. Use select_calendar() to set it.")
        self.cursor.execute(f'SELECT * FROM "{table}"')
        rows = self.cursor.fetchall()
        return sorted([Check(*row) for row in rows], key=lambda x: datetime.strptime(x.date, "%d-%m-%Y"))

    def get_calendars(self) -> List[str]:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in self.cursor.fetchall()] 

    def update(self, date: str, multiplier: Optional[int] = None, short_note: Optional[str] = None, long_note: Optional[str] = None, table: Optional[str] = None) -> None:
        table = table or self.default_table
        if table is None:
            raise ValueError("Default table is not set. Use select_calendar() to set it.")
        updates: List[str] = []
        params: List[Union[int, str]] = []
        if multiplier is not None:
            updates.append("multiplier = ?")
            params.append(multiplier)
        if short_note is not None:
            updates.append("short_note = ?")
            params.append(short_note)
        if long_note is not None:
            updates.append("long_note = ?")
            params.append(long_note)
        if updates:
            query = f'''UPDATE "{table}"
                         SET {', '.join(updates)}
                         WHERE date = ?'''
            params.append(date)
            self.cursor.execute(query, params)
            self.connection.commit()

    def increment(self, date: str, table: Optional[str] = None) -> None:
        table = table or self.default_table
        if table is None:
            raise ValueError("Default table is not set. Use select_calendar() to set it.")
        self.cursor.execute(f'''UPDATE "{table}"
                                 SET multiplier = multiplier + 1
                                 WHERE date = ?''', (date,))
        self.connection.commit()

    def put(self, date: str, multiplier: int = 0, short_note: str = '', long_note: str = '', table: Optional[str] = None) -> None:
        table = table or self.default_table
        if table is None:
            raise ValueError("Default table is not set. Use select_calendar() to set it.")
            
        if multiplier == 0 and short_note == "" and long_note == "":
            self.delete(date)
            return
        self.cursor.execute(f'''INSERT INTO "{table}" (date, multiplier, short_note, long_note)
                                 VALUES (?, ?, ?, ?)''', (date.strip('0'), multiplier, short_note, long_note))
        self.connection.commit()

    def delete(self, date: str, table: Optional[str] = None) -> None:
        table = table or self.default_table
        if table is None:
            raise ValueError("Default table is not set. Use select_calendar() to set it.")
        self.cursor.execute(f'DELETE FROM "{table}" WHERE date = ?', (date,))
        self.connection.commit()

    def create_calendar(self, name: str) -> bool:    
        if name in self.get_calendars():
            return False
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS "{name}" (
                                     date TEXT PRIMARY KEY,
                                     multiplier INTEGER,
                                     short_note TEXT,
                                     long_note TEXT)''')
        self.connection.commit()
        return True 
        
    def rename_calendar(self, new_name: str, table: Optional[str] = None) -> None:
        table = table or self.default_table
        if table is None:
            raise ValueError("Default table is not set. Use select_calendar() to set it.")
        self.default_table = new_name
        self.cursor.execute(f'ALTER TABLE "{table}" RENAME TO "{new_name}"')
        self.connection.commit()

    def reset_calendar(self, table: Optional[str] = None) -> None:
        table = table or self.default_table
        if table is None:
            raise ValueError("Default table is not set. Use select_calendar() to set it.")
        self.cursor.execute(f'DELETE FROM "{table}"')
        self.connection.commit()

    def delete_calendar(self, table: Optional[str] = None) -> None:
        table = table or self.default_table
        if table is None:
            raise ValueError("Default table is not set. Use select_calendar() to set it.")
        self.cursor.execute(f'DROP TABLE IF EXISTS "{table}"')
        self.connection.commit()

    def calendar_exists(self, t: str) -> bool:
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{t}'")
        return self.cursor.fetchone() is not None

    def delete_all(self) -> None:
        tables = self.get_calendars()
        for table in tables:
            self.cursor.execute(f'DROP TABLE IF EXISTS {table}')
        self.connection.commit()
