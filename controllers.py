import threading
import logging
import time
from typing import Dict


import nuimohelpers

CONTROL_VOLUME_UP = 1
CONTROL_VOLUME_DOWN = 2
CONTROL_NEXT = 4
CONTROL_PREVIOUS = 8


class Controller():

    def __init__(self, params: Dict[str, str]):
        self.manager = None
        self.term_received = False

    def set_manager(self, manager):
        self.manager = manager

    def volume_changed(self):
        '''
        Notifies a control that the playback volume has been changed.
        In most cases, this can be ignored, but it can be useful e.g. 
        to display the volume.
        '''
        pass

    def terminate(self):
        self.term_received = True

    def __str__(self):
        return self.service


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

        self.service = "NUIMO"

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
        self.service = "KEYBOARD"
        self.codetable = {}
        for i in params:
            self.codetable[params[i]] = i

        import keyboard
        keyboard.hook(self.keyboard_hook)
        logging.debug("Keyboard listener started")

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


class AlsaVolume(Controller):

    def __init__(self, params: Dict[str, str]):
        import alsaaudio

        self.manager = None
        self.service = "ALSAVOLUME"
        self.term_received = False
        self.volume = 0
        try:
            self.mixername = params["control"]
        except Exception as e:
            logging.error(e)
            return

        thread = threading.Thread(target=self.run_listener, args=())
        thread.daemon = True
        thread.start()

    def volume_changed(self):
        import alsaaudio

        vol = self.manager.volume_percent
        if vol != self.volume:
            alsaaudio.Mixer(self.mixername).setvolume(vol, MIXER_CHANNEL_ALL)

    def run_listener(self):
        while (self.manager is None) and not (self.term_received):
            time.sleep(1)

        while not(self.term_received):
            self.update_volume()
            time.sleep(0.3)

    def update_volume(self):
        import alsaaudio

        volumes = alsaaudio.Mixer(self.mixername).getvolume()
        channels = 0
        vol = 0
        for i in range(len(volumes)):
            channels += 1
            vol += volumes[i]

        if channels > 0:
            vol = vol / channels

        if vol != self.volume:
            logging.debug("ALSA volume changed to {}".format(vol))
            self.volume = vol
            self.manager.set_volume_percent(vol)
