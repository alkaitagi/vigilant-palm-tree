'''The SQLite store is responsible for writing streams to an SQLite database.'''
import sqlite3
import time
from typing import Union

import keyboard
import mouse

from vpt.sinks.base import SinkBase
from vpt.sources.base import SourceBase


class SQLiteStore(SinkBase):
    '''Persistently store the engagement level and keyboard/mouse events
       in an SQLite database.'''
    connection: sqlite3.Connection

    def __init__(self, db_path: str, mouse_source: SourceBase,
                 keyboard_source: SourceBase, engagement_source: SourceBase):
        '''Create a database or open an existing one.'''
        self.connection = sqlite3.connect(db_path)
        cur = self.connection.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS engagement (
                code integer NOT NULL,
                timestamp integer NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS keystrokes (
                type text NOT NULL,
                scancode integer NOT NULL,
                modifiers text NOT NULL,
                timestamp integer NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS mouse_events (
                type text NOT NULL,
                x integer,
                y integer,
                wheel_delta integer,
                button text,
                timestamp integer NOT NULL
            )
        ''')
        self.connection.commit()
        cur.close()

        mouse_source.get_data_stream().subscribe(self.store_mouse_event)
        keyboard_source.get_data_stream().subscribe(self.store_key_event)
        engagement_source.get_data_stream().subscribe(self.store_engagement)

    def __del__(self):
        '''Clean up resources.'''
        self.connection.commit()
        self.connection.close()

    def store_engagement(self, code: int):
        '''Store an instance of engagement.'''
        cur = self.connection.cursor()
        cur.execute('''
            INSERT INTO engagement VALUES (?, ?)
        ''', (code, int(time.time())))
        self.connection.commit()
        cur.close()

    def store_key_event(self, event: keyboard.KeyboardEvent):
        '''Store a keypress with all of its modifiers.'''
        cur = self.connection.cursor()
        cur.execute('''
            INSERT INTO keystrokes VALUES (?, ?, ?, ?)
        ''', (event.event_type, event.scan_code, ','.join(event.modifiers), int(event.time)))
        self.connection.commit()
        cur.close()

    def store_mouse_event(self, event: Union[mouse.MoveEvent, mouse.WheelEvent, mouse.ButtonEvent]):
        '''Store mouse movements, button presses and scrolls.'''
        cur = self.connection.cursor()
        if isinstance(event, mouse.MoveEvent):
            cur.execute('''
                INSERT INTO mouse_events VALUES (?, ?, ?, NULL, NULL, ?)
            ''', ('move', event.x, event.y, int(event.time)))
        elif isinstance(event, mouse.WheelEvent):
            cur.execute('''
                INSERT INTO mouse_events VALUES (?, NULL, NULL, ?, NULL ?)
            ''', ('wheel', event.delta, int(event.time)))
        else:
            cur.execute('''
                INSERT INTO mouse_events VALUES (?, NULL, NULL, NULL, ?, ?)
            ''', ('button', f'{event.button}:{event.event_type}', int(event.time)))
        self.connection.commit()
        cur.close()
