from typing import Dict
from math import ceil
import logging
import threading

from audiocontrol.controllers import Controller

# Nuimo matrices from
# https://github.com/getsenic/senic-hub/blob/master/senic_hub/nuimo_app/matrices.py

LIGHT_OFF = \
    "         " \
    "         " \
    "         " \
    "    *    " \
    "   ***   " \
    "    *    " \
    "         " \
    "         " \
    "         "

LIGHT_ON = \
    "    *    " \
    " *     * " \
    "         " \
    "    *    " \
    "*  ***  *" \
    "    *    " \
    "         " \
    " *     * " \
    "    *    "

LIGHT_BULB = \
    "   ***   "  \
    "  *   *  "  \
    "  *   *  "  \
    "  * * *  "  \
    "  * * *  "  \
    "  * * *  "  \
    "   ***   "  \
    "   ***   "  \
    "         "

PAUSE = \
    "         " \
    "  ## ##  " \
    "  ## ##  " \
    "  ## ##  " \
    "  ## ##  " \
    "  ## ##  " \
    "  ## ##  " \
    "  ## ##  " \
    "         "

PLAY = \
    "         " \
    "   #     " \
    "   ##    " \
    "   ###   " \
    "   ####  " \
    "   ###   " \
    "   ##    " \
    "   #     " \
    "         "

MUSIC_NOTE = \
    "  #####  " \
    "  #####  " \
    "  #   #  " \
    "  #   #  " \
    "  #   #  " \
    " ##  ##  " \
    "### ###  " \
    " #   #   " \
    "         "

SHUFFLE = \
    "         " \
    "         " \
    " ##   ## " \
    "   # #   " \
    "    #    " \
    "   # #   " \
    " ##   ## " \
    "         " \
    "         "

ERROR = \
    "         " \
    "         " \
    "  *   *  " \
    "   * *   " \
    "    *    " \
    "   * *   " \
    "  *   *  " \
    "         " \
    "         "

NEXT_SONG = \
    "         " \
    "         " \
    "   #  #  " \
    "   ## #  " \
    "   ####  " \
    "   ## #  " \
    "   #  #  " \
    "         " \
    "         "

PREVIOUS_SONG = \
    "         " \
    "         " \
    "  #  #   " \
    "  # ##   " \
    "  ####   " \
    "  # ##   " \
    "  #  #   " \
    "         " \
    "         "

POWER_OFF = \
    "         " \
    "         " \
    "   ###   " \
    "  #   #  " \
    "  #   #  " \
    "  #   #  " \
    "   ###   " \
    "         " \
    "         "


LETTER_W = \
    "         " \
    " #     # " \
    " #     # " \
    " #     # " \
    " #     # " \
    " #  #  # " \
    " #  #  # " \
    "  ## ##  " \
    "         "

STATION1 = \
    "         " \
    "     *   " \
    "    **   " \
    "   * *   " \
    "     *   " \
    "     *   " \
    "     *   " \
    "     *   " \
    "         "

STATION2 = \
    "         " \
    "   ***   " \
    "      *  " \
    "      *  " \
    "   ***   " \
    "  *      " \
    "  *      " \
    "   ***   " \
    "         "

STATION3 = \
    "         " \
    "   ***   " \
    "      *  " \
    "      *  " \
    "    **   " \
    "      *  " \
    "      *  " \
    "   ***   " \
    "         "


def progress_bar(progress):
    """
    Generates a light bar matrix to display volume / brightness level.
    :param progress: value between 0..1
    """
    dots = list(" " * 81)
    num_dots = ceil(round(progress, 3) * 9)
    while num_dots > 0:
        dots[81 - ((num_dots - 1) * 9 + 5)] = "*"
        num_dots -= 1

    return "".join(dots)


def matrix_with_index(matrix, index):
    """
    Adds index of the component in the component list to the top right
    corner of the component matrix.
    """
    dots = list(matrix)

    while index >= 0:
        dots[index * 9 + 8] = '*'
        index -= 1

    return "".join(dots)


class Nuimo(Controller):

    import nuimo
    from nuimo import Gesture, LedMatrix

    class NuimoControllerListener(nuimo.ControllerListener):

        is_app_disconnection = False
        connection_failed = False

        def started_connecting(self):
            logging.debug("Connecting to Nuimo controller ...")

        def connect_succeeded(self):
            self.connection_failed = False
            logging.info("Connected to Nuimo controller")
#            self.controller.display_matrix(MUSIC_NOTE)

        def connect_failed(self, error):
            self.connection_failed = True
            logging.error("Can't connect to Nuimo")

        def disconnect_succeeded(self):
            logging.warn("Disconnected, reconnecting...")
            if not self.is_app_disconnection:
                self.controller.connect()

        def services_resolved(self):
            logging.info("Received services resolved to Nuimo controller")

        def received_gesture_event(self, event):
            logging.debug("Received gesture event to Nuimo controller %s",
                          event)
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

        mac = params.get("mac")
        if mac is None:
            logging.error("mac parameter for Nuimo undefined, aborting")
            return

        adaptername = params.get("adapter_name", "hci1")
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
