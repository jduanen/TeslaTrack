'''
################################################################################
#
# TeslaTrack vehicle tracker
#
################################################################################
'''

import logging
import queue

from __init__ import * #### FIXME


class Tracker():
    ''' #### FIXME
    '''
    def __init__(self, vehicleName, inQ, outQ):
        self.name = vehicleName
        self.inQ = inQ
        self.outQ = outQ

    def run(self):
        while True:
            try:
                msg = self.inQ.get(True, None)
            except queue.Empty:
                continue
            if msg == CmdMsg.EXIT:
                break
            #### FIXME
            elif msg == "?":
                print("????")
            #### FIXME
            print(f"running {self.name}")
            sleep(10)
        self.outQ.put(CmdMsg.EXIT)
        logging.info(f"Tracker for '{self.name}': exiting")
