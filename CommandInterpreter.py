'''
################################################################################
#
# TeslaTrack interactive command interpreter
#
################################################################################
'''

import json
from jsonpath_ng.ext import parse
import logging
import re
import sys

from __init__ import * #### FIXME


class CommandInterpreter():
    ''' #### FIXME
    '''
    def __init__(self, selectedVehicles, prompt="> "):
        self.vehicles = {v['display_name']: v for v in selectedVehicles}
        self.prompt = prompt
        self.numVehicles = len(self.vehicles)
        self.chosenVehicleNames = []
        self.running = True

    def _getChosenVehicleInfo(self, jsonPathExpression):
        try:
            for n in self.chosenVehicleNames:
                j = jsonPathExpression.find(self.vehicles[n].get_vehicle_data())[0].value
                print(f"'{n}':", end=" ")
                json.dump(j, sys.stdout, indent=4, sort_keys=True)
                print("")
        except IndexError:
            print(f"Error: invalid jsonPath expression -- '{jsonPathExpression}'")

    def run(self, cmdQueues):
        while self.running:
            line = input(self.prompt).strip()
            cmd = line.split(' ')[0]
            args = line[len(cmd) + 1:]
            if cmd == 'b':
                print("Vehicle Battery Levels:")
                for n in self.chosenVehicleNames:
                    print(f"    '{n}': \t{self.vehicles[n]['charge_state']['battery_level']} %")
            elif cmd == 'C':
                print(f"Currently chosen vehicles: {self.chosenVehicleNames}")
            elif cmd == 'c':
                if args:
                    #### FIXME handle unquoted names as well
                    #### FIXME make it work with both single and double quotes
                    names = re.findall(r'\"(.*?)\"', args)
                    if (len(names) < 1) or not set(names).issubset(set(self.vehicles.keys())):
                        print(f"Error: Invalid vehicle choice")
                    else:
                        self.chosenVehicleNames = [n for n in self.vehicles.keys() if n in names]
                else:
                    self.chosenVehicleNames = self.vehicles.keys()
                print(f"Currently chosen vehicles: {self.chosenVehicleNames}")
            elif cmd == 'd':
                print(f"Chosen Vehicle Drive State:")
                self._getChosenVehicleInfo(parse("$['drive_state']"))
            elif cmd == 'i':
                print(f"Chosen Vehicle Information:")
                self._getChosenVehicleInfo(parse(args))
            elif cmd == 'n':
                print(f"Number of Selected Vehicles: {self.numVehicles}")
            elif cmd == 'q':
                for qName, q in cmdQueues.items():
                    logging.info("Shutting down {qName}")
                    q.put(CmdMsg.EXIT)
                break
            elif cmd == 'w':
                for n in self.chosenVehicleNames:
                    print(f"Waking up: {n}...", end=" ")
                    self.vehicles[n].sync_wake_up()
                    print(f"Vehicle {n} awake")
            elif cmd == 'x':
                #### TODO background the program
                break
            elif cmd == '?' or cmd == 'h':
                print("Help:")
                print("    h: print this help message")
                print("    b: print the battery level for the currently chosen vehicles")
                print("    C: print the currently chosen vehicle names")
                print("    c {<name>}*: choose the vehicle(s) to operate on (or all if no arg is given)")
                print("    d: print drive state for the currently chosen vehicle(s)")
                print("    i <jsonPath>: print given info for the currently chosen vehicle(s)")
                print("    n: print number of selected vehicles")
                print("    q: quit and shut down trackers")
                print("    w: wake up the currently chosen vehicle(s)")
                print("    x: quit command interpeter")
                print("    ?: print this help message")
        print("Exiting...")
        logging.info("CommandInterpreter: exiting")

    def terminate(self):
        self.running = False
