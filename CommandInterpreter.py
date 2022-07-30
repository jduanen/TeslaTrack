'''
################################################################################
#
# TeslaTrack interactive command interpreter
#
################################################################################
'''

import logging

from __init__ import * #### FIXME


class CommandInterpreter():
    ''' #### FIXME
    '''
    def __init__(self, prompt="> "):
        self.prompt = prompt
        self.cmd = ""
        self.running = True

    def run(self, cmdQueues):
        while self.running:
            line = input(self.prompt)
            words = line.split(' ')
            cmd = words[0].lower().strip()
            args = words[1:]
            if cmd == 'a':
                print(f"AAAA")
            elif cmd == 'b':
                pass
            elif cmd == 'q':
                break
            elif cmd == 'x':
                for qName, q in cmdQueues.items():
                    logging.info("Shutting down {qName}")
                    q.put(CmdMsg.EXIT)
                break
            elif cmd == '?' or cmd == 'h':
                print("Help:")
                print("    h: print this help message")
                print("    q: quit command interpeter")
                print("    x: quit and shut down trackers")
                print("    ?: print this help message")
        print("Exiting...")
        logging.info("CommandInterpreter: exiting")

    def terminate(self):
        self.running = False
