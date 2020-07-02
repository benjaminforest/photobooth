import hid

import logging
from .. import StateMachine
from ..Threading import Workers

vid = 0x1130	# Change it for your device
pid = 0xcc00	# Change it for your device


class Hid:

    def __init__(self, config, comm):
        super().__init__()

        self._is_trigger = False
        self._is_enabled = True

        self._comm = comm
        self._h = hid.Device(vid, pid)


        #hid_loop = threading.Thread(target = background)
        #hid_loop.start()


    def handleState(self, state):

        logging.info(f"##### {state}")

        if isinstance(state, StateMachine.IdleState):
            self.showIdle()
        elif isinstance(state, StateMachine.GreeterState):
            self.disableTrigger()
        elif isinstance(state, StateMachine.PostprocessState):
            self.showPostprocessState()


    def background(self, event):

        while self._comm.empty(Workers.HID):
            data = self._h.read(16, timeout=1)
            if len(data) and data[1] != 0:
                self.trigger(event)


    def showPostprocessState(self):

        self.enableTrigger()

        if self._is_enabled:
            self.background(StateMachine.GpioEvent('idle'))


    def showIdle(self):

        self.enableTrigger()

        if self._is_enabled:
            self.background(StateMachine.GpioEvent('trigger'))


    def run(self):

        for state in self._comm.iter(Workers.HID):
            self.handleState(state)

        return True


    def disableTrigger(self):

       if self._is_enabled:
           self._is_trigger = False


    def enableTrigger(self):

        if self._is_enabled:
            self._is_trigger = True


    def trigger(self, event):
        if self._is_trigger:
            self.disableTrigger()
            self._comm.send(Workers.MASTER, event )


