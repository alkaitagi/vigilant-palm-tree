import mouse
from rx import Observable
from rx.subject import Subject

from modulebase import ModuleBase


class MouseToFileOutputModule(ModuleBase):
    def __init__(self, mouse_source: ModuleBase):
        self.file = open('mouse_output.txt', 'w+')
        mouse_source.get_data_stream().subscribe(self.process_mouse)

    def process_mouse(self, event):
        if isinstance(event, mouse.ButtonEvent):
            self.file.write('button %s %s %s\n' % (event.button, event.event_type, event.time))
        elif isinstance(event, mouse.WheelEvent):
            self.file.write('wheel %s %s\n' % (event.delta, event.time))
        elif isinstance(event, mouse.MoveEvent):
            self.file.write('move %s %s %s\n' % (event.x, event.y, event.time))
        self.file.flush()

    def get_data_stream(self) -> Observable:
        return Subject()

    def start(self):
        pass

    def stop(self):
        pass
