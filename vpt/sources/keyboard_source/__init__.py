'''Registers keyboard events to a data stream.'''
import keyboard
from rx import Observable
from rx.subject import Subject

from vpt.sources.base import SourceBase


class KeyboardSource(SourceBase[keyboard.KeyboardEvent]):
    '''A source node for keyboard events.'''
    subj = Subject()

    def start(self):
        keyboard.hook(self.callback)

    def stop(self):
        keyboard.unhook_all()

    def callback(self, event: keyboard.KeyboardEvent):
        '''Sends the event to the stream.'''
        self.subj.on_next(event)

    def get_data_stream(self) -> Observable:
        return self.subj
