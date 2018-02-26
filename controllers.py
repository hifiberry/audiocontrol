import threading
import logging
from typing import Dict
import nuimohelpers
import time

CONTROL_VOLUME_UP = 1
CONTROL_VOLUME_DOWN = 2
CONTROL_NEXT = 4
CONTROL_PREVIOUS = 8


class Controller():

    def __init__(self, params: Dict[str, str]):
        self.manager = None

    def set_manager(self, manager):
        self.manager = manager

    def terminate(self):
        pass


class Nuimo(Controller):

    import nuimo
    import nuimohelpers
    from nuimo import Gesture, LedMatrix

    class NuimoControllerListener(nuimo.ControllerListener):

        is_app_disconnection = False
        connection_failed = False

        def started_connecting(self):
            logging.info("Connecting to Nuimo controller ...")

        def connect_succeeded(self):
            self.connection_failed = False
            logging.info("Connected to Nuimo controller")
            print("SUCCEED")
            self.controller.display_matrix(nuimohelpers.MUSIC_NOTE)

        def connect_failed(self, error):
            self.connection_failed = True
            logging.info("Can't reconnect. Restarting nuimo_app")

        def disconnect_succeeded(self):
            logging.warn("Disconnected, reconnecting...")
            if not self.is_app_disconnection:
                self.controller.connect()

        def services_resolved(self):
            logging.info("Received services resolved to Nuimo controller")

        def received_gesture_event(self, event):
            print(event)
            logging.debug("Received gesture event to Nuimo controller")
            if event.gesture == Nuimo.Gesture.ROTATION:
                self.manager.change_volume_percent(event.value / 15)
            elif (event.gesture == Nuimo.Gesture.TOUCH_RIGHT) or \
                    (event.gesture == Nuimo.Gesture.SWIPE_RIGHT):
                self.manager.skip(1)
            elif (event.gesture == Nuimo.Gesture.TOUCH_LEFT) or \
                    (event.gesture == Nuimo.Gesture.SWIPE_LEFT):
                self.manager.skip(-1)

        def set_manager(self, manager):
            self.manager = manager

    def __init__(self, params: Dict[str, str]):
        import nuimo

        mac = params["mac"]

        self.manager = nuimo.ControllerManager(adapter_name='hci0')
        self.nuimocontroller = nuimo.Controller(manager=self.manager,
                                                mac_address=mac)
        self.nuimocontroller.listener = Nuimo.NuimoControllerListener()
        self.nuimocontroller.listener.controller = self.nuimocontroller
        self.nuimocontroller.connect()

        thread = threading.Thread(target=self.runloop, args=())
        thread.daemon = True
        thread.start()

    def runloop(self):
        try:
            self.manager.run()
        except KeyboardInterrupt:
            self.manager.quit()

    def terminate(self):
        # Terminate GATT event loop
        self.nuimocontroller.listener.stop()
        self.nuimocontroller.disconnect()
        self.manager.stop()

    def set_manager(self, manager):
        Controller.set_manager(self, manager)
        self.nuimocontroller.listener.set_manager(manager)


class Keyboard(Controller):

    def __init__(self, params: Dict[str, str]):
        self.codetable = {}
        print(params)
        for i in params:
            self.codetable[params[i]] = i

        import keyboard
        keyboard.hook(self.keyboard_hook)

        print(self.codetable)
        print("Keyboard listener started")

    def keyboard_hook(self, e):
        import keyboard
        if e.event_type == keyboard.KEY_DOWN:
            try:
                command = self.codetable[str(e.scan_code)]
            except:
                return

            if command == "volume_up":
                self.manager.change_volume_percent(5)
            elif command == "volume_down":
                self.manager.change_volume_percent(-5)
            elif command == "previous":
                self.manager.skip(-1)
            elif command == "next":
                self.manager.skip(1)

    def run(self):
        import keyboard
        keyboard.wait()
